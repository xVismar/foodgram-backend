
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.views.generic import RedirectView


def redirect_short_link(request, short_id):
    return redirect(reverse('recipe-detail', args=[short_id]))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path(
        'about/',
        RedirectView.as_view(url='/static/pages/about/index.html'),
        name='О проекте'
    ),
    path(
        'technologies/',
        RedirectView.as_view(url='/static/pages/technologies/index.html'),
        name='Технологии'
    ),
    path('', include('recipes.urls', namespace='recipes')),
]
