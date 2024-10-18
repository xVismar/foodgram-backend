from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

users_data = [
    {
        'username': 'johndoe879',
        'email': 'johndoe879@example.com',
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'password': 'mysecretpass123'
    },
    {
        'username': 'alicesmith023',
        'email': 'alicesmith023@example.com',
        'first_name': 'Анна',
        'last_name': 'Смирнова',
        'password': 'mysecretpass123'
    },
    {
        'username': 'bobjohnson751',
        'email': 'bobjohnson751@example.com',
        'first_name': 'Дмитрий',
        'last_name': 'Иванов',
        'password': 'mysecretpass123'
    },
    {
        'username': 'emilybrown594',
        'email': 'emilybrown594@example.com',
        'first_name': 'Екатерина',
        'last_name': 'Смирнова',
        'password': 'mysecretpass123'
    }
]


class Command(BaseCommand):
    help = 'Создает в базе тестовых пользователей.'

    def handle(self, *args, **options):
        existing_users = set(User.objects.values_list('username', flat=True))
        new_users_data = [
            user_data for user_data in users_data
            if user_data['username'] not in existing_users
        ]
        if new_users_data:
            for user_data in new_users_data:
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password=user_data['password']
                )
            self.stdout.write(
                self.style.SUCCESS('Пользователи созданы успешно.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Новые пользователи не найдены. Создание пропущено.'
                )
            )
