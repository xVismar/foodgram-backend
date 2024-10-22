from django.shortcuts import redirect


def redirect_short_link(request, short_id):
    return redirect('api:recipes-detail', args=[short_id])
