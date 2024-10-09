import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импортирует теги из файла data/mytags.json'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'mytags.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tags_data = json.load(file)
            Tag.objects.bulk_create(
                [Tag(**tag) for tag in tags_data],
                ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS('Теги успешно импортированы.')
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    'Ошибка при чтении JSON файла.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
