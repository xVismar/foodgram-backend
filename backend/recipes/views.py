from django.shortcuts import redirect


def redirect_short_link(request, short_id):
    return redirect('api:recipe-detail', pk=short_id)
