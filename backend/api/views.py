import datetime
import tempfile
import os


from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.views import View
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination, PaginationNone
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientsSerializer, RecipeSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.serializers import RecipeMiniSerializer


class CustomHandleMixin:

    def handle_cart_action(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            try:
                recipe = model.objects.get(user=user, recipe=recipe)
                recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except model.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def shopping_cart_list(ingredients, cart_recipes):
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    ingredients_dict = {}
    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['amount']
        if name in ingredients_dict:
            ingredients_dict[name]['total_amount'] += amount
        else:
            ingredients_dict[name] = {
                'unit': unit,
                'total_amount': amount
            }
    ingredients_info = [
        f"{i}. {name.capitalize()} ({info['unit']}) — {info['total_amount']}"
        for i, (name, info) in enumerate(ingredients_dict.items(), start=1)
    ]
    recipes = Recipe.objects.filter(id__in=cart_recipes)
    recipe_names = [recipe.name for recipe in recipes]
    shopping_list = '\n'.join([
        f'Дата составления списка покупок: {today}',
        f'Для приготовления следующих рецептов: {recipe_names}',
        'Вам потребуется купить продуктов:',
        *ingredients_info
    ])
    return shopping_list


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = PaginationNone


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    pagination_class = PaginationNone
    search_fields = ('name',)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet, CustomHandleMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('tags__slug',)

    def get_permissions(self):
        actions = [
            'create', 'update', 'partial_update', 'destroy', 'favorite',
            'download_shopping_cart', 'shopping_cart'
        ]
        if self.action in actions:
            return (IsAuthenticated(), IsAuthorOrReadOnly(),)
        return (AllowAny(),)

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(user=user,
                                                recipe=OuterRef('pk'))
                )
            )
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if author:
            queryset = queryset.filter(author__id=author)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return self.handle_cart_action(request, pk, ShoppingCart)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        return self.handle_cart_action(request, pk, Favorite)

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = recipe.get_or_create_short_link()
        short_url = request.build_absolute_uri(f'/s/{short_link}')
        return Response(
            {'short-link': short_url}, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        cart = request.user.shopping_cart.all().values_list(
            'recipe', flat=True
        )
        cart_recipes = Recipe.objects.filter(id__in=cart)
        ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=cart
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )
        shopping_list = shopping_cart_list(ingredients, cart_recipes)
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.txt'
        ) as temp_file:
            temp_file.write(shopping_list)
            temp_file_path = temp_file.name
        filename = f'{request.user.username}_shopping_list.txt'
        response = HttpResponse(
            open(temp_file_path, 'rb'),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        os.remove(temp_file_path)
        return response


class ShortLinkRedirectView(View):
    def get(self, request, short_id):
        recipe = get_object_or_404(Recipe, short_link=short_id)
        return redirect(
            'https://foodgram-vismar.ddns.net/recipes/' + str(recipe.id)
        )
