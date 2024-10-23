import datetime


def shopping_cart_list(ingredients, cart_recipes):
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    ingredients_info = [
        f'{i}. {ingredient["ingredient_name"].capitalize()} - '
        f'{ingredient["total_amount"]}'
        f'({ingredient["ingredient_unit"]})'

        for i, ingredient in enumerate(ingredients, start=1)
    ]
    recipe_names = [f'- {recipe.name}' for recipe in cart_recipes]
    shopping_list = '\n'.join([
        f'Дата составления списка покупок: {today}',
        'Для приготовления следующих рецептов:',
        *recipe_names,
        'Вам потребуется купить продуктов:',
        *ingredients_info
    ])
    return shopping_list
