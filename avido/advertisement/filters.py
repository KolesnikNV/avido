from django_filters import rest_framework as filters

from advertisement.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Advertisement Filter Set."""

    price = filters.RangeFilter()
    city = filters.CharFilter(
        field_name="city_name__name", lookup_expr="icontains"
    )
    category = filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Advertisement
        fields = (
            "price",
            "city",
            "category",
            "name",
            "description",
        )
