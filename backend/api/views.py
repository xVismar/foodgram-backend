from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import LimitPagePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CurentUserSerializer, IngredientsSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer
)
from api.services import handle_cart_actions, shopping_cart_list
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag
)


User = get_user_model()


class CurentUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CurentUserSerializer
    pagination_class = LimitPagePagination
    permission_classes = (AllowAny,)

    def get_permissions(self):
        return (
            (IsAuthenticated(),)
            if self.action not in ['create', 'list', 'retrieve']
            else (AllowAny,)
        )

    @action(
        detail=False,
        methods=['PUT', 'PATCH', 'DELETE'],
        permission_classes=(IsAuthenticated(),),
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
            user.avatar = 'avatars/default_avatar.jpeg'
            user.save()
            raise ValidationError('Аватар не найден или аватар по умолчанию.')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': user.avatar.url}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated(),)
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError('Вы не можете подписаться на себя.')
        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=user, author=author).delete()
        _, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            raise ValidationError('Вы уже подписаны на этого автора.')
        recipes_limit = int(request.GET.get('recipes_limit', 0))
        serializer = SubscriptionSerializer(
            author,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated(),)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribed_to__user=user)
        recipes_limit = int(request.GET.get('recipes_limit', 0))
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page or queryset,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
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
    search_fields = ('name',)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('tags__slug',)
    permission_classes = (IsAuthenticated(), IsAuthorOrReadOnly(),)

    def get_permissions(self):
        actions = [
            'create', 'update', 'partial_update', 'destroy', 'favorite',
            'download_shopping_cart', 'shopping_cart'
        ]
        return (
            (AllowAny(),) if self.action not in actions
            else super().get_permissions()
        )

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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return handle_cart_actions(request, pk, ShoppingCart)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        return handle_cart_actions(request, pk, Favorite)

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f'/s/{recipe.id}')
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
        ).annotate(total_amount=Sum('amount'))
        return (
            FileResponse(
                shopping_cart_list(ingredients, cart_recipes),
                content_type='text/plain; charset=utf-8'
            )
        )


def redirect_short_link(request, short_id):
    recipe = get_object_or_404(Recipe, short_link=short_id)
    api_url = reverse('api:recipe-detail', args=[recipe.id])
    front_url = api_url.replace('/api/', '')
    return redirect(front_url)
