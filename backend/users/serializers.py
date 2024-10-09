
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import Recipe
from users.models import UserSubscription


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class BaseCustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserSubscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class CustomUserSerializer(BaseCustomUserSerializer):
    avatar = Base64ImageField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed', 'avatar'
        )

    def update(self, instance, validated_data):
        default_avatar = 'avatars/default_avatar.jpeg'
        if instance.avatar and instance.avatar.name != default_avatar:
            instance.avatar.delete()
        instance.avatar = validated_data.get('avatar', None)
        return super().update(instance, validated_data)


class CustomUserSetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data.get('current_password')):
            raise serializers.ValidationError(
                'Текущий пароль не верен.')
        return data


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscriptionSerializer(BaseCustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed', 'avatar', 'recipes_count', 'recipes'
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        limit = self.context.get('recipes_limit')
        if limit:
            queryset = queryset[: int(limit)]
        return RecipeMiniSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
