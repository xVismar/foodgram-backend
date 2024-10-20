
from django_filters.rest_framework import BooleanFilter, FilterSet

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_in_shopping_cart = BooleanFilter(
        method='user_related_filter',
        related_field='shoppingcarts'
    )
    is_favorited = BooleanFilter(
        method='user_related_filter',
        related_field='favorites'
    )

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited')

    def user_related_filter(self, recipes, name, is_related, related_field):
        user = self.request.user
        if user.is_authenticated and is_related:
            return recipes.filter(**{related_field + '__user': user})
        return recipes
