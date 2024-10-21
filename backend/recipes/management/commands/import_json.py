import json
import os

from django.conf import settings
from django.db import IntegrityError


def handle_import_result(self, success, message):
    style = self.style.SUCCESS if success else self.style.ERROR
    return self.stdout.write(style(message))


def import_from_json(self, model, file_name):
    file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            try:
                model.objects.bulk_create(
                    [model(**item) for item in data], ignore_conflicts=True)
                return handle_import_result(
                    self,
                    True,
                    f'{model.__name__}s успешно добавленны. '
                    f'Количество импортированных: {len(data)}',
                )
            except IntegrityError:
                return handle_import_result(
                    self,
                    False,
                    f'Такой {model.__name__} уже существует в базе.'
                )

    except FileNotFoundError:
        return handle_import_result(self, False, f'Файл {file_path} не найден')

    except json.JSONDecodeError:
        return handle_import_result(
            self, False, 'Ошибка чтения JSON. Проверьте формат файла.'
        )

    except Exception as e:
        return handle_import_result(self, False, f'Ошибка: {e}')
