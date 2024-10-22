import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class BaseImportCommand(BaseCommand):

    def handle_import_result(self, success, message):
        style = self.style.SUCCESS if success else self.style.ERROR
        return self.stdout.write(style(message))

    def import_from_json(self, model, file_name):
        file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                model.objects.bulk_create(
                    [model(**item) for item in data],
                    ignore_conflicts=True
                )
                return self.handle_import_result(
                    True,
                    f'{model.__name__}s успешно добавленны. '
                    f'Количество импортированных: {len(data)}',
                )
        except IntegrityError:
            return self.handle_import_result(
                False,
                f'Такой {model.__name__} уже существует в базе.'
            )
        except FileNotFoundError:
            return self.handle_import_result(
                False, f'Файл {file_path} не найден'
            )
        except json.JSONDecodeError:
            return self.handle_import_result(
                False, 'Ошибка чтения JSON. Проверьте формат файла.'
            )
        except Exception as e:
            return self.handle_import_result(False, f'Ошибка: {e}')
