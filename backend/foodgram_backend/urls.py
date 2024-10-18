from django.contrib import admin
from django.urls import include, path

from api.views import redirect_short_link, AboutPageView, TechnologiesPageView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path(
        's/<str:short_link>/',
        redirect_short_link,
        name='short-link-redirect'
    ),
    path(
        'about/',
        AboutPageView.as_view(),
        name='about'
    ),
    path(
        'technologies/',
        TechnologiesPageView.as_view(),
        name='technologies'
    ),
]
