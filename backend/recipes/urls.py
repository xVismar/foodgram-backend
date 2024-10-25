from django.urls import path


from recipes.views import redirect_short_link

app_name = 'recipes'

urlpatterns = [
    path('<int:short_id>/', redirect_short_link, name='short-link-redirect'),
]
