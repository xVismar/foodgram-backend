from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe

from users.models import User, UserSubscription


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class TagInline(admin.TabularInline):
    model = Tag
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count',
        'get_tags',
    )
    search_fields = [
        'author__username',
        'name',
    ]
    list_filter = [
        'tags',
    ]
    inlines = [RecipeIngredientInline]
    fieldsets = (
        (None, {'fields': ('name', 'author', 'tags')}),
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

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def get_tags(self, obj):
        return ', '.join(
            obj.tags.values_list('name', flat=True).order_by('name'))

    favorite_count.short_description = 'В избранном'
    get_tags.short_description = 'Теги'


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
        'is_superuser')
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

    def get_subscriptions(self, obj):
        custom_user_ct = ContentType.objects.get_for_model(User)
        app_label = custom_user_ct.app_label
        model_name = custom_user_ct.model

        subscriptions = UserSubscription.objects.filter(user=obj)
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

    get_subscriptions.short_description = 'Подписки'
    get_subscriptions.admin_order_field = 'author__username'
    get_subscriptions.description = 'Показывает подписки пользователя'

    def get_recipes(self, obj):
        recipe_ct = ContentType.objects.get_for_model(Recipe)
        app_label = recipe_ct.app_label
        model_name = recipe_ct.model

        recipes = Recipe.objects.filter(author=obj)
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

    def get_favorited_recipes(self, obj):
        recipe_ct = ContentType.objects.get_for_model(Favorite)
        app_label = recipe_ct.app_label
        model_name = recipe_ct.model

        favorited_recipes = Favorite.objects.filter(user=obj)
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

    get_subscriptions.short_description = 'Подписки'
    get_recipes.short_description = 'Рецепты'
    get_favorited_recipes.short_description = 'Избранные рецепты'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
