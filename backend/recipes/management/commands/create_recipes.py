from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()

recipes_data = {
    "recipe_one": {
        "id": 1,
        "ingredients": [
            {"id": 2180, "amount": 150},
            {"id": 591, "amount": 300},
            {"id": 1546, "amount": 15},
            {"id": 1419, "amount": 15},
            {"id": 1684, "amount": 1.25},
            {"id": 1669, "amount": 1.5},
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
        "author": 1,
        # "short_link": "fp9bxYSq"
    },
    "recipe_two": {
        "id": 2,
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
        "author": 2,
        # "short_link": "fp9bxdsQ"
    },
    "recipe_three": {
        "id": 3,
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
        "author": 3,
        # "short_link": "fp41xYSq"
    },
    "recipe_four": {
        "id": 4,
        "ingredients": [
            {"id": 1081, "amount": 320},
            {"id": 2180, "amount": 2},
            {"id": 886, "amount": 100},
            {"id": 2055, "amount": 30},
            {"id": 1240, "amount": 200},
            {"id": 280, "amount": 400},
            {"id": 1341, "amount": 200},
            {"id": 79, "amount": 200}
        ],
        "tags": [2],
        "image": "recipes/recipe_four.jpg",
        "name": "Рецепт пасты болоньезе",
        "text": (
            "Если делаете пасту сами, то для начала замешиваем тесто.\n"
            "Просеиваем 2 стакана муки, в углубление добавляем два яйца и"
            "замешиваем.\n"
            "Ни соли, ничего другого не надо.\n"
            "Максимум, если у вас получилось сухое тесто и оно крошится - "
            "добавьте чуть-чуть теплой воды.\n"
            "Замесили тесто, накрыли пленкой и отложили минут на 30.\n"
            "В это время занимаемся фаршем.\n"
            "Мелко порезали лук и чеснок.\n"
            "Обжариваем на сковородке до золотистого цвета.\n"
            "Затем добавляем фарш и тушим минут 10.\n"
            "А сами нарезаем болгарский перец кубиками.\n"
            "Так же в болоньезе идет томатная паста: можно взять готовую, а "
            "можно самим закинуть в блендер помидоры, базилик, перемолоть до "
            "однородного состояния и вот вам готова томатная паста.\n"
            "Фарш мы 10 минут потушили, добавляем порезанный перчик и еще "
            "тушим 5 минут.\n"
            "Затем выливаем томатную пасту, солим, перчим и тушим на медленном"
            " огне под крышкой минут 15 до готовности.\n"
            "В это время раскатываем наше тесто тонким слоем и нарезаем на "
            "узенькие полоски.\n"
            "Чуть-чуть обваливаем в муке, чтобы полоски не слипались.\n"
            "И можно их оставить сушиться на досочке (так сказать, заготовить "
            "впрок), а можно прямо сразу бросить в кипящую подсоленную воду.\n"
            "Варится домашняя паста гораздо быстрее магазинной.\n"
            "Буквально минута и все готово.\n"
            "Выкладываем пасту на тарелку.\n"
            "Сверху наш фарш в томатном соусе.\n"
            "Посыпаем натертым сыром.\n"
            "Добавляем базилик и паста Болоньезе готова."
        ),
        "cooking_time": 30,
        "author": 1,
    },
    "recipe_five": {
        "id": 5,
        "ingredients": [
            {"id": 252, "amount": 1500},
            {"id": 556, "amount": 700},
            {"id": 1419, "amount": 100},
            {"id": 886, "amount": 150},
            {"id": 1567, "amount": 150},
            {"id": 524, "amount": 250},
            {"id": 1684, "amount": 5},
            {"id": 1853, "amount": 15},
            {"id": 1378, "amount": 5},
            {"id": 609, "amount": 90},
            {"id": 1269, "amount": 100}
        ],
        "tags": [2],
        "image": "recipes/recipe_five.jpg",
        "name": (
            "Густой украинский борщ, с квашеной капустой по-семейному рецепту"
        ),
        "text": (
            "Нарежьте картофель средним кубиком, лук мелко, морковь и свёклу "
            "натрите на крупную терку.\n"
            "В кипящую воду добавьте картофель, доведите до кипения.\n"
            "После закипания снимите пенку, приправьте солью.\n"
            "Варите  картофель15 минут.\n"
            "На сковороду налейте масло, добавьте лук, морковь, свёклу "
            "пассируйте овощи 5 минут.\n"
            "К овощам добавьте томатную пасту, приправу и кипяток, тушите "
            "закрыв крышкой 5 минут.\n"
            "В воду с готовым картофелем добавьте зажарку, лавровый лист, "
            "перец, варите 3 минуты.\n"
            "Затем добавьте хорошо отжатую квашеную капусту, варите от 5 до "
            "10 минут до готовности капусты.\n"
            "Приятного аппетита."
        ),
        "cooking_time": 30,
        "author": 3,
    },
    "recipe_six": {
        "id": 6,
        "ingredients": [
            {"id": 1568, "amount": 300},
            {"id": 1749, "amount": 80},
            {"id": 2055, "amount": 15},
            {"id": 899, "amount": 50},
            {"id": 1684, "amount": 1},
            {"id": 1235, "amount": 1}
        ],
        "tags": [5],
        "image": "recipes/recipe_six.jpg",
        "name": "Салат из свеклы, сыра и чеснока",
        "text": (
            "Чистим свеклу, натираем на крупной тёрке.\n"
            "Сыр натираем на крупной тёрке.\n"
            "Чеснок на мелкой тёрке или через чеснокодавку.\n"
            "Добавляем майонез, соль, черный молотый перец и перемешиваем.\n"
            "Оставьте салат в холодильнике минут на 20, чтобы он пропитался. "
            "(хотя можно кушать и сразу)."
        ),
        "cooking_time": 5,
        "author": 4,
    },
    "recipe_seven": {
        "id": 7,
        "ingredients": [
            {"id": 1162, "amount": 15},
            {"id": 1852, "amount": 125},
            {"id": 553, "amount": 10},
            {"id": 1250, "amount": 2.5},
            {"id": 43, "amount": 250},
            {"id": 1100, "amount": 50},
            {"id": 30, "amount": 1.3},
            {"id": 1546, "amount": 10},
            {"id": 680, "amount": 2.5},
            {"id": 1684, "amount": 1},
            {"id": 1235, "amount": 1}
        ],
        "tags": [2],
        "image": "recipes/recipe_seven.jpg",
        "name": "Соус «currywurst» для сосисок и колбасок гриль",
        "text": (
            "В разогретый сотейник влить оливковое масло, внести томатную "
            "пасту, перемешивая,  прожарить 2-3 минуты.\n"
            "Нагрев ниже среднего.\n"
            "Добавить карри, кориандр и кайенский перец.\n"
            "Перемешивая продолжать обжарку.\n"
            "Влить апельсиновый сок и хорошо смешать до равномерной массы.\n"
            "Добавить мясной бульон и снова перемешать.\n"
            "Нагрев ниже среднего.\n"
            "Закинуть 2 целые звездочки аниса.\n"
            "Варить 2 минуты.\n"
            "Добавить по вкусу соль и перец.\n"
            "Перемешать.\n"
            "Всыпать сахарный песок или положить чайную ложку мёда, снизив "
            "температуру до 40С.\n"
            "Удалить звёздочки.\n"
            "Перемешать и проверить на вкус.\n"
            "Соус Currywurst  готов.\n"
            "Приятного аппетита!"
        ),
        "cooking_time": 38,
        "author": 1,
    }
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
                id=recipe_data['id'],
                name=recipe_data['name'],
                text=recipe_data['text'],
                cooking_time=recipe_data['cooking_time'],
                author_id=recipe_data['author'],
                image=recipe_data['image'],
                short_link=None
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
