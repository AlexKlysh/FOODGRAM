from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.filters import IngredientSearch, RecipeFilter
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeAddSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    TagSerializer
)
from api.pagination import CustomPagination
from api.permissions import AuthorOrReadOnly, ReadOnly
from recipes.models import (
    IngredientInRecipe,
    FavoriteRecipes,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет получения списка тэгов/одного тэга."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет получения списка ингредиентов/одного ингредиента.
    Доступен фильтр по полю name."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearch,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет Рецептов.
    Доступен фильтр по полям (tags, author, is_favorited,
    is_in_sopping_cart)."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (ReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return self.serializer_class
        return RecipeAddSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={
                    'user': user.id,
                    'recipe': recipe.id
                },
                context={
                    'request': request
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                FavoriteRecipes,
                user=user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={
                    'user': user.id,
                    'recipe': recipe.id
                },
                context={
                    'request': request
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = list(IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
                'ingredient__name', 'ingredient__measurement_unit', 'amount')
        )
        cart = {}
        for ingredient in ingredients:
            ing_unit = f'{ingredient[0]} ({ingredient[1]})'
            cart[ing_unit] = cart.get(ing_unit, 0) + ingredient[2]
        cart_data = 'Надо купить: \n'
        for item, value in cart.items():
            cart_data += (f'{item} - {value}\n')
        filename = 'shopping_cart.txt'
        response = HttpResponse(cart_data, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"')
        return response
