import webcolors
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import (
    MAX_QUANTITY,
    MIN_QUANTITY
)
from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.serializers import CustomUserSerializer


class Hex2NameColor(serializers.Field):
    """Метод перевода цвета в Hex в название."""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор Тэгов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Рецепта для вывода частичной информации о нем."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientInRecipe."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngridientAddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        required=True, min_value=MIN_QUANTITY, max_value=MAX_QUANTITY
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов/Рецепта."""
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True, source='recipe')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.fav_recipes.filter(
                user=request.user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.shopping_cart.filter(
                user=request.user
            ).exists()
        return False


class RecipeAddSerializer(serializers.ModelSerializer):
    """Сериализатор для получения Рецептов/Рецепта."""
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True
    )
    ingredients = IngridientAddRecipeSerializer(many=True, required=True)
    cooking_time = serializers.IntegerField(
        required=True, min_value=MIN_QUANTITY, max_value=MAX_QUANTITY
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'author',
            'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, attrs):
        ing_list = attrs.get('ingredients')
        tags_list = attrs.get('tags')

        if not ing_list:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        if not tags_list:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тэг'
            )
        if len(tags_list) != len(set(tags_list)):
            raise serializers.ValidationError(
                'Тэги не должны повторяться'
            )
        unique_ing_list = set([ing['id'] for ing in ing_list])
        if len(ing_list) != len(unique_ing_list):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return attrs

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredients_list = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if ingredients:
            instance.ingredients.clear()
        instance.tags.set(tags)
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор Избранного."""
    class Meta:
        model = FavoriteRecipes
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if user.fav_recipes_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт {recipe} уже добавлен в избранное'
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe, context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор Продуктовой Корзины."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if user.shopping_cart_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт {recipe} уже добавлен в корзину'
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe, context={'request': request}
        ).data
