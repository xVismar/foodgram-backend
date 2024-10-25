from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path(
        'about',
        TemplateView.as_view(template_name='/static/pages/about/index.html'),
        name='О проекте'
    ),
    path(
        'technologies',
        TemplateView.as_view(
            template_name='/static/pages/technologies/index.html'
        ),
        name='Технологии'
    ),
    path('s/', include('recipes.urls', namespace='recipes')),
]
