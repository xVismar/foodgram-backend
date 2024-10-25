from django_filters.rest_framework import BooleanFilter, FilterSet, CharFilter
from django.contrib.auth.models import AnonymousUser

from recipes.models import Recipe, Ingredient


class RecipeFilter(FilterSet):
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart',
    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited',
    )

    def filter_by_relation(self, queryset, name, value):
        return (
            queryset if not value or isinstance(
                self.request.user, AnonymousUser
            ) else (
                queryset.filter(favorites__user=self.request.user) if name
                else queryset.filter(shoppingcarts__user=self.request.user)
            )
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_by_relation(queryset, None, value)

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_by_relation(queryset, name, value)

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited')


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
