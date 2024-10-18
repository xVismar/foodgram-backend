from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.services import get_data_set, RecipeMiniSerializer
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
    avatar = Base64ImageField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=author
            ).exists()
        return False

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
        source='recipeingredient_set'
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

    def validate_ingredients(self, ingredients_data):
        if not ingredients_data:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без продуктов.'
            )
        ingredients_id_set = get_data_set(ingredients_data)
        for id in ingredients_id_set:
            if not Ingredient.objects.filter(id=id).exists():
                raise serializers.ValidationError(
                    'Такого продукта не существует.'
                )
        return ingredients_data

    def validate_tags(self, tags_data):
        if not tags_data:
            raise serializers.ValidationError(
                'Нелья создать рецепт без добавления хотя бы однго тэга.'
            )
        tags_id_set = get_data_set(tags_data)
        for id in tags_id_set:
            if not Tag.objects.filter(id=id).exists():
                raise serializers.ValidationError(
                    'Такого тэга не существует.'
                )
        return tags_data

    def recipe_ingredients_create(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_data['ingredient']['id'],
                    amount=ingredient_data['amount']
                )
                for ingredient_data in ingredients_data
            ]
        )

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

    def check_relation(self, user, recipe, model):
        request = self.context.get('request')
        return (
            model.objects.filter(user=request.user, recipe=recipe).exists() if
            request and request.user.is_authenticated
            else False
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


class SubscriptionSerializer(CurentUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CurentUserSerializer.Meta):
        fields = (
            'recipes_count', 'recipes'
        )

    def get_recipes(self, user):
        return RecipeMiniSerializer(
            user.recipes.all()[:float('inf')], many=True
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()
