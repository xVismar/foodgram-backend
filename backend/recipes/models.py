from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from api.validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        max_length=settings.MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=settings.MAX_STR_LENGTH,
        unique=True,
        validators=[validate_username],
        verbose_name='Ник',
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


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribers'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.user.username} подписан на {self.author.username}'
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=settings.MAX_TAG_LENGTH,
        unique=True,
        verbose_name='Название тэга'
    )
    slug = models.SlugField(
        max_length=settings.MAX_TAG_LENGTH,
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:settings.MAX_STR_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.MAX_INGREDIENT_NAME_LENGTH,
        verbose_name='Название Продукта'
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_ingredient',
                fields=['name', 'measurement_unit']
            )
        ]
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name[:settings.MAX_STR_LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=settings.MAX_RECIPE_NAME_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_AMOUNT_COOK_TIME_INGREDIENT,
                'Время приготовления не может быть меньше 1 минуты.'
            )
        ],
        verbose_name='Время приготовления'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Время создания рецепта'
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name[:settings.MAX_STR_LENGTH]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_AMOUNT_COOK_TIME_INGREDIENT,
                'Мера не может быть меньше 1'
            )
        ],
        verbose_name='Мера'
    )

    class Meta:
        default_related_name = 'recipeingredients'
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_ingredient',
                fields=['recipe', 'ingredient']
            )
        ]
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецепте'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class UserRecipeBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class ShoppingCart(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        default_related_name = 'carts'
        constraints = [
            models.UniqueConstraint(
                name='unique_cart_recipes',
                fields=['user', 'recipe']
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite_recipes',
                fields=['user', 'recipe']
            )
        ]
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
