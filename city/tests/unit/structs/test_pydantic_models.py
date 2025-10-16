"""
Unit тесты для Pydantic моделей (city/structs.py).

Проверяется:
- Валидация полей Coordinates
- Валидация полей City
- Валидация SubscriptionCities
- Валидация CitiesResponse
- Сериализация и десериализация
"""

import pytest

from city.structs import City, CitiesResponse, Coordinates, SubscriptionCities


@pytest.mark.unit
class TestCoordinates:
    """Тесты для модели Coordinates."""

    def test_valid_coordinates(self) -> None:
        """Создание с валидными координатами."""
        coord = Coordinates(lat=55.75, lon=37.62)

        assert coord.lat == 55.75
        assert coord.lon == 37.62

    def test_coordinates_zero_values(self) -> None:
        """Координаты могут быть нулевыми."""
        coord = Coordinates(lat=0.0, lon=0.0)

        assert coord.lat == 0.0
        assert coord.lon == 0.0

    def test_coordinates_negative_values(self) -> None:
        """Координаты могут быть отрицательными."""
        coord = Coordinates(lat=-55.75, lon=-37.62)

        assert coord.lat == -55.75
        assert coord.lon == -37.62

    def test_coordinates_extreme_latitude_max(self) -> None:
        """Максимальная широта."""
        coord = Coordinates(lat=90.0, lon=0.0)
        assert coord.lat == 90.0

    def test_coordinates_extreme_latitude_min(self) -> None:
        """Минимальная широта."""
        coord = Coordinates(lat=-90.0, lon=0.0)
        assert coord.lat == -90.0

    def test_coordinates_extreme_longitude_max(self) -> None:
        """Максимальная долгота."""
        coord = Coordinates(lat=0.0, lon=180.0)
        assert coord.lon == 180.0

    def test_coordinates_extreme_longitude_min(self) -> None:
        """Минимальная долгота."""
        coord = Coordinates(lat=0.0, lon=-180.0)
        assert coord.lon == -180.0

    def test_coordinates_serialization(self) -> None:
        """Сериализация в словарь."""
        coord = Coordinates(lat=55.75, lon=37.62)
        data = coord.model_dump()

        assert data == {'lat': 55.75, 'lon': 37.62}

    def test_coordinates_deserialization(self) -> None:
        """Десериализация из словаря."""
        data = {'lat': 55.75, 'lon': 37.62}
        coord = Coordinates(**data)

        assert coord.lat == 55.75
        assert coord.lon == 37.62


@pytest.mark.unit
class TestCityStruct:
    """Тесты для модели City."""

    def test_valid_city(self) -> None:
        """Создание города с валидными данными."""
        city = City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))

        assert city.id == 1
        assert city.title == 'Москва'
        assert city.coordinates.lat == 55.75
        assert city.coordinates.lon == 37.62

    def test_city_with_nested_coordinates(self) -> None:
        """Создание города с вложенными координатами."""
        city = City(
            id=1,
            title='Москва',
            coordinates={'lat': 55.75, 'lon': 37.62},  # type: ignore[arg-type]
        )

        assert isinstance(city.coordinates, Coordinates)
        assert city.coordinates.lat == 55.75

    def test_city_serialization(self) -> None:
        """Сериализация города в словарь."""
        city = City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))
        data = city.model_dump()

        assert data == {'id': 1, 'title': 'Москва', 'coordinates': {'lat': 55.75, 'lon': 37.62}}

    def test_city_deserialization(self) -> None:
        """Десериализация города из словаря."""
        data = {'id': 1, 'title': 'Москва', 'coordinates': {'lat': 55.75, 'lon': 37.62}}
        city = City(**data)  # type: ignore[arg-type]

        assert city.id == 1
        assert city.title == 'Москва'
        assert isinstance(city.coordinates, Coordinates)

    def test_city_with_empty_title(self) -> None:
        """Город может быть создан с пустым названием."""
        city = City(id=1, title='', coordinates=Coordinates(lat=0.0, lon=0.0))
        assert city.title == ''


@pytest.mark.unit
class TestSubscriptionCities:
    """Тесты для модели SubscriptionCities."""

    def test_valid_subscription(self) -> None:
        """Создание подписки с валидными данными."""
        sub = SubscriptionCities(
            username='testuser',
            cities=[City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))],
        )

        assert sub.username == 'testuser'
        assert len(sub.cities) == 1
        assert sub.cities[0].title == 'Москва'

    def test_subscription_with_empty_cities(self) -> None:
        """Подписка может иметь пустой список городов."""
        sub = SubscriptionCities(username='testuser', cities=[])

        assert sub.username == 'testuser'
        assert sub.cities == []

    def test_subscription_with_multiple_cities(self) -> None:
        """Подписка с несколькими городами."""
        sub = SubscriptionCities(
            username='testuser',
            cities=[
                City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62)),
                City(id=2, title='Питер', coordinates=Coordinates(lat=59.93, lon=30.34)),
            ],
        )

        assert len(sub.cities) == 2

    def test_subscription_serialization(self) -> None:
        """Сериализация подписки."""
        sub = SubscriptionCities(
            username='testuser',
            cities=[City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))],
        )
        data = sub.model_dump()

        assert data['username'] == 'testuser'
        assert len(data['cities']) == 1
        assert data['cities'][0]['title'] == 'Москва'


@pytest.mark.unit
class TestCitiesResponse:
    """Тесты для модели CitiesResponse."""

    def test_cities_response_with_own_cities(self) -> None:
        """Ответ с собственными городами."""
        response = CitiesResponse(
            own=[City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))]
        )

        assert response.own is not None
        assert len(response.own) == 1
        assert response.subscriptions is None

    def test_cities_response_with_subscriptions(self) -> None:
        """Ответ с подписками."""
        response = CitiesResponse(
            subscriptions=[
                SubscriptionCities(
                    username='user1',
                    cities=[
                        City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))
                    ],
                )
            ]
        )

        assert response.own is None
        assert response.subscriptions is not None
        assert len(response.subscriptions) == 1

    def test_cities_response_with_both(self) -> None:
        """Ответ с собственными городами и подписками."""
        response = CitiesResponse(
            own=[City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))],
            subscriptions=[
                SubscriptionCities(
                    username='user1',
                    cities=[
                        City(id=2, title='Питер', coordinates=Coordinates(lat=59.93, lon=30.34))
                    ],
                )
            ],
        )

        assert response.own is not None
        assert response.subscriptions is not None
        assert len(response.own) == 1
        assert len(response.subscriptions) == 1

    def test_cities_response_empty(self) -> None:
        """Пустой ответ."""
        response = CitiesResponse()

        assert response.own is None
        assert response.subscriptions is None

    def test_cities_response_serialization(self) -> None:
        """Сериализация полного ответа."""
        response = CitiesResponse(
            own=[City(id=1, title='Москва', coordinates=Coordinates(lat=55.75, lon=37.62))],
            subscriptions=[
                SubscriptionCities(
                    username='user1',
                    cities=[
                        City(id=2, title='Питер', coordinates=Coordinates(lat=59.93, lon=30.34))
                    ],
                )
            ],
        )
        data = response.model_dump()

        assert 'own' in data
        assert 'subscriptions' in data
        assert isinstance(data['own'], list) and len(data['own']) == 1
        assert isinstance(data['subscriptions'], list) and len(data['subscriptions']) == 1

    def test_cities_response_with_empty_lists(self) -> None:
        """Ответ с пустыми списками."""
        response = CitiesResponse(own=[], subscriptions=[])

        assert response.own == []
        assert response.subscriptions == []
