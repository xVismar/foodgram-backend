from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe


def redirect_short_link(request, short_id):
    return (
        redirect(f'/recipes/{get_object_or_404(Recipe, id=short_id).id}/')
    )
