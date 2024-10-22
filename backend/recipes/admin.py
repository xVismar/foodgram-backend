from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from recipes.constants import COOK_TIME_LONG, COOK_TIME_QUICK
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag, User
)


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    THRESHOLDS = {
        'Быстро': (0, COOK_TIME_QUICK - 1),
        'Средне': (COOK_TIME_QUICK, COOK_TIME_LONG - 1),
        'Долго': (COOK_TIME_LONG, 10**10),
    }

    def lookups(self, request, model):
        return [
            ((min_time, max_time), (f'{name} ({count})'))
            for name, (min_time, max_time) in self.THRESHOLDS.items()
            for count in (Recipe.objects.filter(
                cooking_time__range=[min_time, max_time]
            ).count(),
            )
        ]

    def queryset(self, request, queryset):
        if self.value():
            min_time, max_time = eval(self.value())
            return queryset.filter(
                cooking_time__range=[min_time, max_time]
            )
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0

    def ingredient_info(self, recipeingredient):
        ingredient = recipeingredient.ingredient
        return (
            f'{ingredient.name} ({ingredient.measurement_unit}) - '
            f'{recipeingredient.amount}'
        )
    readonly_fields = ('ingredient_info',)


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
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
        'get_ingredients',
        'image',
        'cooking_time'
    )
    search_fields = (
        'author__username',
        'name',
        'tags'
    )
    autocomplete_fields = ('author',)
    list_filter = (
        'tags',
        'author',
        CookingTimeFilter
    )
    inlines = (RecipeIngredientInline, RecipeTagInline, FavoriteInline)
    fieldsets = (
        (None, {'fields': ('name', 'author',)}),
        ('Описание', {'fields': ('text', 'cooking_time', 'image',)})
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
                    'image'
                ),
            },
        ),
    )
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    @admin.display(description='Продукты')
    @mark_safe
    def get_ingredients(self, recipe):
        return '<br>'.join((
            f'{recipe.ingredient.name} ( '
            f'{recipe.ingredient.measurement_unit}) {recipe.amount} '
            for recipe in recipe.recipeingredients.all())
        )

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    @mark_safe
    def get_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


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
    readonly_fields = (
        'get_subscriptions', 'get_recipes', 'get_favorited_recipes'
    )

    def get_queryset(self, request):
        return (
            super().get_queryset(request).filter(
                recipes__isnull=False).distinct()
        )

    @staticmethod
    def generate_link(user, description, url_name, field_name):
        count = getattr(user, field_name).count()
        if count > 0:
            return format_html(
                '<a href="{}?{}__id__exact={}">{count} {description}</a>',
                reverse('admin:' + url_name),
                'author',
                user.id,
                count=count,
                description=description
            )
        return 0

    link_data = {
        'Подписки': ('recipes_subscription_changelist', 'authors'),
        'Рецепты': ('recipes_recipe_changelist', 'recipes'),
        'Избранные рецепты': ('recipes_favorite_changelist', 'favorites')
    }

    @mark_safe
    @admin.display(description='Подписки')
    def get_subscriptions(self, user):
        return self.generate_link(
            user, 'подписок', *self.link_data['Подписки']
        )

    @mark_safe
    @admin.display(description='Рецепты')
    def get_recipes(self, user):
        return self.generate_link(user, 'рецепт', *self.link_data['Рецепты'])

    @mark_safe
    @admin.display(description='Избранные рецепты')
    def get_favorited_recipes(self, user):
        return self.generate_link(
            user, 'избранных рецептов', *self.link_data['Избранные рецепты']
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
