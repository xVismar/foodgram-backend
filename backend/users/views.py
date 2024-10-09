
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPagination
from users.models import UserSubscription
from users.serializers import (
    CustomUserCreateSerializer, CustomUserSerializer,
    CustomUserSetPasswordSerializer, UserSubscriptionSerializer
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def get_queryset(self):
        return User.objects.all().order_by(User._meta.ordering[0])

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return CustomUserSetPasswordSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['POST']
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['PUT', 'PATCH', 'DELETE'],
        permission_classes=(IsAuthenticated(),),
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        serializer = CustomUserSerializer(
            user, data=request.data, partial=True
        )
        if request.method != 'DELETE':
            if not request.data:
                return Response(
                    {'detail': 'Запрос не может быть пустым.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            user.avatar = 'avatars/default_avatar.jpeg'
            user.save()
            return Response(
                'Аватар не найден или аватар по умолчанию.',
                status=status.HTTP_404_NOT_FOUND
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': user.avatar.url},
            status=status.HTTP_200_OK
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
            return Response(
                'Вы не можете подписаться на себя.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            subscription = UserSubscription.objects.filter(
                user=user, author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Вы не подписаны на этого автора.',
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = UserSubscription.objects.get_or_create(
            user=user, author=author
        )
        if created:
            recipes_limit = request.query_params.get('recipes_limit')
            serializer = UserSubscriptionSerializer(
                author,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            'Вы уже подписаны на этого автора.',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated(),))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribed_to__user=user)
        recipes_limit = request.query_params.get('recipes_limit')
        page = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            page or queryset,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
        )
        return (
            self.get_paginated_response(serializer.data) if page is not None
            else Response(serializer.data)
        )
