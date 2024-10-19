from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import BooleanFilter, FilterSet

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited',)

    def filter_is_in_shopping_cart(self, recipes, name, is_in_shopping_cart):
        user = self.request.user
        if user.is_authenticated and is_in_shopping_cart:
            return recipes.filter(carts__user=user)
        return recipes

    def filter_is_favorited(self, recipes, name, is_favorited):
        user = self.request.user
        if user.is_authenticated and is_favorited:
            return recipes.filter(favorites__user=user)
        return recipes


class CookingTimeFilter(admin.SimpleListFilter):
    title = _('Cooking Time (min)')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        counts = queryset.values('cooking_time').annotate(total=Count('id'))
        cooking_time_ranges = set()
        lookups = []
        for count in counts:
            cooking_time = count['cooking_time']
            total = count['total']
            if cooking_time < 30 and 'Быстро' not in cooking_time_ranges:
                lookups.append(('Быстро ({})'.format(total), 'Менее 30 минут'))
                cooking_time_ranges.add('Быстро')
            elif (
                30 <= cooking_time <= 60
                and 'Средне' not in cooking_time_ranges
            ):
                lookups.append(
                    ('Средне ({})'.format(total), 'От 30 до 60 минут')
                )
                cooking_time_ranges.add('Средне')
            elif cooking_time > 60 and 'Долго' not in cooking_time_ranges:
                lookups.append(('Долго ({})'.format(total), 'Более 60 минут'))
                cooking_time_ranges.add('Долго')

        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Быстро ({})'.format(queryset.filter(
            cooking_time__lt=30).count()
        ):
            return queryset.filter(cooking_time__lt=30)
        elif value == 'Средне ({})'.format(queryset.filter(
            cooking_time__range=[30, 60]).count()
        ):
            return queryset.filter(cooking_time__range=[30, 60])
        elif value == 'Долго ({})'.format(queryset.filter(
            cooking_time__gt=60).count()
        ):
            return queryset.filter(cooking_time__gt=60)
