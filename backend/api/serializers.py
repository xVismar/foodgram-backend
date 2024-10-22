from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag, User
)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CurentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'is_subscribed', 'avatar')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=author
            ).exists()
        )

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        if avatar:
            instance.avatar.save(avatar.name, avatar, save=False)
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
    image = Base64ImageField()

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

    def validate_fields(self, field_data, field_name, model):
        if not field_data:
            raise serializers.ValidationError(
                f'Нельзя создать рецепт без {field_name}.'
            )
        field_ids = {
            field['id'] if isinstance(field, dict) else field.id
            for field in field_data
        }
        if len(field_ids) != len(field_data):
            raise serializers.ValidationError(
                f'{field_name} не могут повторяться.'
            )
        non_existent_ids = (
            field_ids - {obj.id for obj in model.objects.filter(
                id__in=field_ids
            )}
        )
        if non_existent_ids:
            raise serializers.ValidationError(
                f'Таких {field_name} не существует: '
                f'{", ".join(map(str, non_existent_ids))}.'
            )
        return field_data

    def validate_ingredients(self, field_data):
        return self.validate_fields(field_data, 'ингредиентов', Ingredient)

    def validate_tags(self, field_data):
        return self.validate_fields(field_data, 'тегов', Tag)

    def recipe_ingredients_create(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredients')
        tags_data = validated_data.pop('tags')
        validated_data = super().create(validated_data)
        self.recipe_ingredients_create(validated_data, ingredients_data)
        validated_data.tags.set(tags_data)
        return validated_data

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

    def check_relation(self, user, recipe, model):
        request = self.context.get('request')
        return (
            (request and request.user.is_authenticated)
            and model.objects.filter(user=request.user, recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        return (
            self.check_relation(
                self.context.get('request').user, recipe, Favorite
            )
        )

    def get_is_in_shopping_cart(self, recipe):
        return (
            self.check_relation(
                self.context.get('request').user, recipe, ShoppingCart
            )
        )


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
