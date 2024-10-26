from django.shortcuts import redirect
from django.http import Http404
from recipes.models import Recipe


def redirect_short_link(request, short_id):
    return (
        redirect(f'/recipes/{short_id}/')
        if Recipe.objects.filter(id=short_id).exists()
        else Http404('Рецепт с таким ID не найден')
    )
