
from datetime import datetime

from django.http import HttpResponse
from django.db.models import Exists, OuterRef, Sum
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils.text import slugify

from api.filters import RecipeFilter
from api.pagination import CustomPagination, PaginationNone
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientsSerializer, RecipeSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, RecipeIngredient
)
from users.serializers import RecipeMiniSerializer


class CustomHandleMixin:

    def handle_cart_action(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            try:
                item = model.objects.get(user=user, recipe=recipe)
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except model.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


# def shopping_cart_list(ingredients, cart):
#     today = datetime.now().strftime('%d-%m-%Y')
#     ingredients_dict = {}
#     for ingredient in ingredients:
#         name = ingredient['ingredient__name']
#         unit = ingredient['ingredient__measurement_unit']
#         amount = ingredient['total_amount']

#         if name in ingredients_dict:
#             ingredients_dict[name]['total_amount'] += amount
#         else:
#             ingredients_dict[name] = {
#                 'unit': unit,
#                 'total_amount': amount
#             }
#     ingredients_info = [
#         f"{i}. {name.capitalize()} ({info['unit']}) — {info['total_amount']}"
#         for i, (name, info) in enumerate(ingredients_dict.items(), start=1)
#     ]
#     recipes = [recipe.name for recipe in cart]
#     shopping_list = '\n'.join([
#         f'Дата составления списка покупок: {today}',
#         f'Для приготовления следующих рецептов: {recipes}',
#         'Вам потребуется купить продуктов:',
#         *ingredients_info
#     ])
#     return shopping_list


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
            return (IsAuthenticated, IsAuthorOrReadOnly,)
        return (AllowAny,)

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

    def perform_create(self, serializer):
        recipe = serializer.save(author=self.request.user)
        recipe.short_link = slugify(recipe.title)[:10]
        recipe.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return self.handle_cart_action(request, pk, ShoppingCart)
    # @action(
    #     detail=False,
    #     methods=['GET'],
    #     permission_classes=(IsAuthenticated,),
    #     url_path='download_shopping_cart'
    # )
    # def download_shopping_cart(self, request):
    #     user = request.user
    #     cart = user.shoping_cart.all().values_list('recipe', flat=True)
    #     cart_recipes = Recipe.objects.filter(
    #         id__in=cart
    #     ).prefetch_related('ingredients')
    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__in=cart_recipes
    #     ).values(
    #         'ingredient__name',
    #         'ingredient__measurement_unit',
    #         total_amount=Sum('amount')
    #     ).annotate(
    #         recipe=F('recipe__id')
    #     )
    #     shopping_list = shopping_cart_list(ingredients, cart_recipes)
    #     filename = f'{user.username}_shopping_list.txt'
    #     response = HttpResponse(shopping_list, content_type='text/plain')
    #     response['Content-Disposition'] = f'attachment; filename={filename}'
    #     return response

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(content_type='text/plain')
        cart = user.shoping_cart.all().values_list('recipe', flat=True)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=cart
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')
                   ).order_by('ingredient__name')
        today = datetime.now().strftime('%d-%m-%Y')
        message = (
            f'Дата составления списка покупок: {today}\n\n'
            f'Для приготовления следующих рецептов: {cart}\n\n'
            'Вам потребуется купить продуктов:\n\n'
        )
        response.write(message.encode('utf-8'))
        for ingredient, item in enumerate(ingredients, start=1):
            info = (
                f'{ingredient}. {item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) - '
                f'{item["total_amount"]}\n'
            )
            response.write(info.encode('utf-8'))
        return response

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
        permission_classes=(IsAuthenticated,),
        url_path='get_link'
    )
    def get_link(self, request, *args, **kwargs):
        url = request.build_absolute_uri('/s/')
        return Response(
            {'short-link': f'{url}{self.get_object().short_link}'}
        )


@api_view(['GET'])
def redirect_short_link(request, short_id):
    recipe = get_object_or_404(Recipe, short_link=short_id)
    return redirect(f'/recipes/{recipe.id}/')
