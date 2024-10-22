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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            representation['avatar'] = request.build_absolute_uri(
                instance.avatar.url
            )
        return representation


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

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов.'
            )
        ingredients = set()
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться.')
            ingredients.add(ingredient_id)
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    'Такого ингредиента не существует.'
                )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нелья создать рецепт без добавления хотя бы однго тега.'
            )
        tags = set()
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    'Теги не могут повторяться.')
            tags.add(tag)
        return value

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
