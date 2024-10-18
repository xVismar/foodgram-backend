
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

model_data = [
    {'model': Ingredient, 'file_name': 'ingredients.json'},
    {'model': Tag, 'file_name': 'mytags.json'}
]


class Command(BaseCommand):
    help = 'Импортирует ингредиенты и тэги из .json файлов'

    def handle(self, *args, **kwargs):
        for item in model_data:
            file_path = os.path.join(
                settings.BASE_DIR, 'data', item['file_name']
            )
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    item_data = json.load(file)
                    model = item['model']
                    new_items = [model(**item) for item in item_data]
                    model.objects.bulk_create(new_items)
                    self.stdout.write(
                        self.style.SUCCESS('Данные успешно импортированы.')
                    )
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(
                    f'Файл не найден: {file_path}')
                )
            except json.JSONDecodeError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Ошибка при чтении JSON файла {item["file_name"]}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
