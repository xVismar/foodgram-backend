import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание суперпользователей с параметрами из окружения.'

    def handle(self, *args, **options):
        users_data = [
            {
                'username': os.getenv('SUPERUSER_USERNAME', 'admin'),
                'email': os.getenv('SUPERUSER_EMAIL', 'admin@example.com'),
                'first_name': os.getenv('SUPERUSER_FIRST_NAME', 'Admin'),
                'last_name': os.getenv('SUPERUSER_LAST_NAME', 'User'),
                'password': os.getenv('SUPERUSER_PASSWORD', 'adminpassword'),
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'review',
                'email': 'review@admin.ru',
                'first_name': 'Ревьюер',
                'last_name': 'Практикум',
                'password': 'review1admin',
                'is_superuser': True,
                'is_staff': True,
            },
        ]
        created_users = []
        for user_data in users_data:
            username = user_data['username']
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Пользователь {username} уже существует.'
                    )
                )
            else:
                created_users.append(User.objects.create_user(**user_data))
        if created_users:
            self.stdout.write(
                self.style.SUCCESS(
                    'СуперПользователи созданы успешно.'
                )
            )
