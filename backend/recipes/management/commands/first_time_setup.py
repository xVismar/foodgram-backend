from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path
import subprocess
import shutil


class Command(BaseCommand):
    help = (
        'Добавляет теги, ингредиенты, суперпользователя, тестовых'
        'пользователей и тестовые рецецпты в в базу данных проекта.'
    )

    base_dir = Path.cwd()
    source_dir = base_dir / 'data' / 'media_data'
    destination_dir = base_dir / 'media'
    folders_to_copy = ['recipes']
    for folder in folders_to_copy:
        src_folder = source_dir / folder
        dest_folder = destination_dir / folder
        shutil.copytree(src_folder, dest_folder, dirs_exist_ok=True)
    print('Данные из backend/data успешно скопированы в backend/media/')

    def handle(self, *args, **kwargs):
        commands = [
            'import_ingredients',
            'import_tags',
            'create_superuser',
            'create_users',
            'create_recipes',
        ]
        for command in commands:
            try:
                self.stdout.write(self.style.NOTICE(f'Запускаю {command}...'))
                call_command(command)
                self.stdout.write(
                    self.style.SUCCESS(f'{command} выполнен успешно.')
                )
            except subprocess.CalledProcessError as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при выполнении {command}: {e}.')
                )
