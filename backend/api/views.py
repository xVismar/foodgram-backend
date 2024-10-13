
from datetime import datetime

from django.core.files.base import ContentFile
from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.encoding import smart_bytes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientsSerializer, RecipeSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.serializers import RecipeMiniSerializer


class CustomHandleMixin:

    def custom_add_remove_handle(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            try:
                item = model.objects.get(user=user, recipe=recipe)
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except model.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def shopping_cart_list(ingredients, cart):
    today = datetime.now().strftime('%d-%m-%Y')
    ingredients_info = [
        f"{i}. {ingredient['ingredient__name'].capitalize()} "
        f"({ingredient['ingredient__measurement_unit']}) — "
        f"{ingredient['total_amount']}"
        for i, ingredient in enumerate(ingredients, start=1)
    ]
    recipes = [recipe.name for recipe in cart]
    return '\n'.join([
        f'Дата составления списка покупок: {today}',
        f'Для приготовления следующих рецептов: {recipes}'
        'Вам потрубется купить продуктов:'
        f'{ingredients_info}'
    ])


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
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
    permission_classes = (AllowAny,)
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
        return queryset.order_by('id')

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = recipe.get_or_create_short_link()
        short_url = request.build_absolute_uri(f'/s/{short_link}')
        return Response(
            {'short-link': short_url}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return self.custom_add_remove_handle(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user).values_list(
            'recipe', flat=True
        )
        ingredients_sum = (
            RecipeIngredient.objects.filter(recipe__in=shopping_cart)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        shopping_list = smart_bytes(
            shopping_cart_list(ingredients_sum, shopping_cart)
        )
        return FileResponse(
            ContentFile(shopping_list),
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        return self.custom_add_remove_handle(request, pk, Favorite)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


def redirect_short_link(request, short_id):
    recipe = get_object_or_404(Recipe, short_link=short_id)
    return redirect(f'/recipes/{recipe.id}')
