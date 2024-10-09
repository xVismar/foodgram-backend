import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    """Проверка имени пользователя на соответствие шаблону."""
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            f'Использовать {username} в качестве логина запрещено!'
        )
    matching_chars = re.findall(r'^[\w.@+-]', username)
    if username and not matching_chars:
        invalid_chars = ''.join(set(matching_chars))
        raise ValidationError(
            f'Поле "username" содержит недопустимые символы: {invalid_chars}!'
        )
    return username