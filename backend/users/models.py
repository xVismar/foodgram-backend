from django.db import models
from django.contrib.auth.models import AbstractUser
from users.validators import validate_username
from django.conf import settings
from django.db.models import UniqueConstraint
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name',]
    email = models.EmailField(
        max_length=settings.MAX_EMAIL_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Почта',
        error_messages={
            'unique': 'Пользователь с таким адресом уже зарегистрирован',
        },
    )
    username = models.CharField(
        max_length=settings.MAX_STR_LENGTH,
        unique=True,
        validators=[validate_username, UnicodeUsernameValidator()],
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=settings.MAX_STR_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.MAX_STR_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default=None,
        null=True,
        verbose_name='Аватар'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:settings.MAX_STR_LENGTH]


class UserSubscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribed_to",
        verbose_name='Автор рецепта'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'], name='unique_subscribers'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.user.username} подписан на {self.author.username}'
        )
