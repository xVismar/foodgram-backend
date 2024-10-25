from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect


def redirect_short_link(request, short_id):
    try:
        short_id = int(short_id)
    except ValueError:
        raise ValidationError(
            f'ID "{short_id}" - некорректен. ID может быть только целым '
            'позитивным числом'
        )
    return HttpResponseRedirect(f'/recipes/{short_id}/')
