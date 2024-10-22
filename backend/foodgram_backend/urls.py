from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


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
