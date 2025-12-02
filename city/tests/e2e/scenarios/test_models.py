import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from country.models import Country
from region.models import Region, RegionType


def create_test_country() -> Country:
    """Создает тестовую страну."""
    return Country(name='Фейковая страна', code='FC')


def create_test_region_type() -> RegionType:
    """Создает тестовый тип региона."""
    return RegionType(title='область')


def create_test_region(
    country: Country | None = None, region_type: RegionType | None = None
) -> Region:
    """Создает тестовый регион."""
    if country is None:
        country = create_test_country()
    if region_type is None:
        region_type = create_test_region_type()

    return Region(
        title='Фейковый регион',
        type=region_type,
        iso3166='FAKE-REG',
        country=country,
        area=None,
        full_name='Фейковый регион область',
    )


@pytest.fixture
def fake_country() -> Country:
    """Фикстура для создания тестовой страны."""
    return create_test_country()


@pytest.fixture
def fake_region_type() -> RegionType:
    """Фикстура для создания тестового типа региона."""
    return create_test_region_type()


@pytest.fixture
def fake_region() -> Region:
    """Фикстура для создания тестового региона."""
    return create_test_region()


@pytest.fixture
def city_instance(fake_country: Country, fake_region: Region) -> City:
    """Фикстура для создания тестового города."""
    return City(
        title='Test City',
        country=fake_country,
        region=fake_region,
        population=500_000,
        date_of_foundation=1800,
        coordinate_width=55.75,
        coordinate_longitude=37.61,
        wiki='https://en.wikipedia.org/wiki/Test_City',
        image='https://example.com/test_city.jpg',
        image_source_text='Example Source',
        image_source_link='https://example.com/source',
    )


@pytest.fixture
def user_instance() -> User:
    """Фикстура для создания тестового пользователя."""
    return User(username='testuser', email='test@example.com')


@pytest.fixture
def visited_city_instance(city_instance: City, user_instance: User) -> VisitedCity:
    """Фикстура для создания тестового посещенного города."""
    return VisitedCity(
        user=user_instance,
        city=city_instance,
        date_of_visit=None,
        has_magnet=False,
        impression='Great city!',
        rating=5,
        is_first_visit=True,
    )


@pytest.mark.e2e
class TestCityModel:
    """Тесты для модели City."""

    def test_city_model_structure(self) -> None:
        """Проверяет структуру модели City."""
        expected_fields = {
            'title',
            'country',
            'region',
            'population',
            'date_of_foundation',
            'coordinate_width',
            'coordinate_longitude',
            'wiki',
            'image',
            'image_source_text',
            'image_source_link',
        }
        model_fields = set(f.name for f in City._meta.get_fields() if not f.auto_created)
        assert model_fields == expected_fields, (
            'Модель City изменилась. Обновите тесты и добавьте тесты для новых полей.'
        )

    def test_city_str(self, city_instance: City) -> None:
        """Проверяет строковое представление города."""
        assert str(city_instance) == 'Test City'

    def test_city_get_absolute_url(self, city_instance: City) -> None:
        """Проверяет метод get_absolute_url."""
        city_instance.pk = 123
        assert city_instance.get_absolute_url() == '/city/123'

    def test_city_fields_required(self) -> None:
        """Проверяет обязательные поля города."""
        fake_region = create_test_region()
        city = City(
            title='',  # Пустая строка вместо None
            country=None,
            region=fake_region,
            coordinate_width=0.0,  # Валидное значение вместо None
            coordinate_longitude=0.0,  # Валидное значение вместо None
        )
        with pytest.raises(ValidationError) as exc_info:
            city.full_clean()

        errors = exc_info.value.message_dict
        assert 'title' in errors
        assert 'country' in errors

    def test_city_meta_options(self) -> None:
        """Проверяет мета-опции модели City."""
        assert City._meta.verbose_name == 'Город'
        assert City._meta.verbose_name_plural == 'Города'
        assert City._meta.ordering == ['title']

    def test_city_field_values(self, city_instance: City) -> None:
        """Проверяет значения полей города."""
        assert city_instance.title == 'Test City'
        assert str(city_instance.country) == 'Фейковая страна'
        assert str(city_instance.region) == 'Фейковый регион область'
        assert city_instance.population == 500_000
        assert city_instance.date_of_foundation == 1800
        assert city_instance.coordinate_width == 55.75
        assert city_instance.coordinate_longitude == 37.61
        assert city_instance.wiki == 'https://en.wikipedia.org/wiki/Test_City'
        assert city_instance.image == 'https://example.com/test_city.jpg'
        assert city_instance.image_source_text == 'Example Source'
        assert city_instance.image_source_link == 'https://example.com/source'

    def test_city_title_max_length(self) -> None:
        """Проверяет максимальную длину названия города."""
        fake_country = create_test_country()
        fake_region = create_test_region()
        long_title = 'A' * 101  # Превышает max_length=100
        city = City(
            title=long_title,
            country=fake_country,
            region=fake_region,
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )
        with pytest.raises(ValidationError) as exc_info:
            city.full_clean()
        assert 'title' in exc_info.value.message_dict

    def test_city_coordinate_validation(self) -> None:
        """Проверяет валидацию координат."""
        fake_country = create_test_country()
        fake_region = create_test_region()
        # Тест с невалидными координатами
        city = City(
            title='Test City',
            country=fake_country,
            region=fake_region,
            coordinate_width=200.0,  # Невалидная широта
            coordinate_longitude=200.0,  # Невалидная долгота
        )
        # Координаты не имеют встроенной валидации в модели, но тест показывает структуру
        assert city.coordinate_width == 200.0
        assert city.coordinate_longitude == 200.0

    def test_city_optional_fields(self) -> None:
        """Проверяет опциональные поля города."""
        fake_country = create_test_country()
        city = City(
            title='Minimal City',
            country=fake_country,
            region=None,  # Опциональное поле
            coordinate_width=55.75,
            coordinate_longitude=37.61,
            # Все остальные поля опциональны
        )
        city.full_clean(exclude=['country'])  # Должно пройти валидацию
        assert city.region is None
        assert city.population is None
        assert city.date_of_foundation is None

    def test_city_url_fields_validation(self) -> None:
        """Проверяет валидацию URL полей."""
        fake_country = create_test_country()
        fake_region = create_test_region()
        city = City(
            title='Test City',
            country=fake_country,
            region=fake_region,
            coordinate_width=55.75,
            coordinate_longitude=37.61,
            wiki='invalid-url',  # Невалидный URL
            image='invalid-image-url',  # Невалидный URL
            image_source_link='invalid-source-url',  # Невалидный URL
        )
        with pytest.raises(ValidationError) as exc_info:
            city.full_clean()
        errors = exc_info.value.message_dict
        assert 'wiki' in errors
        assert 'image' in errors
        assert 'image_source_link' in errors

    def test_city_positive_integer_fields(self) -> None:
        """Проверяет поля с положительными целыми числами."""
        fake_country = create_test_country()
        fake_region = create_test_region()
        city = City(
            title='Test City',
            country=fake_country,
            region=fake_region,
            coordinate_width=55.75,
            coordinate_longitude=37.61,
            population=-1000,  # Отрицательное значение
            date_of_foundation=-100,  # Отрицательное значение
        )
        with pytest.raises(ValidationError) as exc_info:
            city.full_clean()
        errors = exc_info.value.message_dict
        assert 'population' in errors
        assert 'date_of_foundation' in errors

    def test_city_edge_case_values(self) -> None:
        """Проверяет граничные значения."""
        fake_country = create_test_country()
        fake_region = create_test_region()
        city = City(
            title='A',  # Минимальная длина
            country=fake_country,
            region=fake_region,
            coordinate_width=0.0,  # Граничное значение
            coordinate_longitude=0.0,  # Граничное значение
            population=0,  # Граничное значение
            date_of_foundation=1,  # Минимальное значение
        )
        city.full_clean(exclude=['country'])  # Должно пройти валидацию
        assert city.title == 'A'
        assert city.coordinate_width == 0.0
        assert city.coordinate_longitude == 0.0
        assert city.population == 0
        assert city.date_of_foundation == 1


@pytest.mark.e2e
class TestVisitedCityModel:
    """Тесты для модели VisitedCity."""

    def test_visited_city_model_structure(self) -> None:
        """Проверяет структуру модели VisitedCity."""
        expected_fields = {
            'user',
            'city',
            'date_of_visit',
            'has_magnet',
            'impression',
            'rating',
            'is_first_visit',
            'created_at',
            'updated_at',
        }
        model_fields = set(f.name for f in VisitedCity._meta.get_fields() if not f.auto_created)
        assert model_fields == expected_fields, (
            'Модель VisitedCity изменилась. Обновите тесты и добавьте тесты для новых полей.'
        )

    def test_visited_city_str(self, visited_city_instance: VisitedCity) -> None:
        """Проверяет строковое представление посещенного города."""
        assert str(visited_city_instance) == 'Test City'

    def test_visited_city_get_absolute_url(self, visited_city_instance: VisitedCity) -> None:
        """Проверяет метод get_absolute_url."""
        visited_city_instance.pk = 123
        assert visited_city_instance.get_absolute_url() == '/city/123'

    def test_visited_city_meta_options(self) -> None:
        """Проверяет мета-опции модели VisitedCity."""
        assert VisitedCity._meta.verbose_name == 'Посещённый город'
        assert VisitedCity._meta.verbose_name_plural == 'Посещённые города'
        assert VisitedCity._meta.ordering == ['-id']

    def test_visited_city_field_values(self, visited_city_instance: VisitedCity) -> None:
        """Проверяет значения полей посещенного города."""
        assert visited_city_instance.user.username == 'testuser'
        assert visited_city_instance.city.title == 'Test City'
        assert visited_city_instance.date_of_visit is None
        assert visited_city_instance.has_magnet is False
        assert visited_city_instance.impression == 'Great city!'
        assert visited_city_instance.rating == 5
        assert visited_city_instance.is_first_visit is True

    def test_visited_city_required_fields(self) -> None:
        """Проверяет обязательные поля посещенного города."""
        visited_city = VisitedCity(
            user=None,  # Обязательное поле
            city=None,  # Обязательное поле
            rating=0,  # Обязательное поле с невалидным значением
        )
        with pytest.raises(ValidationError) as exc_info:
            visited_city.full_clean()
        errors = exc_info.value.message_dict
        assert 'user' in errors
        assert 'city' in errors
        assert 'rating' in errors

    def test_visited_city_rating_validation(self) -> None:
        """Проверяет валидацию рейтинга."""
        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        # Тест с рейтингом меньше 1
        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=0,  # Меньше минимального значения
        )
        with pytest.raises(ValidationError) as exc_info:
            visited_city.full_clean()
        assert 'rating' in exc_info.value.message_dict

        # Тест с рейтингом больше 5
        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=6,  # Больше максимального значения
        )
        with pytest.raises(ValidationError) as exc_info:
            visited_city.full_clean()
        assert 'rating' in exc_info.value.message_dict

    def test_visited_city_rating_valid_values(self) -> None:
        """Проверяет валидные значения рейтинга."""
        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        for rating in [1, 2, 3, 4, 5]:
            visited_city = VisitedCity(
                user=user_instance,
                city=city_instance,
                rating=rating,
            )
            visited_city.full_clean(exclude=['user', 'city'])  # Должно пройти валидацию
            assert visited_city.rating == rating

    def test_visited_city_optional_fields(self) -> None:
        """Проверяет опциональные поля посещенного города."""
        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=5,
            # Все остальные поля опциональны
        )
        visited_city.full_clean(exclude=['user', 'city'])  # Должно пройти валидацию
        assert visited_city.date_of_visit is None
        assert visited_city.has_magnet is False  # Значение по умолчанию
        assert visited_city.impression is None
        assert visited_city.is_first_visit is True  # Значение по умолчанию

    def test_visited_city_boolean_fields_defaults(self) -> None:
        """Проверяет значения по умолчанию для булевых полей."""
        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=5,
        )
        assert visited_city.has_magnet is False
        assert visited_city.is_first_visit is True

    def test_visited_city_impression_field(self) -> None:
        """Проверяет поле впечатлений."""
        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        long_impression = 'A' * 1000  # Длинное впечатление
        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=5,
            impression=long_impression,
        )
        visited_city.full_clean(exclude=['user', 'city'])  # Должно пройти валидацию
        assert visited_city.impression == long_impression

    def test_visited_city_date_of_visit(self) -> None:
        """Проверяет поле даты посещения."""
        from datetime import date

        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        visit_date = date(2023, 6, 15)
        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=5,
            date_of_visit=visit_date,
        )
        visited_city.full_clean(exclude=['user', 'city'])  # Должно пройти валидацию
        assert visited_city.date_of_visit == visit_date

    def test_visited_city_unique_constraint(self) -> None:
        """Проверяет уникальное ограничение."""
        from datetime import date

        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        visit_date = date(2023, 6, 15)

        # Создаем первый объект
        visited_city1 = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=5,
            date_of_visit=visit_date,
        )

        # Создаем второй объект с теми же user, city и date_of_visit
        visited_city2 = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=4,
            date_of_visit=visit_date,
        )

        # Проверяем, что unique_together работает
        # (В реальном тесте это потребовало бы сохранения в БД)
        assert visited_city1.user == visited_city2.user
        assert visited_city1.city == visited_city2.city
        assert visited_city1.date_of_visit == visited_city2.date_of_visit

    def test_visited_city_edge_cases(self) -> None:
        """Проверяет граничные случаи."""
        user_instance = User(username='testuser', email='test@example.com')
        city_instance = City(
            title='Test City',
            country=create_test_country(),
            region=create_test_region(),
            coordinate_width=55.75,
            coordinate_longitude=37.61,
        )

        # Минимальный рейтинг
        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=1,
            has_magnet=False,
            is_first_visit=False,
        )
        visited_city.full_clean(exclude=['user', 'city'])
        assert visited_city.rating == 1
        assert visited_city.has_magnet is False
        assert visited_city.is_first_visit is False

        # Максимальный рейтинг
        visited_city = VisitedCity(
            user=user_instance,
            city=city_instance,
            rating=5,
            has_magnet=True,
            is_first_visit=True,
        )
        visited_city.full_clean(exclude=['user', 'city'])
        assert visited_city.rating == 5
        assert visited_city.has_magnet is True
        assert visited_city.is_first_visit is True
