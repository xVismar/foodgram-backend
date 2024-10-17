from django.contrib import admin
from django.urls import include, path

from api.views import ShortLinkRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path(
        's/<str:short_link>/',
        ShortLinkRedirectView.as_view(),
        name='short-link-redirect'
    ),
]
