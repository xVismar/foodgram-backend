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

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not isinstance(self.request.user, AnonymousUser):
            return (
                queryset.filter(shoppingcarts__user=self.request.user)
                if value else queryset
            )
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value and not isinstance(self.request.user, AnonymousUser):
            return (
                queryset.filter(favorites__user=self.request.user)
                if value else queryset
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited')


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
