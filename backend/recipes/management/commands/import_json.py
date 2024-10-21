import json
import os

from django.conf import settings
from django.db import IntegrityError


def import_from_json(model, file_name):
    file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            objects_to_create = [model(**item) for item in data]
            try:
                model.objects.bulk_create(objects_to_create)
                return (
                    True,
                    f'{model.__name__}s успешно импортированы. '
                    f'Количество импортированных: {len(objects_to_create)}'
                )
            except IntegrityError:
                return False, f'Такой {model.__name__} уже существует в базе.'
    except FileNotFoundError:
        return False, f'Файл {file_path} не найден'
    except json.JSONDecodeError:
        return False, 'Ошибка чтения JSON. Проверьте формат файла.'
    except Exception as e:
        return False, f'Ошибка: {e}'
