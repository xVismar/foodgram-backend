from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess


class Command(BaseCommand):
    help = (
        'Добавляет теги, ингредиенты, суперпользователя, '
        'в базу данных проекта.'
    )

    def handle(self, *args, **kwargs):
        commands = [
            'import_data',
            'create_superuser',
            'create_users',
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
