from ast import literal_eval

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import CharField, Case, ManyToManyField, When, Value
from django.forms import CheckboxSelectMultiple
from django.urls import reverse
from django.utils.safestring import mark_safe

from recipes.constants import COOK_TIME_LONG, COOK_TIME_QUICK
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag, User
)


admin.site.unregister(Group)


link_data = {
    'Подписки': ('recipes_subscription_changelist', 'authors'),
    'Рецепты': ('recipes_recipe_changelist', 'recipes'),
    'Избранные рецепты': ('recipes_favorite_changelist', 'favorites'),
    'Подписан': ('recipes_subscription_changelist', 'subscribers'),
    'Продукты': ('ingredient_recipes_changelist', 'recipeingredients')
}


def generate_link(model, description, filter, url_name, field_name):
    count = getattr(model, field_name).count()
    if count > 0:
        return (
            f'<a href="{reverse("admin:" + url_name)}'
            f'?{filter}__id__exact={model.id}">'
            f'{count} {description}</a>'
        )
    return 0


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    THRESHOLDS = {
        'Быстро': (1, COOK_TIME_QUICK - 1),
        'Средне': (COOK_TIME_QUICK, COOK_TIME_LONG - 1),
        'Долго': (COOK_TIME_LONG, 100 * 100),
    }

    @staticmethod
    def cooking_time_range_filter(time_range, recipes_to_sort):
        return recipes_to_sort.filter(cooking_time__range=[*time_range])

    def lookups(self, request, model):
        return [
            (
                (min_time, max_time),
                (
                    f'{name} ({count}) {min_time} '
                    f'{-max_time if max_time < 1000 else ""}'
                )
            )
            for name, (min_time, max_time) in self.THRESHOLDS.items()
            for count in [self.cooking_time_range_filter(
                [min_time, max_time], Recipe.objects
            ).count()]
        ]

    def queryset(self, request, queryset):
        if self.value():
            return (
                self.cooking_time_range_filter(
                    literal_eval(self.value()),
                    queryset
                )
            )
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    fields = ('ingredient', 'amount')
    readonly_fields = ('unit',)
    list_display = ('unit',)

    @admin.display(description='Единица измерения')
    def unit(self, recipeingredient):
        return ''.join(f'{recipeingredient.ingredient.measurement_unit}')

    @admin.display(description='Продукты')
    @mark_safe
    def get_ingredients(self, recipe):
        return '<br>'.join((
            f'{recipe.ingredient.name} ( '
            f'{recipe.ingredient.measurement_unit}) {recipe.amount} '
            for recipe in recipe.recipeingredients.all())
        )


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0
    verbose_name = "Тэг"
    verbose_name_plural = "Тэги"


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
        'thumbnail',
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
                    'thumbnail',
                ),
            },
        ),
    )
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
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

    @admin.display(description='Тэги')
    @mark_safe
    def get_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Картинка')
    @mark_safe
    def thumbnail(self, recipe):
        return (
            '<img src="{0}" width="100px" height="100px" />'.format(
                recipe.image.url
            )
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit', 'number_of_recipes'
    )
    search_fields = ('name', 'measurement_unit', 'recipes')
    list_filter = ('recipes',)

    def generate_ingredient_link(self, ingredient):
        count = ingredient.recipes.count()
        if count > 0:
            return (
                f'<a href="/admin/recipes/recipe/'
                f'?ingredients={ingredient.id}">{count}</a>'
            )
        return 0

    @mark_safe
    @admin.display(description='Рецепты')
    def number_of_recipes(self, ingredient):
        return self.generate_ingredient_link(ingredient)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'number_of_recipes')
    search_fields = ('name', 'slug')
    list_filter = ('name',)

    def generate_tag_link(self, tag):
        count = tag.recipes.count()
        if count > 0:
            return (
                f'<a href="/admin/recipes/recipe/'
                f'?tags={tag.id}">{count}</a>'
            )
        return 0

    @mark_safe
    @admin.display(description='Рецепты')
    def number_of_recipes(self, tag):
        return self.generate_tag_link(tag)


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
        'is_staff_display',
        'is_superuser_display',
        'number_of_recipes',
        'number_of_subscriptions',
        'number_of_subscribers',
        'number_of_favorites',
        'avatar_image'
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

    def get_queryset(self, request):
        return (
            super().get_queryset(request).filter(
                recipes__isnull=False).distinct().annotate(
                    is_staff_display=Case(
                        When(is_staff=True, then=Value('Админ')),
                        default=Value('Пользователь'),
                        output_field=CharField()
                    )
            )
        )

    @mark_safe
    @admin.display(description='Подписки')
    def number_of_subscribers(self, user):
        return generate_link(
            user, 'подписок', 'author', *link_data['Подписки']
        )

    @mark_safe
    @admin.display(description='Подписан')
    def number_of_subscriptions(self, user):
        return generate_link(
            user, 'подписан', 'author', *link_data['Подписан']
        )

    @mark_safe
    @admin.display(description='Рецептов')
    def number_of_recipes(self, user):
        return generate_link(user, '', 'author', *link_data['Рецепты'])

    @mark_safe
    @admin.display(description='Избранных')
    def number_of_favorites(self, user):
        return generate_link(
            user, 'избранных', 'author', *link_data['Избранные рецепты']
        )

    @admin.display(description='Штат')
    def is_staff_display(self, user):
        return user.is_staff_display

    @mark_safe
    @admin.display(description='Супер')
    def is_superuser_display(self, user):
        return (
            '<img src="/static/admin/img/icon-yes.svg" alt="True">'
            if user.is_superuser else
            '<img src="/static/admin/img/icon-no.svg" alt="False">'
        )

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_image(self, user):
        if user.avatar:
            return (
                '<img src="{0}" width="100px" height="100px" />'.format(
                    user.avatar.url
                )
            )
        return ' '


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
