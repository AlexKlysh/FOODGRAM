from django.contrib import admin

from recipes.models import (
    FavoriteRecipes, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 2
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(IngredientInRecipe)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'is_favorited')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientInline, )
    filter_horizontal = ('tags',)

    def is_favorited(self, obj):
        return obj.fav_recipes.count()
    is_favorited.short_description = 'Добавлен в избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


admin.site.register(FavoriteRecipes)

admin.site.register(ShoppingCart)
