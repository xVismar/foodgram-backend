from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


import recipes.constants as CONST
from recipes.validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        max_length=CONST.MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=CONST.MAX_STR_LENGTH,
        unique=True,
        validators=[validate_username],
        verbose_name='Ник',
    )
    first_name = models.CharField(
        max_length=CONST.MAX_STR_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=CONST.MAX_STR_LENGTH,
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
        return self.username[:CONST.MAX_STR_LENGTH]

    @property
    def number_of_recipes(self):
        return self.recipes.count()

    @property
    def number_of_subscriptions(self):
        return self.authors.count()

    @property
    def number_of_subscribers(self):
        return self.subscribers.count()


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
            models.UniqueConstraint(
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
        max_length=CONST.MAX_TAG_LENGTH,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=CONST.MAX_TAG_LENGTH,
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:CONST.MAX_STR_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=CONST.MAX_INGREDIENT_NAME_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=CONST.MAX_MEASUREMENT_UNIT_LENGTH,
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
        return self.name[:CONST.MAX_STR_LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=CONST.MAX_RECIPE_NAME_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание'
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
                CONST.MIN_AMOUNT_COOK_TIME_INGREDIENT,
                (
                    'Время приготовления не может быть меньше '
                    f'{CONST.MIN_AMOUNT_COOK_TIME_INGREDIENT}'
                )
            )
        ],
        verbose_name='Время готовки (мин)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Создан'
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name[:CONST.MAX_STR_LENGTH]


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
                CONST.MIN_AMOUNT_INGREDIENT,
                f'Мера не может быть меньше {CONST.MIN_AMOUNT_INGREDIENT}'
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
        return (
            f'{self.ingredient.name} {self.ingredient.measurement_unit} в '
            f'{self.recipe.name}'
        )


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
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                name='unique_%(class)s_constraint',
                fields=['user', 'recipe']
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class ShoppingCart(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'В избранном'
        verbose_name_plural = 'В избранных'
