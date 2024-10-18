import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.serializers import RecipeMiniSerializer
from recipes.models import Recipe


def handle_cart_actions(request, pk, model):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'DELETE':
        try:
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            raise Exception('Нет добавленных.')
    _, created = model.objects.get_or_create(user=user, recipe=recipe)
    if not created:
        raise Exception('Ошибка добавления.')
    serializer = RecipeMiniSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def shopping_cart_list(ingredients, cart_recipes):
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    ingredients_info = [
        f'{i}. {ingredient["ingredient__name"].capitalize()}'
        f'({ingredient["ingredient__measurement_unit"]}) — '
        f'{ingredient["total_amount"]}'
        for i, ingredient in enumerate(ingredients, start=1)
    ]
    recipes = Recipe.objects.filter(id__in=cart_recipes)
    recipe_names = [recipe.name for recipe in recipes]
    shopping_list = '\n'.join([
        f'Дата составления списка покупок: {today}',
        f'Для приготовления следующих рецептов: {recipe_names}',
        'Вам потребуется купить продуктов:',
        *ingredients_info
    ])
    return shopping_list


def get_data_set(data):
    return set(item['id'] for item in data)
