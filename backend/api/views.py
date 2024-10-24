from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPagePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CurentUserSerializer, IngredientsSerializer, RecipeMiniSerializer,
    RecipeSerializer, SubscriptionSerializer, TagSerializer
)
from api.services import shopping_cart_list
from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Subscription, Tag
)

User = get_user_model()


class CurentUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CurentUserSerializer
    pagination_class = LimitPagePagination
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        serializer = CurentUserSerializer(
            user, data=request.data, partial=True
        )
        if request.method != 'DELETE':
            if not request.data:
                raise ValidationError('Запрос не может быть пустым.')
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError('Аватар не найден или аватар по умолчанию.')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': user.avatar.url}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError('Вы не можете подписаться на себя.')
        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        _, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            raise ValidationError('Вы уже подписаны на этого автора.')
        serializer = SubscriptionSerializer(
            author,
            context={
                'request': request,
                'recipes_limit': int(request.GET.get('recipes_limit', 10**10))
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(authors__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page or queryset,
            many=True,
            context={
                'request': request,
                'recipes_limit': int(request.GET.get('recipes_limit', 10**10))
            },
        )
        return (
            self.get_paginated_response(serializer.data) if page is not None
            else Response(serializer.data)
        )


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('tags__slug',)
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly,)

    def get_permissions(self):
        return (
            (AllowAny(),) if self.request.method in SAFE_METHODS
            else super().get_permissions()
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        favorite = self.request.query_params.get('favorites')
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
        if favorite:
            queryset = queryset.filter(favorites__user=user)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return Response(
            {'short-link': request.build_absolute_uri(f'/s/{recipe.id}')},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        cart = request.user.shoppingcarts.prefetch_related(
            'recipe__recipeingredients__ingredient'
        ).annotate(
            ingredient_name=F('recipe__recipeingredients__ingredient__name'),
            ingredient_unit=F(
                'recipe__recipeingredients__ingredient__measurement_unit'
            ),
            total_amount=Sum('recipe__recipeingredients__amount')
        ).values(
            'recipe__id',
            'ingredient_name',
            'ingredient_unit',
            'total_amount'
        )
        cart_recipes = Recipe.objects.filter(id__in=cart.values('recipe__id'))
        return FileResponse(
            shopping_cart_list(cart, cart_recipes),
            content_type='text/plain; charset=utf-8'
        )

    @staticmethod
    def manage_user_recipe_relation(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            _, created = model.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                raise ValueError(
                    f'Ошибка добавления рецепта {recipe.name} для пользователя'
                    f' {user.username}. Рецепт уже был добавлен'
                )
            return Response(
                RecipeMiniSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.manage_user_recipe_relation(request, pk, ShoppingCart)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,)

    )
    def favorite(self, request, pk=None):
        return self.manage_user_recipe_relation(request, pk, Favorite)
