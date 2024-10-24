from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import redirect


def redirect_short_link(request, short_id):
    try:
        short_id = int(short_id)
    except ValueError:
        raise ValidationError(
            f'ID "{short_id}" - некорректен. ID может быть только целым '
            'позитивным числом.'
        )
    return redirect(f'{settings.HOME_DOMAIN}recipes/{short_id}/')
