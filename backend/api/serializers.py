from django.db import transaction
from rest_framework import serializers, validators

from api.fields import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.serializers import CustomUserSerializer, RecipeMiniSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    author = CustomUserSerializer(read_only=True)
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
        ingredients_data = validated_data.pop('recipeingredient_set')
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
        ingredients_data = validated_data.pop('recipeingredient_set', None)
        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)
        instance = super().update(instance, validated_data)
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            self.recipe_ingredients_create(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        return {
            **super().to_representation(instance),
            'tags': TagSerializer(instance.tags.all(), many=True).data
        }

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            Favorite.objects.filter(user=request.user, recipe=obj).exists() if
            request and request.user.is_authenticated
            else False
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
            if request and request.user.is_authenticated
            else False
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = (validators.UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe'),
            message=('Этот рецепт уже есть в списке покупок')
        ),
        )

    def to_representation(self, instance):
        return RecipeMiniSerializer().to_representation(
            Recipe.objects.get(id=instance.recipe.id)
        )
