from django_filters import rest_framework

from items.models import Item


class ItemFilter(rest_framework.FilterSet):
    min_price = rest_framework.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = rest_framework.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Item
        fields = ['categories__name']
