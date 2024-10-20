
from django_filters.rest_framework import BooleanFilter, FilterSet

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited',)

    def filter_is_in_shopping_cart(self, recipes, name, is_in_shopping_cart):
        user = self.request.user
        if user.is_authenticated and is_in_shopping_cart:
            return recipes.filter(carts__user=user)
        return recipes

    def filter_is_favorited(self, recipes, name, is_favorited):
        user = self.request.user
        if user.is_authenticated and is_favorited:
            return recipes.filter(favorites__user=user)
        return recipes
