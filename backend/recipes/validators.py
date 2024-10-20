import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    """Проверка имени пользователя на соответствие шаблону."""
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            f'Использовать {username} в качестве логина запрещено!'
        )
    if not re.match(r'^[\w.@+-]+$', username):
        invalid_chars = ''.join(set(re.findall(r'[^\w.@+-]', username)))
        raise ValidationError(
            f'Поле "username" содержит недопустимые символы: {invalid_chars}!'
        )
    return username
