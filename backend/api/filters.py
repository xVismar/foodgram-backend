from django_filters.rest_framework import filters, FilterSet, CharFilter


from recipes.models import Recipe, Ingredient


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filger_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'is_in_shopping_cart', 'is_favorited')

    def user_related_filter(self, recipes, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if user and value:
            return recipes.filter(
                shoppingcarts__user=user if name == 'is_in_shopping_cart'
                else None,
                favorites__user=user if name == 'is_favorited'
                else None
            )
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        return self.user_related_filter(recipes, name, value)

    def filger_is_favorited(self, recipes, name, value):
        return self.user_related_filter(recipes, name, value)


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
