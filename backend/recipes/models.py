from django.core.validators import MinValueValidator
from django.db import models
import shortuuid
from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_TAG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Идентификатор тэга',
        max_length=settings.MAX_TAG_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:settings.MAX_STR_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:settings.MAX_STR_LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_RECIPE_NAME_LENGTH,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть меньше 1 минуты.'
            )
        ]
    )
    short_link = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Короткая ссылка',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Время создания'
    )

    class Meta:
        default_related_name = '%(class)ss'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name[:settings.MAX_STR_LENGTH]

    def get_or_create_short_link(self):
        if not self.short_link:
            self.short_link = shortuuid.uuid()[:10]
            self.save(update_fields=['short_link'])
        return self.short_link


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,

        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1, 'Количество ингредиентов не может быть меньше 1'
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_recipe_ingredient',
                                    fields=['recipe', 'ingredient'])
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (
            f'{self.ingredient.name} - '
            f'{self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(name='unique_shopping_cart',
                                    fields=['user', 'recipe'])
        ]

    def __str__(self):
        return f'{self.recipe.name} в корзине у {self.user.username}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(name='unique_favorite',
                                    fields=['user', 'recipe'])
        ]

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'
