"""
Integration тесты для валидации формы VisitedCity_Create_Form (city/forms.py).

Тестируется:
- Метод clean_city() - проверка дубликатов
- Метод clean_rating() - валидация диапазона
- Логика __init__() - формирование queryset
- Обработка ошибок
"""

from datetime import date
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from city.forms import VisitedCity_Create_Form
from city.models import City, VisitedCity
from country.models import Country, Location, PartOfTheWorld
from region.models import Area, Region, RegionType


@pytest.fixture
def setup_data(django_user_model: Any) -> dict[str, Any]:
    """Создание базовых данных для тестов."""
    part = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part)
    
    country_ru = Country.objects.create(
        name='Россия', code='RU', fullname='Российская Федерация', location=location
    )
    country_kz = Country.objects.create(
        name='Казахстан', code='KZ', fullname='Республика Казахстан', location=location
    )
    
    region_type = RegionType.objects.create(title='Область')
    area_ru = Area.objects.create(country=country_ru, title='Центральный РУ')
    area_kz = Area.objects.create(country=country_kz, title='Центральный КЗ')
    
    region_ru = Region.objects.create(
        title='Московская', country=country_ru, type=region_type,
        area=area_ru, iso3166='MOS', full_name='Московская область'
    )
    region_kz = Region.objects.create(
        title='Алматинская', country=country_kz, type=region_type,
        area=area_kz, iso3166='ALM', full_name='Алматинская область'
    )
    
    moscow = City.objects.create(
        title='Москва', country=country_ru, region=region_ru,
        coordinate_width=55.75, coordinate_longitude=37.62
    )
    spb = City.objects.create(
        title='Санкт-Петербург', country=country_ru, region=region_ru,
        coordinate_width=59.93, coordinate_longitude=30.34
    )
    almaty = City.objects.create(
        title='Алматы', country=country_kz, region=region_kz,
        coordinate_width=43.25, coordinate_longitude=76.95
    )
    
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    
    return {
        'user': user,
        'country_ru': country_ru,
        'country_kz': country_kz,
        'region_ru': region_ru,
        'region_kz': region_kz,
        'moscow': moscow,
        'spb': spb,
        'almaty': almaty,
    }


@pytest.mark.django_db
@pytest.mark.integration
class TestCleanRatingValidation:
    """Тесты метода clean_rating()."""

    def test_clean_rating_valid_values(self, setup_data: dict[str, Any]) -> None:
        """Все значения от 1 до 5 валидны."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        for rating in ['1', '2', '3', '4', '5']:
            form = VisitedCity_Create_Form(request=request)
            form.cleaned_data = {'rating': rating}
            
            result = form.clean_rating()
            
            assert result == int(rating)

    def test_clean_rating_invalid_too_low(self, setup_data: dict[str, Any]) -> None:
        """Значение 0 невалидно."""
        user = setup_data['user']
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.cleaned_data = {'rating': '0'}
        
        with pytest.raises(ValidationError) as exc_info:
            form.clean_rating()
        
        assert 'Оценка должна быть в диапазоне от 1 до 5' in str(exc_info.value)

    def test_clean_rating_invalid_too_high(self, setup_data: dict[str, Any]) -> None:
        """Значение 6 невалидно."""
        user = setup_data['user']
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.cleaned_data = {'rating': '6'}
        
        with pytest.raises(ValidationError) as exc_info:
            form.clean_rating()
        
        assert 'Оценка должна быть в диапазоне от 1 до 5' in str(exc_info.value)

    def test_clean_rating_invalid_negative(self, setup_data: dict[str, Any]) -> None:
        """Отрицательное значение невалидно."""
        user = setup_data['user']
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.cleaned_data = {'rating': '-1'}
        
        with pytest.raises(ValidationError):
            form.clean_rating()


@pytest.mark.django_db
@pytest.mark.integration
class TestCleanCityDuplicateValidation:
    """Тесты метода clean_city() - проверка дубликатов."""

    def test_clean_city_allows_first_visit(self, setup_data: dict[str, Any]) -> None:
        """Первое посещение города разрешено."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.instance = VisitedCity()  # Новая запись
        form.cleaned_data = {
            'city': moscow,
            'date_of_visit': date(2024, 1, 1)
        }
        
        result = form.clean_city()
        
        assert result == moscow  # Не должно быть ошибки

    def test_clean_city_forbids_duplicate_with_same_date(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Дубликат с той же датой запрещён."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        
        # Создаём первое посещение
        VisitedCity.objects.create(
            user=user, city=moscow,
            date_of_visit=date(2024, 1, 15),
            rating=5, is_first_visit=True
        )
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        # Пытаемся создать дубликат
        form = VisitedCity_Create_Form(request=request)
        form.instance = VisitedCity()
        form.cleaned_data = {
            'city': moscow,
            'date_of_visit': date(2024, 1, 15)  # Та же дата
        }
        
        with pytest.raises(ValidationError) as exc_info:
            form.clean_city()
        
        assert 'уже был отмечен Вами как посещённый' in str(exc_info.value)

    def test_clean_city_allows_different_date(self, setup_data: dict[str, Any]) -> None:
        """Разрешено посещение того же города с другой датой."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        
        VisitedCity.objects.create(
            user=user, city=moscow,
            date_of_visit=date(2024, 1, 15),
            rating=5, is_first_visit=True
        )
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.instance = VisitedCity()
        form.cleaned_data = {
            'city': moscow,
            'date_of_visit': date(2024, 2, 15)  # Другая дата
        }
        
        result = form.clean_city()
        
        assert result == moscow  # Не должно быть ошибки

    def test_clean_city_forbids_duplicate_without_date(
        self, setup_data: dict[str, Any]
    ) -> None:
        """Дубликат без даты запрещён."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        
        VisitedCity.objects.create(
            user=user, city=moscow,
            date_of_visit=None,
            rating=5, is_first_visit=True
        )
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.instance = VisitedCity()
        form.cleaned_data = {
            'city': moscow,
            'date_of_visit': None
        }
        
        with pytest.raises(ValidationError) as exc_info:
            form.clean_city()
        
        assert 'без указания даты' in str(exc_info.value)

    def test_clean_city_allows_edit_own_record(self, setup_data: dict[str, Any]) -> None:
        """При редактировании своя запись не считается дубликатом."""
        user = setup_data['user']
        moscow = setup_data['moscow']
        
        visit = VisitedCity.objects.create(
            user=user, city=moscow,
            date_of_visit=date(2024, 1, 15),
            rating=5, is_first_visit=True
        )
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user
        
        form = VisitedCity_Create_Form(request=request)
        form.instance = visit  # Редактируем существующую запись
        form.cleaned_data = {
            'city': moscow,
            'date_of_visit': date(2024, 1, 15)  # Та же дата
        }
        
        result = form.clean_city()
        
        assert result == moscow  # Не должно быть ошибки

    def test_clean_city_different_users_no_conflict(
        self, setup_data: dict[str, Any], django_user_model: Any
    ) -> None:
        """Разные пользователи могут посещать один город в одну дату."""
        user1 = setup_data['user']
        user2 = django_user_model.objects.create_user(username='user2', password='pass')
        moscow = setup_data['moscow']
        
        # User1 посещает
        VisitedCity.objects.create(
            user=user1, city=moscow,
            date_of_visit=date(2024, 1, 15),
            rating=5, is_first_visit=True
        )
        
        from unittest.mock import Mock
        request = Mock()
        request.user = user2
        
        # User2 может посетить в ту же дату
        form = VisitedCity_Create_Form(request=request)
        form.instance = VisitedCity()
        form.cleaned_data = {
            'city': moscow,
            'date_of_visit': date(2024, 1, 15)  # Та же дата
        }
        
        result = form.clean_city()
        
        assert result == moscow  # Нет конфликта


@pytest.mark.django_db
@pytest.mark.integration
class TestFormInitQuerysetLogic:
    """Тесты логики __init__() - формирование queryset."""

    def test_init_with_country_filters_regions(self, setup_data: dict[str, Any]) -> None:
        """При указании страны фильтруются регионы этой страны."""
        country_kz = setup_data['country_kz']
        
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request, initial={'country': country_kz.id})
        
        # Проверяем что queryset для region отфильтрован
        region_queryset = form.fields['region'].queryset
        regions_list = list(region_queryset)
        
        # Все регионы должны быть из Казахстана
        for region in regions_list:
            assert region.country == country_kz

    def test_init_with_region_in_data_filters_cities(
        self, setup_data: dict[str, Any]
    ) -> None:
        """При указании региона в data фильтруются города."""
        region_kz = setup_data['region_kz']
        almaty = setup_data['almaty']
        
        from unittest.mock import Mock
        request = Mock()
        
        data = {'region': str(region_kz.id)}
        form = VisitedCity_Create_Form(data=data, request=request)
        
        # Queryset для city должен быть отфильтрован
        city_queryset = form.fields['city'].queryset
        cities_list = list(city_queryset)
        
        # Должны быть только города из этого региона
        assert almaty in cities_list

    def test_init_with_initial_city_populates_queryset(
        self, setup_data: dict[str, Any]
    ) -> None:
        """При указании города через initial заполняется queryset."""
        moscow = setup_data['moscow']
        region_ru = setup_data['region_ru']
        
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request, initial={'city': moscow.id})
        
        # Должен быть установлен регион
        assert form.initial.get('region') == region_ru.id
        
        # Queryset городов должен быть отфильтрован по региону
        city_queryset = form.fields['city'].queryset
        assert moscow in list(city_queryset)

    def test_init_without_errors_empties_city_queryset(
        self, setup_data: dict[str, Any]
    ) -> None:
        """По умолчанию queryset городов пустой до выбора региона."""
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request)
        
        # Без ошибок форма должна иметь пустой queryset городов
        city_queryset = form.fields['city'].queryset
        assert city_queryset.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestFormFieldsConfiguration:
    """Тесты настройки полей формы."""

    def test_rating_field_has_correct_choices(self, setup_data: dict[str, Any]) -> None:
        """Поле rating имеет выбор от 1 до 5."""
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request)
        
        choices = form.fields['rating'].choices
        assert len(choices) == 5
        assert ('1', '1') in choices
        assert ('5', '5') in choices

    def test_impression_field_not_required(self, setup_data: dict[str, Any]) -> None:
        """Поле impression не обязательно."""
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request)
        
        assert form.fields['impression'].required is False

    def test_country_field_required(self, setup_data: dict[str, Any]) -> None:
        """Поле country обязательно."""
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request)
        
        assert form.fields['country'].required is True

    def test_region_field_not_required(self, setup_data: dict[str, Any]) -> None:
        """Поле region не обязательно."""
        from unittest.mock import Mock
        request = Mock()
        
        form = VisitedCity_Create_Form(request=request)
        
        assert form.fields['region'].required is False


@pytest.mark.django_db
@pytest.mark.integration
class TestFormErrorHandling:
    """Тесты обработки ошибок."""

    def test_form_handles_nonexistent_city(self, setup_data: dict[str, Any]) -> None:
        """Обработка несуществующего города при initial."""
        from unittest.mock import Mock
        request = Mock()
        
        # Не должно быть ошибки, даже если город не существует
        form = VisitedCity_Create_Form(request=request, initial={'city': 99999})
        
        # Форма должна создаться
        assert form is not None

