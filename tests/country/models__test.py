"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User
from django.db import models
from pytest_django.fixtures import django_user_model

from city.models import City
from country.models import Country, Location, PartOfTheWorld, VisitedCountry


@pytest.mark.django_db
def test__can_create_model_visited_country_instance_test():
    assert VisitedCountry()


@pytest.mark.django_db
def test__model_visited_country_has_valid_verbose_name():
    assert VisitedCountry._meta.verbose_name == 'Посещенная страна'
    assert VisitedCountry._meta.verbose_name_plural == 'Посещенные страны'


@pytest.mark.django_db
def test__model_visited_country_has_a_field_location():
    field = VisitedCountry._meta.get_field('country')

    assert field.verbose_name == 'Страна'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), Country)


@pytest.mark.django_db
def test__model_visited_country_has_a_field_location():
    field = VisitedCountry._meta.get_field('user')

    assert field.verbose_name == 'Пользователь'
    assert field.blank is False
    assert field.null is False
    assert field.remote_field.on_delete == models.CASCADE
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), User)


@pytest.mark.django_db
def test__model_visited_country_has_a_field_name():
    field = VisitedCountry._meta.get_field('added_at')

    assert field.verbose_name == 'Дата добавления'
    assert field.auto_now_add is True
    assert isinstance(field, models.DateTimeField)


@pytest.mark.django_db
def test__model_visited_country_returns_correct_str_representation(django_user_model):
    country_name = 'Восточная Европа'
    country = Country.objects.create(name=country_name)
    user = django_user_model.objects.create_user(username='username', password='password')
    visited_country = VisitedCountry.objects.create(country=country, user=user)

    assert country_name == str(visited_country)


@pytest.mark.django_db
def test__can_create_model_part_of_the_world_instance_test():
    assert PartOfTheWorld()


@pytest.mark.django_db
def test__model_part_of_the_world_has_valid_verbose_name():
    assert PartOfTheWorld._meta.verbose_name == 'Часть света'
    assert PartOfTheWorld._meta.verbose_name_plural == 'Части света'


@pytest.mark.django_db
def test__model_part_of_the_world_has_a_field_name():
    field = PartOfTheWorld._meta.get_field('name')

    assert field.verbose_name == 'Название'
    assert field.max_length == 20
    assert field.unique is True
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.CharField)


@pytest.mark.django_db
def test__model_part_of_the_world_returns_correct_str_representation():
    part_name = 'Европа'
    part = PartOfTheWorld.objects.create(name=part_name)

    assert part_name == str(part)


@pytest.mark.django_db
def test__can_create_model_location_instance_test():
    assert Location()


@pytest.mark.django_db
def test__model_location_has_valid_verbose_name():
    assert Location._meta.verbose_name == 'Расположение'
    assert Location._meta.verbose_name_plural == 'Расположения'


@pytest.mark.django_db
def test__model_location_has_a_field_name():
    field = Location._meta.get_field('name')
    assert field.verbose_name == 'Название'
    assert field.max_length == 50
    assert field.unique is True
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.CharField)


@pytest.mark.django_db
def test__model_location_has_a_field_location():
    field = Location._meta.get_field('part_of_the_world')
    assert field.verbose_name == 'Часть света'
    assert field.blank is True
    assert field.null is True
    assert field.remote_field.on_delete == models.SET_NULL
    assert isinstance(field, models.ForeignKey)
    assert isinstance(field.remote_field.model(), PartOfTheWorld)


@pytest.mark.django_db
def test__model_location_returns_correct_str_representation():
    location_name = 'Западная Европа'
    part = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name=location_name, part_of_the_world=part)

    assert location_name == str(location)


@pytest.mark.django_db
def test__can_create_model_country_instance_test():
    assert Country()


@pytest.mark.django_db
def test__model_country_has_valid_verbose_name():
    assert Country._meta.verbose_name == 'Страна'
    assert Country._meta.verbose_name_plural == 'Страны'


@pytest.mark.django_db
def test__model_country_has_a_field_name():
    assert Country._meta.get_field('name').verbose_name == 'Название'
    assert Country._meta.get_field('name').max_length == 255
    assert Country._meta.get_field('name').unique is True
    assert Country._meta.get_field('name').blank is False
    assert Country._meta.get_field('name').null is False
    assert isinstance(Country._meta.get_field('name'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_fullname():
    assert Country._meta.get_field('fullname').verbose_name == 'Полное название'
    assert Country._meta.get_field('fullname').max_length == 255
    assert Country._meta.get_field('fullname').unique is True
    assert Country._meta.get_field('fullname').blank is True
    assert Country._meta.get_field('fullname').null is True
    assert isinstance(Country._meta.get_field('fullname'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_english_name():
    assert Country._meta.get_field('english_name').verbose_name == 'Название на-английском языке'
    assert Country._meta.get_field('english_name').max_length == 255
    assert Country._meta.get_field('english_name').unique is False
    assert Country._meta.get_field('english_name').blank is True
    assert Country._meta.get_field('english_name').null is True
    assert isinstance(Country._meta.get_field('english_name'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_english_fullname():
    assert (
        Country._meta.get_field('english_fullname').verbose_name
        == 'Полное название на-английском языке'
    )
    assert Country._meta.get_field('english_fullname').max_length == 255
    assert Country._meta.get_field('english_fullname').unique is False
    assert Country._meta.get_field('english_fullname').blank is True
    assert Country._meta.get_field('english_fullname').null is True
    assert isinstance(Country._meta.get_field('english_fullname'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_iso3166_1_alpha2():
    assert (
        Country._meta.get_field('iso3166_1_alpha2').verbose_name == 'Двухбуквенный код ISO 3166-1'
    )
    assert Country._meta.get_field('iso3166_1_alpha2').max_length == 2
    assert Country._meta.get_field('iso3166_1_alpha2').unique is True
    assert Country._meta.get_field('iso3166_1_alpha2').blank is True
    assert Country._meta.get_field('iso3166_1_alpha2').null is True
    assert isinstance(Country._meta.get_field('iso3166_1_alpha2'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_iso3166_1_alpha3():
    assert (
        Country._meta.get_field('iso3166_1_alpha3').verbose_name == 'Трёхбуквенный код ISO 3166-1'
    )
    assert Country._meta.get_field('iso3166_1_alpha3').max_length == 3
    assert Country._meta.get_field('iso3166_1_alpha3').unique is True
    assert Country._meta.get_field('iso3166_1_alpha3').blank is True
    assert Country._meta.get_field('iso3166_1_alpha3').null is True
    assert isinstance(Country._meta.get_field('iso3166_1_alpha3'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_iso3166_1_numeric():
    assert Country._meta.get_field('iso3166_1_numeric').verbose_name == 'Цифровой код ISO 3166-1'
    assert Country._meta.get_field('iso3166_1_numeric').max_length == 3
    assert Country._meta.get_field('iso3166_1_numeric').unique is True
    assert Country._meta.get_field('iso3166_1_numeric').blank is True
    assert Country._meta.get_field('iso3166_1_numeric').null is True
    assert isinstance(Country._meta.get_field('iso3166_1_numeric'), models.CharField)


@pytest.mark.django_db
def test__model_country_has_a_field_capital():
    assert Country._meta.get_field('capital').verbose_name == 'Столица'
    assert Country._meta.get_field('capital').unique is True
    assert Country._meta.get_field('capital').blank is True
    assert Country._meta.get_field('capital').null is True
    assert Country._meta.get_field('capital').remote_field.on_delete == models.SET_NULL
    assert isinstance(Country._meta.get_field('capital'), models.OneToOneField)
    assert isinstance(Country._meta.get_field('capital').remote_field.model(), City)


@pytest.mark.django_db
def test__model_country_has_a_field_location():
    assert Country._meta.get_field('location').verbose_name == 'Расположение'
    assert Country._meta.get_field('location').unique is False
    assert Country._meta.get_field('location').blank is True
    assert Country._meta.get_field('location').null is True
    assert Country._meta.get_field('location').remote_field.on_delete == models.SET_NULL
    assert isinstance(Country._meta.get_field('location'), models.ForeignKey)
    assert isinstance(Country._meta.get_field('location').remote_field.model(), Location)


@pytest.mark.django_db
def test__model_country_returns_correct_str_representation():
    country_name = 'Восточная Европа'
    country = Country.objects.create(name=country_name)

    assert country_name == str(country)
