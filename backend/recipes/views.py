from django.shortcuts import redirect


def redirect_short_link(request, short_id):
    return redirect('api:recipe-detail', kwargs={'pk': short_id})
