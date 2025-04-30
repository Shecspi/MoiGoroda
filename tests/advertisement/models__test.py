import pytest
from colorfield.fields import ColorField
from django.db import models

from advertisement.models import LinkAdvertisement


@pytest.mark.django_db
def link_advertisement_meta__test():
    """Тестирование мета-данных модели LinkAdvertisement"""
    assert LinkAdvertisement._meta.verbose_name == 'Рекламная ссылка'
    assert LinkAdvertisement._meta.verbose_name_plural == 'Рекламные ссылки'


@pytest.mark.django_db
def parameters_of_field__title__test():
    """Тестирование параметров поля title"""
    field = LinkAdvertisement._meta.get_field('title')
    assert field.verbose_name == 'Отображаемый текст'
    assert field.help_text == 'Текст, который будет виден пользователю как подпись к ссылке'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.CharField)


@pytest.mark.django_db
def parameters_of_field__url__test():
    """Тестирование параметров поля url"""
    field = LinkAdvertisement._meta.get_field('url')
    assert field.verbose_name == 'URL ссылки'
    assert field.help_text == 'Полный адрес перехода, например: https://example.com'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.URLField)


@pytest.mark.django_db
def parameters_of_field__legal_marking__test():
    """Тестирование параметров поля legal_marking"""
    field = LinkAdvertisement._meta.get_field('legal_marking')
    assert field.verbose_name == 'Маркировка рекламы'
    assert (
        field.help_text
        == 'Текст, который будет отображаться как юридическая маркировка рекламы, например: "Реклама. ООО «Компания». ИНН 1234567890"'
    )
    assert field.blank is False
    assert isinstance(field, models.CharField)


@pytest.mark.django_db
def parameters_of_field__color__test():
    """Тестирование параметров поля color"""
    field = LinkAdvertisement._meta.get_field('color')
    assert field.verbose_name == 'Цвет ссылки'
    assert field.help_text == 'Цвет текста ссылки в формате HEX, например: #FF0000'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, ColorField)


@pytest.mark.django_db
def parameters_of_field__icon_class__test():
    """Тестирование параметров поля icon_class"""
    field = LinkAdvertisement._meta.get_field('icon_class')
    assert field.verbose_name == 'Класс FontAwesome'
    assert field.help_text == 'CSS-класс иконки FontAwesome, например: fa-solid fa-star'
    assert field.blank is False
    assert field.null is False
    assert isinstance(field, models.CharField)


@pytest.mark.django_db
def str_method__test(create_link_advertisement):
    """Тестирование метода __str__ модели"""
    ad = create_link_advertisement
    assert str(ad) == 'Test Advertisement'


@pytest.fixture
def create_link_advertisement():
    """Фикстура для создания объекта LinkAdvertisement"""
    return LinkAdvertisement.objects.create(
        title='Test Advertisement',
        url='https://example.com',
        legal_marking='Реклама. ООО «Компания». ИНН 1234567890',
        color='#FF0000',
        icon_class='fa-solid fa-star',
    )
