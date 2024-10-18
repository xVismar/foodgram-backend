import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из файла data/ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ingredients_data = json.load(file)
            existing_ingredients = set(Ingredient.objects.values_list(
                'name', flat=True
            ))
            new_ingredients = [
                Ingredient(**ingredient) for ingredient in ingredients_data
                if ingredient['name'] not in existing_ingredients
            ]
            if new_ingredients:
                Ingredient.objects.bulk_create(
                    new_ingredients,
                    ignore_conflicts=True
                )
                self.stdout.write(
                    self.style.SUCCESS('Ингредиенты успешно импортированы.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Новые ингредиенты не найдены. Импорт пропущен.'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    'Ошибка при чтении JSON файла. Проверьте формат.'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
