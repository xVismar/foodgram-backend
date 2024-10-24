from django_filters.rest_framework import BooleanFilter, FilterSet, CharFilter

from recipes.models import Recipe, Ingredient


class RecipeFilter(FilterSet):
    is_in_shopping_cart = BooleanFilter(
        method='user_related_filter',
    )
    is_favorited = BooleanFilter(
        method='user_related_filter',
    )

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited')

    def user_related_filter(self, recipes, name, value):
        user = self.request.user
        if user.is_authenticated:
            return recipes.filter(
                shoppingcarts__user=user if name == 'is_in_shopping_cart'
                else None,
                favorites__user=user if name == 'is_favorited'
                else None,
            ).distinct()
        return recipes


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
