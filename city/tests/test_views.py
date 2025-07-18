import pytest
from django.test import RequestFactory
from django.core.exceptions import ImproperlyConfigured
from city.views import VisitedCityDetail
from city.dto import CityDetailsDTO
from django.http import Http404

@pytest.fixture
def fake_service(mocker):
    service = mocker.Mock()
    city = mocker.Mock()
    city.title = 'Москва'
    city.region = 'Московская область'
    city.country = 'Россия'
    dto = CityDetailsDTO(
        city=city,
        average_rating=4.5,
        popular_months=['Июнь'],
        visits=[],
        collections=[],
        number_of_visits=1,
        number_of_visits_all_users=2,
        number_of_users_who_visit_city=1,
        number_of_cities_in_country=10,
        number_of_cities_in_region=5,
        rank_in_country_by_visits=1,
        rank_in_country_by_users=1,
        rank_in_region_by_visits=1,
        rank_in_region_by_users=1,
        neighboring_cities_by_rank_in_country_by_visits=[],
        neighboring_cities_by_rank_in_country_by_users=[],
        neighboring_cities_by_rank_in_region_by_visits=[],
        neighboring_cities_by_rank_in_region_by_users=[],
    )
    service.get_city_details.return_value = dto
    return service

@pytest.fixture
def fake_service_factory(fake_service):
    return lambda request: fake_service

@pytest.fixture
def rf():
    return RequestFactory()

def test_visited_city_detail_context(rf, fake_service_factory, fake_service, mocker):
    request = rf.get('/city/1/')
    request.user = mocker.Mock()
    view = VisitedCityDetail()
    view.service_factory = fake_service_factory  # type: ignore
    mocker.patch.object(view, 'get_object', return_value=fake_service.get_city_details.return_value.city)
    view.kwargs = {'pk': 1}
    view.request = request
    view.dispatch(request, pk=1)
    fake_service.get_city_details.assert_any_call(1, request.user)

def test_visited_city_detail_improperly_configured(rf):
    request = rf.get('/city/1/')
    view = VisitedCityDetail()
    view.service_factory = None
    with pytest.raises(ImproperlyConfigured):
        view.dispatch(request, pk=1)

def test_visited_city_detail_service_raises(rf, fake_service_factory, fake_service, mocker):
    request = rf.get('/city/1/')
    request.user = mocker.Mock()
    fake_service.get_city_details.side_effect = Http404
    view = VisitedCityDetail()
    view.service_factory = fake_service_factory  # type: ignore
    mocker.patch.object(view, 'get_object', return_value=fake_service.get_city_details.return_value.city)
    view.kwargs = {'pk': 1}
    view.request = request
    try:
        view.dispatch(request, pk=1)
        assert False, "Http404 was not raised"
    except Http404:
        pass

def test_visited_city_detail_unauthenticated_user(rf, fake_service_factory, fake_service, mocker):
    request = rf.get('/city/1/')
    user = mocker.Mock()
    user.is_authenticated = False
    request.user = user
    view = VisitedCityDetail()
    view.service_factory = fake_service_factory  # type: ignore
    mocker.patch.object(view, 'get_object', return_value=fake_service.get_city_details.return_value.city)
    view.kwargs = {'pk': 1}
    view.request = request
    view.dispatch(request, pk=1)
    fake_service.get_city_details.assert_any_call(1, user)

def test_visited_city_detail_get_object_called(rf, fake_service_factory, fake_service, mocker):
    request = rf.get('/city/1/')
    request.user = mocker.Mock()
    view = VisitedCityDetail()
    view.service_factory = fake_service_factory  # type: ignore
    get_object_mock = mocker.patch.object(view, 'get_object', return_value=fake_service.get_city_details.return_value.city)
    view.kwargs = {'pk': 1}
    view.request = request
    view.dispatch(request, pk=1)
    get_object_mock.assert_called()

def test_visited_city_detail_context_extra_fields(rf, fake_service_factory, fake_service, mocker):
    request = rf.get('/city/1/')
    request.user = mocker.Mock()
    view = VisitedCityDetail()
    view.service_factory = fake_service_factory  # type: ignore
    mocker.patch.object(view, 'get_object', return_value=fake_service.get_city_details.return_value.city)
    view.kwargs = {'pk': 1}
    view.request = request
    view.dispatch(request, pk=1)
    context = view.get_context_data()
    # Проверяем, что стандартные поля есть
    assert 'page_title' in context
    assert 'page_description' in context
    assert 'city' in context
    assert 'extra_field' not in context 