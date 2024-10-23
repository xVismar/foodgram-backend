from django.shortcuts import redirect
from django.conf import settings


def redirect_short_link(request, short_id):
    return redirect(settings.HOME_DOMAIN + 'recipes/' + short_id)
