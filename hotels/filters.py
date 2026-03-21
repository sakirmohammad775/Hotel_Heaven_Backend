from django_filters.rest_framework import FilterSet
from hotels.models import Hotel


class HotelFilter(FilterSet):
    class Meta:
        model = Hotel
        fields = {
            'category_id': ['exact'],
            'price': ['gt', 'lt']
        }