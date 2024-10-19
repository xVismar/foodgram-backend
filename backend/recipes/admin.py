from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from api.filters import CookingTimeFilter

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Subscription,
    Tag, User, RecipeTag
)


def format_tags(func):

    def wrapper(self, recipe):
        tags = func(self, recipe)
        return format_html('<br>'.join(tags))
    return wrapper


def set_short_description(description):
    def decorator(func):
        func.short_description = description
        return func
    return decorator


def allow_tags(func):
    func.allow_tags = True
    return func


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0

    def ingredient_info(self, recipeingredient):
        ingredient = Ingredient.objects.get(id=recipeingredient.ingredient_id)
        return f'{ingredient.name} ({ingredient.measurement_unit})'

    readonly_fields = ["ingredient_info"]


class TagInline(admin.TabularInline):
    model = RecipeTag
    extra = 0


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count',
        'get_tags',
        'image',
        'cooking_time'
    )
    search_fields = [
        'author__username',
        'name',
        'tags'
    ]
    autocomplete_fields = ['author']
    list_filter = [
        'tags',
        'author',
        CookingTimeFilter,
    ]
    inlines = [RecipeIngredientInline, TagInline, FavoriteInline]
    fieldsets = (
        (None, {'fields': ('name', 'author', )}),
        ('Описание', {'fields': ('text', 'cooking_time', 'image')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'name',
                    'author',
                    'tags',
                    'text',
                    'cooking_time',
                    'ingredients',
                    'image',
                ),
            },
        ),
    )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    @set_short_description('В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.all().count()

    @allow_tags
    @set_short_description('Теги')
    @format_tags
    def get_tags(self, recipe):
        return recipe.tags.values_list('name', flat=True).order_by('name')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = [
        'name',
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = [
        'name',
        'slug',
    ]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'is_active',
        'is_staff',
        'is_superuser',
        'number_of_recipes',
        'number_of_subscriptions',
        'number_of_subscribers',
        'avatar'
    )
    search_fields = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name',
                                                'avatar')}),
        (
            'Подписки и рецепты',
            {'fields': ('get_subscriptions', 'get_recipes',
                        'get_favorited_recipes')},
        ),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                ),
            },
        ),
    )
    ordering = ('username',)
    readonly_fields = ('get_subscriptions', 'get_recipes',
                       'get_favorited_recipes')

    @set_short_description('Подписки')
    def get_subscriptions(self, user):
        custom_user_ct = ContentType.objects.get_for_model(User)
        app_label = custom_user_ct.app_label
        model_name = custom_user_ct.model
        subscriptions = user.authors.all()
        if subscriptions.exists():
            return mark_safe(
                '<br>'.join([
                    f'''<a href='{
                    reverse(f'admin:{app_label}_{model_name}_change',
                            args=[sub.author.id])
                    }'>'''
                    f'{sub.author.username}</a>'
                    for sub in subscriptions
                ])
            )
        return 'Нет подписок'

    @set_short_description('Рецепты')
    def get_recipes(self, user):
        recipe_ct = ContentType.objects.get_for_model(Recipe)
        app_label = recipe_ct.app_label
        model_name = recipe_ct.model
        recipes = user.recipes.all()
        if recipes.exists():
            return mark_safe(
                '<br>'.join([
                    f'''<a href='{
                    reverse(f'admin:{app_label}_{model_name}_change',
                            args=[recipe.id])
                    }'>'''
                    f'{recipe.name}</a>'
                    for recipe in recipes
                ])
            )
        return 'Нет рецептов'

    @set_short_description('Избранные рецепты')
    def get_favorited_recipes(self, user):
        recipe_ct = ContentType.objects.get_for_model(Favorite)
        app_label = recipe_ct.app_label
        model_name = recipe_ct.model
        favorited_recipes = user.favorites.all()
        if favorited_recipes.exists():
            return mark_safe(
                '<br>'.join([
                    f'''<a href='{
                    reverse(f'admin:{app_label}_{model_name}_change',
                            args=[favorited_recipe.id])
                    }'>'''
                    f'{favorited_recipe.recipe.name}</a>'
                    for favorited_recipe in favorited_recipes
                ])
            )
        return 'Нет избранных рецептов'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
