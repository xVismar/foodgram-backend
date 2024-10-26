
import base64
from collections import Counter

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag, User
)


class Base64Image(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CurentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64Image()

    class Meta(UserSerializer.Meta):
        abstract = True
        model = User
        fields = (
            *UserSerializer.meta.fields, 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=author
            ).exists()
        return False

    def validate(self, attrs):
        request = self.context.get('request')
        if request and 'avatar' not in attrs or attrs.get('avatar') is None:
            raise serializers.ValidationError('Отсутствует поле "avatar"')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar', None)
        if avatar:
            if instance.avatar:
                instance.avatar.delete()
            instance.avatar = avatar
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    author = CurentUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipeingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64Image()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def related_field_validate(
        self, model_data, field_name, model, validation_message
    ):
        if not model_data:
            raise ValidationError(validation_message)
        id_set = set(
            item.id if model == Tag or isinstance(item, Tag)
            else item['ingredient']['id'] for item in model_data
        )
        not_found = [
            id for id in id_set if not model.objects.filter(id=id).exists()
        ]
        duplicates = [id for id, count in Counter(id_set).items() if count > 1]
        errors = []
        if not_found:
            errors.append(f'{field_name}s с ID {not_found} не найдены.')
        if duplicates:
            errors.append(
                f'Обнаружены дублированные {field_name}s с ID: {duplicates}.'
            )
        if errors:
            raise ValidationError(errors)
        return model_data

    def validate_ingredients(self, ingredients_data):
        return self.related_field_validate(
            ingredients_data,
            'ingredients',
            Ingredient,
            'Нельзя создать рецепт без продуктов.'
        )

    def validate_tags(self, tags_data):
        return self.related_field_validate(
            tags_data,
            'tags',
            Tag,
            'Нельзя создать рецепт без хотя бы одного тэга.'
        )

    def recipe_ingredients_create(self, recipe, ingredients_data):
        recipe_ingredients_to_create = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount'])
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients_to_create)

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredients')
        tags_data = validated_data.pop('tags')
        image_data = validated_data.pop('image')
        recipe = Recipe.objects.create(**validated_data)
        recipe.image.save(image_data.name, image_data, save=True)
        self.recipe_ingredients_create(recipe, ingredients_data)
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('recipeingredients', None)
        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)
        instance.tags.set(tags_data)
        instance.recipeingredients.all().delete()
        self.recipe_ingredients_create(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return {
            **super().to_representation(instance),
            'tags': TagSerializer(instance.tags.all(), many=True).data
        }

    def check_relation(self, recipe, model):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and model.objects.filter(user=request.user, recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        return self.check_relation(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_relation(recipe, ShoppingCart)


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CurentUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CurentUserSerializer.Meta):
        fields = (
            *CurentUserSerializer.Meta.fields, 'recipes_count', 'recipes'
        )

    def get_recipes(self, user):
        return RecipeMiniSerializer(
            user.recipes.all()[
                :self.context.get('recipes_limit', 10**10)
            ],
            many=True
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()
