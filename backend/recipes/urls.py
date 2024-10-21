from django.shortcuts import redirect
from django.urls import path, reverse


from api.views import RecipeViewSet

app_name = 'recipes'


def redirect_short_link(request, short_id):
    return redirect(reverse('recipes:recipe-detail', args=[short_id]))


urlpatterns = [
    path(
        'recipes/<int:pk>/',
        RecipeViewSet.as_view({'get': 'retrieve'}),
        name='recipe-detail'
    ),
    path('s/<int:short_id>/', redirect_short_link, name='short-link-redirect'),
]
