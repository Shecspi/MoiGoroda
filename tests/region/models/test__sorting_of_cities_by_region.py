import pytest

from city.models import City, VisitedCity
from utils.CitiesByRegionMixin import CitiesByRegionMixin

from django.db.models import OuterRef, Exists, Subquery, DateField


@pytest.mark.django_db
def test__sorting(setup_db_for_sorting):
    mixin = CitiesByRegionMixin()
    queryset = City.objects.filter(region__id=1).annotate(
        is_visited=Exists(
            VisitedCity.objects.filter(city_id=OuterRef('pk'), user=1)
        ),
        date_of_visit=Subquery(
            VisitedCity.objects.filter(city_id=OuterRef('pk'), user=1).values('date_of_visit'),
            output_field=DateField()
        )
    )

    result_name_down = [city for city in mixin.apply_sort_to_queryset(queryset, 'name_down').values_list('title', flat=True)]
    assert result_name_down == ['Город 1', 'Город 2', 'Город 3']

    result_name_up = [city for city in mixin.apply_sort_to_queryset(queryset, 'name_up').values_list('title', flat=True)]
    assert result_name_up == ['Город 3', 'Город 2', 'Город 1']

    result_date_down = [city for city in mixin.apply_sort_to_queryset(queryset, 'date_down').values_list('title', flat=True)]
    assert result_date_down == ['Город 2', 'Город 1', 'Город 3']

    result_date_up = [city for city in mixin.apply_sort_to_queryset(queryset, 'date_up').values_list('title', flat=True)]
    assert result_date_up == ['Город 3', 'Город 1', 'Город 2']
