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
            existing_tags = set(Tag.objects.values_list('title', flat=True))
            new_tags = [
                Tag(**tag) for tag in tags_data
                if tag['title'] not in existing_tags
            ]
            if new_tags:
                Tag.objects.bulk_create(new_tags, ignore_conflicts=True)
                self.stdout.write(
                    self.style.SUCCESS('Теги успешно импортированы.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Новые теги не найдены. Импорт пропущен.'
                    )
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    'Ошибка при чтении JSON файла.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
