from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet, RecipeViewSet, TagViewSet, CurentUserViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('users', CurentUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:pk>/',
        RecipeViewSet.as_view({'get': 'retrieve'}),
        name='recipe-detail'
    )
]
