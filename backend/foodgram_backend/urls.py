from django.contrib import admin
from django.urls import include, path

from api.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('s/<str:short_id>/', redirect_short_link, name='redirect_short_link'),
]
