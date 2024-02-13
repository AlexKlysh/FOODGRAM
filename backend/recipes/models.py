from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель Тэгов."""
    name = models.CharField('Назавание тэга', max_length=200)
    color = ColorField('HEX-код цвета', max_length=7, unique=True)
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    def __str__(self) -> str:
        return self.name[:20]

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)


class Ingredient(models.Model):
    """Модель Ингредиентов."""
    name = models.CharField('Название продукта', max_length=200)
    measurement_unit = models.CharField('Мера измерения', max_length=50)

    def __str__(self) -> str:
        return self.name[:20]

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Recipe(models.Model):
    """Модель Рецептов."""
    author = models.ForeignKey(
        User, verbose_name="Автор",
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField('Назавание рецепта', max_length=200)
    image = models.ImageField(
        'Фото', upload_to='recipes/images',
        default=None
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(
            1, message='Время приготовления не может быть меньше 1 минуты'
        ),)
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipes',
        through='IngredientInRecipe'
    )
    pub_date = models.DateTimeField('Время побликации', auto_now_add=True)

    def __str__(self) -> str:
        return self.name[:20]

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class IngredientInRecipe(models.Model):
    """Модель для связи Ингредиентов и рецептов."""
    recipe = models.ForeignKey(
        Recipe, related_name='recipe', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, related_name='ingredient', on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(
            1, message='Количесвто не может быть меньше 1'
        ),)
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self) -> str:
        return f'{self.ingredient} in {self.recipe}'


class FavoriteRecipes(models.Model):
    """Модель Избранного."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='fav_recipes_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='fav_recipes',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_fovorite',
            ),
        ]

    def __str__(self):
        return f"{self.recipe} in {self.user}'s favorites"


class ShoppingCart(models.Model):
    """Модель Списка Покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Корзина',
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]

    def __str__(self):
        return f"{self.recipe} in {self.user}'s shopping cart"
