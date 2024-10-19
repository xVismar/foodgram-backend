
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from api.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('s/<int:short_id>/', redirect_short_link, name='short-link-redirect'),
    path(
        'about/',
        RedirectView.as_view(url='/static/pages/about/index.html'),
        name='about'
    ),
    path(
        'technologies/',
        RedirectView.as_view(url='/static/pages/technologies/index.html'),
        name='technologies'
    ),
]
