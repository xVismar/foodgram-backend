from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()

recipes_data = {
    "recipe_one": {
        "ingredients": [
            {"id": 2180, "amount": 2},
            {"id": 591, "amount": 1},
            {"id": 1546, "amount": 1},
            {"id": 1419, "amount": 1},
            {"id": 1684, "amount": 1},
            {"id": 1669, "amount": 1},
            {"id": 1081, "amount": 220}
        ],
        "tags": [2],
        "image": "recipes/recipe_one.jpg",
        "name": "Оладушки, которые не опадают",
        "text": (
            "Важны 3 фактора:\n"
            "1. Прогрев кефира\n"
            "2. Очередность ингредиентов (особенно соды)\n"
            "3. Густота теста и ни в коем случае не мешать готовое тесто. "
            "Можно дать ему постоять 5-10 минут, чтобы у соды было время "
            "среагировать. Но когда времени нет, я готовлю сразу.\n\n"
            "1. Соединить кефир, яйца, сахар и соль.\n"
            "Поставить кастрюлю на средний огонь.\n"
            "Нужно подогреть так, чтобы опущенному пальцу было горячо, но "
            "терпимо (постоянно помешивать и следить, чтобы яйца не свернулись"
            ")\n\n"
            "2. Всыпаем муку, взбиваем до однородности.\n"
            "Количество муки зависит от густоты кефиры.\n"
            "Если он жидкий, потребуется 3 неполных ст.л. дополнительно.\n"
            "Тесто должно ооочень медленно стекать с ложки\n\n"
            "3. Добавляем соду, перемешиваем, затем вливаем масло.\n"
            "Еще раз перемешать и далее тесто размешивать нельзя\n\n"
            "4. На разогретую сковороду наливаем масло и выкладываем по"
            "1 ст.л. теста.\n"
            "Жарим до золотистой корочки, переворачиваем и доготавливаем под "
            "крышкой также до румяной корочки."
        ),
        "cooking_time": 30,
        "author": 2
    },
    "recipe_two": {
        "ingredients": [
            {"id": 520, "amount": 1000},
            {"id": 886, "amount": 1},
            {"id": 959, "amount": 1},
            {"id": 1081, "amount": 70},
            {"id": 2055, "amount": 25},
            {"id": 1890, "amount": 20},
            {"id": 1419, "amount": 50},
            {"id": 1742, "amount": 100},
            {"id": 1684, "amount": 20},
            {"id": 1724, "amount": 40}
        ],
        "tags": [2],
        "image": "recipes/recipe_two.jpg",
        "name": "Постные котлеты",
        "text": (
            "Капусту разрежьте на 4 части и приварите в подсоленной воде минут"
            " 8-10.\\n"
            "Откиньте капусту на дуршлаг,пропустите через мясорубку и отожмите"
            ", чтобы удалить воду.\\n"
            "На мелкой терке натрите лук и пропустите чеснок через "
            "пресс-чеснок.\\n"
            "'Укроп мелко нарежьте.\\n"
            "К капусте добавьте лук, чеснок и зелень. Посолите, приправьте "
            "специями по вкусу.\\n"
            "Добавьте муку, манную крупу, тщательно перемешайте.\\n"
            "Сформируйте из этой массы котлетки, обваляйте в панировочных "
            "сухарях и обжарьте на растительном масле до хрустящей золотистой "
            "корочки.\\n"
            "Приятного аппетита!!!"
        ),
        "cooking_time": 40,
        "author": 3
    },
    "recipe_three": {
        "ingredients": [
            {"id": 1081, "amount": 500},
            {"id": 1419, "amount": 50},
            {"id": 609, "amount": 150},
            {"id": 1032, "amount": 150},
            {"id": 402, "amount": 20},
            {"id": 1546, "amount": 15},
            {"id": 1684, "amount": 5},
            {"id": 2180, "amount": 5},
            {"id": 879, "amount": 200},
            {"id": 1646, "amount": 25}
        ],
        "tags": [5],
        "image": "recipes/recipe_three.jpg",
        "name": (
            "Пирожки-минутка, жареные с луком и яйцом, быстрое заварное тесто"
        ),
        "text": (
            "Тесто очень быстрое, к началу замеса желательно приготовить "
            "начинку.\n"
            "У меня отварные яйца с зелёным луком.\n"
            "Для теста нам понадобится 150 мл кипятка, ставим чайник, чтобы "
            "закипел.\n"
            "В тёплом молоке разводим дрожжи и сахар.\n"
            "В отдельную миску просеиваем муку, 1 стакан, из общего количества"
            ", добавляем соль и растительное масло.\n"
            "Вливаем кипяток и тщательно перемешиваем лопаткой.\n"
            "Добавляем дрожжевую смесь, перемешиваем.\n"
            "Постепенно всыпаем всю муку.\n"
            "Тесто должно получиться мягкое и эластичное.\n"
            "Тесто прикрыть и оставить на 15 минут.\n"
            "Развесить тесто по 65 гр.\n"
            "У меня получилось 13 одинаковых кусочков.\n"
            "Можно оставить их на 10 минут, можно пропустить этот шаг, и сразу"
            " отрывать кусочки теста и раскатывать в лепёшки.\n"
            "Распределить начинку, слепить пирожки.\n"
            "Жарить в хорошо разогретом растительном масле.\n"
            "Выложить на бумажные полотенца, чтобы удалить излишки жира.\n"
            "Приятного аппетита!"
        ),
        "cooking_time": 35,
        "author": 4
    },
}


class Command(BaseCommand):
    help = (
        'Добавляет в базу тестовые рецепты. Применять после создания'
        ' хотя бы одного пользователя, импорта тегов и ингредиентов.'
    )

    def handle(self, *args, **options):
        if (
            not User.objects.exists()
            or not Ingredient.objects.exists()
            or not Tag.objects.exists()
        ):
            self.stdout.write(
                self.style.ERROR(
                    'Для добавления рецептов нужно, чтобы в базе был хотя бы '
                    'один пользователь, ингредиент и тег.')
            )
            return
        for recipe_key, recipe_data in recipes_data.items():
            recipe = Recipe.objects.create(
                name=recipe_data['name'],
                text=recipe_data['text'],
                cooking_time=recipe_data['cooking_time'],
                author_id=recipe_data['author'],
                image=recipe_data['image'],
            )
            recipe.short_link = recipe.get_or_create_short_link()
            recipe.save()
            for ingredient_data in recipe_data['ingredients']:
                try:
                    ingredient = Ingredient.objects.get(
                        id=ingredient_data['id'])
                except Ingredient.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Ингредиент с ID={ingredient_data["id"]} не найден.'))
                    return
                recipe.ingredients.add(
                    ingredient,
                    through_defaults={'amount': ingredient_data['amount']}
                )
            for tag_id in recipe_data['tags']:
                try:
                    tag = Tag.objects.get(id=tag_id)
                except Tag.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Тег с ID={tag_id} не найден.'))
                    return
                recipe.tags.add(tag)
        self.stdout.write(self.style.SUCCESS('Рецепты добавлены успешно.'))
