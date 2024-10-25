import numpy as np
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Case, CharField, ManyToManyField, Value, When
from django.forms import CheckboxSelectMultiple
from django.urls import reverse
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Subscription,
    Tag, User
)


admin.site.unregister(Group)


link_data = {
    'Подписки': ('recipes_subscription_changelist', 'authors'),
    'Рецепты': ('recipes_recipe_changelist', 'recipes'),
    'Избранные рецепты': ('recipes_favorite_changelist', 'favorites'),
    'Подписан': ('recipes_subscription_changelist', 'subscribers'),
}


def generate_link(model, filter, url_name, field_name):
    count = getattr(model, field_name).count()
    if count > 0:
        return (
            f'<a href="{reverse("admin:" + url_name)}'
            f'?{filter}__id__exact={model.id}">'
            f'{count}</a>'
        )
    return 0


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def _filter(self, min_time, max_time, object_to_filter):
        return (
            object_to_filter if not self.value()
            else object_to_filter.filter(
                cooking_time__range=(min_time, max_time)
            )
        )

    def lookups(self, request, model_admin):
        cooking_times = model_admin.model.objects.values_list(
            'cooking_time', flat=True
        )
        if not cooking_times:
            return []
        min_cooking_time = min(cooking_times)
        max_cooking_time = max(cooking_times)
        edges = np.linspace(
            min_cooking_time, max_cooking_time, 4, dtype=int
        )
        return [
            (
                (edges[i], edges[i + 1]),
                f'{edges[i]} - {edges[i + 1]} ( '
                f'{self._filter(edges[i], edges[i+1], Recipe.objects).count()}'
                ')'
            )
            for i in range(len(edges) - 1)
        ]

    def queryset(self, request, queryset):
        min_time, max_time = eval(self.value())
        return self._filter(min_time, max_time, queryset)


class HasRecipesFilter(admin.SimpleListFilter):
    title = 'Рецепты'
    parameter_name = 'Наличие рецептов'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        return (
            queryset.filter(recipes__isnull=False)
            if value == 'yes' else queryset
        )


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0
    verbose_name = 'Тэг'
    verbose_name_plural = 'Тэги'


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    verbose_name = 'Избранный рецепт'
    verbose_name_plural = 'Избранные рецепты'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    verbose_name = 'Продукт'
    verbose_name_plural = 'Продукты'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'ingredient':
            kwargs['queryset'] = Ingredient.objects.all().order_by('name')
            kwargs['widget'] = forms.Select(
                attrs={
                    'style': 'width: 250px;',
                }
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'amount':
            kwargs['widget'] = forms.TextInput(
                attrs={
                    'style': 'width: 100px;',
                }
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        to_label = formset.form.base_fields['ingredient']
        to_label.label_from_instance = self.label_from_instance
        return formset

    def label_from_instance(self, obj):
        return f'{obj.name} ({obj.measurement_unit})'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count',
        'get_tags',
        'get_ingredients',
        'thumbnail',
        'cooking_time',
    )
    search_fields = (
        'author__username',
        'name',
        'tags',
        'ingredients__name',
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
                ),
            },
        ),
    )
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def lookup_allowed(self, key, value):
        return True

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
        if recipe.image:
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
                f'<a href="{reverse("admin:recipes_recipe_changelist")}'
                f'?ingredients__id__exact={ingredient.id}">{count}</a>'
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

    def lookup_allowed(self, key, value):
        return True

    def generate_tag_link(self, tag):
        count = tag.recipes.count()
        if count > 0:
            return (
                f'<a href="{reverse("admin:recipes_recipe_changelist")}'
                f'?tags__id__exact={tag.id}">{count}</a>'
            )
        return 0

    @mark_safe
    @admin.display(description='Рецепты')
    def number_of_recipes(self, tag):
        return self.generate_tag_link(tag)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_recipe_link')

    @admin.display(description='Рецепт')
    @mark_safe
    def get_recipe_link(self, favorite):
        return (
            f'<a href="{reverse("admin:recipes_recipe_changelist")}'
            f'?id={favorite.recipe.id}">'
            f'{favorite.recipe.name}</a>'
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_recipe_link')

    @admin.display(description='Рецепт')
    @mark_safe
    def get_recipe_link(self, shopping_cart):
        return (
            f'<a href="{reverse("admin:recipes_recipe_changelist")}'
            f'?id={shopping_cart.recipe.id}">'
            f'{shopping_cart.recipe.name}</a>'
        )


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
    list_filter = (
        'is_staff',
        'is_superuser',
        HasRecipesFilter
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
            super().get_queryset(request).annotate(
                is_staff_display=Case(
                    When(is_staff=True, then=Value('Админ')),
                    default=Value('Пользователь'),
                    output_field=CharField(max_length=20)
                )
            )
        )

    @mark_safe
    @admin.display(description='Подписки')
    def number_of_subscribers(self, user):
        return generate_link(
            user, '', 'author', *link_data['Подписки']
        )

    @mark_safe
    @admin.display(description='Подписан')
    def number_of_subscriptions(self, user):
        return generate_link(
            user, '', 'author', *link_data['Подписан']
        )

    @mark_safe
    @admin.display(description='Рецептов')
    def number_of_recipes(self, user):
        return generate_link(user, '', 'author', *link_data['Рецепты'])

    @mark_safe
    @admin.display(description='Избранных')
    def number_of_favorites(self, user):
        return generate_link(
            user, '', 'author', *link_data['Избранные рецепты']
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
    list_display = ('user', 'get_author_link')

    @admin.display(description='Автор')
    @mark_safe
    def get_author_link(self, subscription):
        return (
            f'<a href="{reverse("admin:recipes_user_changelist")}'
            f'?id={subscription.author.id}">'
            f'{subscription.author.username}</a>'
        )
