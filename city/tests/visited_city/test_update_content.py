"""
Тесты для проверки контента страницы обновления и валидации формы.

Проверяется:
- Корректность отображения формы и всех полей
- Валидация данных формы
- Граничные значения
- Обработка ошибок валидации
- Предзаполнение формы существующими данными
"""

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse
from city.models import VisitedCity, City
from region.models import Region


class TestUpdateFormContent:
    """Тесты содержимого формы редактирования."""

    @pytest.mark.django_db
    def test_page_header(self, setup, client):
        """Страница должна содержать правильный заголовок."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        page_header = content.find('h1', {'id': 'section-page_header'})

        assert 'city/city_create.html' in (t.name for t in response.templates)
        assert content is not None
        assert page_header is not None
        assert 'Редактирование города' in page_header.get_text()

    @pytest.mark.django_db
    def test_form_country_field(self, setup, client):
        """Форма должна содержать поле для выбора страны."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        
        country_select = source.find('select', {'id': 'id_country'})
        assert country_select is not None

    @pytest.mark.django_db
    def test_form_region_field(self, setup, client):
        """Форма должна содержать поле для выбора региона."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        block = form.find('div', {'id': 'div_id_region'})
        label = block.find('label')
        select = block.find('select', {'id': 'id_region'})
        hint = block.find('div', {'id': 'hint_id_region'})

        assert form is not None
        assert block is not None
        assert 'Регион' in label.get_text()
        assert select is not None
        assert hint is not None

    @pytest.mark.django_db
    def test_form_city_field(self, setup, client):
        """Форма должна содержать поле для выбора города."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        block = form.find('div', {'id': 'div_id_city'})
        label = block.find('label')
        select = block.find('select', {'id': 'id_city'})
        hint = block.find('div', {'id': 'hint_id_city'})

        assert form is not None
        assert block is not None
        assert 'Город' in label.get_text()
        assert select is not None
        assert hint is not None

    @pytest.mark.django_db
    def test_form_date_of_visit_field(self, setup, client):
        """Форма должна содержать поле для даты посещения."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        block = form.find('div', {'id': 'div_id_date_of_visit'})
        label = block.find('label')
        input_date = form.find('input', {'type': 'date', 'id': 'id_date_of_visit'})
        hint = form.find('div', {'id': 'hint_id_date_of_visit'})

        assert form is not None
        assert block is not None
        assert 'Дата посещения' in label.get_text()
        assert input_date is not None
        assert hint is not None

    @pytest.mark.django_db
    def test_form_has_magnet_field(self, setup, client):
        """Форма должна содержать поле для отметки наличия сувенира."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        block = form.find('div', {'id': 'div_id_has_magnet'})
        label = block.find('label')
        input_checkbox = block.find('input', {'type': 'checkbox', 'id': 'id_has_magnet'})
        hint = block.find('div', {'id': 'hint_id_has_magnet'})

        assert form is not None
        assert block is not None
        assert 'Наличие сувенира из города' in label.get_text()
        assert input_checkbox is not None
        assert hint is not None

    @pytest.mark.django_db
    def test_form_rating_field(self, setup, client):
        """Форма должна содержать поле для оценки города."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        block = form.find('div', {'id': 'div_id_rating'})
        label = block.find('label')
        input_radio_1 = block.find('input', {'type': 'radio', 'id': 'id_rating_0'})
        label_1 = block.find('label', {'for': 'id_rating_0'})
        input_radio_2 = block.find('input', {'type': 'radio', 'id': 'id_rating_1'})
        label_2 = block.find('label', {'for': 'id_rating_1'})
        input_radio_3 = block.find('input', {'type': 'radio', 'id': 'id_rating_2'})
        label_3 = block.find('label', {'for': 'id_rating_2'})
        input_radio_4 = block.find('input', {'type': 'radio', 'id': 'id_rating_3'})
        label_4 = block.find('label', {'for': 'id_rating_3'})
        input_radio_5 = block.find('input', {'type': 'radio', 'id': 'id_rating_4'})
        label_5 = block.find('label', {'for': 'id_rating_4'})
        hint = block.find('div', {'id': 'hint_id_rating'})

        assert form is not None
        assert block is not None
        assert 'Оценка города' in label.get_text()
        assert input_radio_1 is not None
        assert '1' in label_1.get_text()
        assert input_radio_2 is not None
        assert '2' in label_2.get_text()
        assert input_radio_3 is not None
        assert '3' in label_3.get_text()
        assert input_radio_4 is not None
        assert '4' in label_4.get_text()
        assert input_radio_5 is not None
        assert '5' in label_5.get_text()
        assert hint is not None

    @pytest.mark.django_db
    def test_form_impression_field(self, setup, client):
        """Форма должна содержать поле для впечатлений."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        block = form.find('div', {'id': 'div_id_impression'})
        label = block.find('label')
        textarea = block.find('textarea', {'id': 'id_impression'})

        assert form is not None
        assert block is not None
        assert 'Впечатления о городе' in label.get_text()
        assert textarea is not None

    @pytest.mark.django_db
    def test_form_submit_button(self, setup, client):
        """Форма должна содержать кнопку отправки."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        content = source.find('div', {'id': 'section-content'})
        form = content.find('form')
        button = form.find('input', {'type': 'submit', 'id': 'submit-id-save', 'value': 'Сохранить'})

        assert form is not None
        assert button is not None


class TestUpdateFormValidation:
    """Тесты валидации формы обновления."""

    @pytest.mark.django_db
    def test_update_with_valid_data(self, setup, client):
        """Обновление с валидными данными должно быть успешным."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'date_of_visit': '2023-05-15',
                'has_magnet': True,
                'rating': 4,
                'impression': 'Great city!'
            }
        )
        
        assert response.status_code == 302
        updated = VisitedCity.objects.get(pk=1)
        assert updated.rating == 4
        assert updated.has_magnet is True

    @pytest.mark.django_db
    def test_update_with_missing_required_city(self, setup, client):
        """Обновление без указания города должно возвращать ошибку."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'rating': 4,
            }
        )
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    @pytest.mark.django_db
    def test_update_with_missing_required_rating(self, setup, client):
        """Обновление без указания рейтинга должно возвращать ошибку."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
            }
        )
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    @pytest.mark.django_db
    def test_update_rating_boundary_values(self, setup, client):
        """Тестирование граничных значений рейтинга."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        # Минимальное значение
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'rating': 1,
            }
        )
        assert response.status_code == 302
        assert VisitedCity.objects.get(pk=1).rating == 1
        
        # Максимальное значение
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'rating': 5,
            }
        )
        assert response.status_code == 302
        assert VisitedCity.objects.get(pk=1).rating == 5

    @pytest.mark.django_db
    def test_update_with_optional_date_of_visit(self, setup, client):
        """Обновление без даты посещения должно быть успешным (поле опциональное)."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'rating': 4,
                'date_of_visit': '',
            }
        )
        
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_update_with_optional_impression(self, setup, client):
        """Обновление без впечатлений должно быть успешным (поле опциональное)."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'rating': 4,
                'impression': '',
            }
        )
        
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_update_has_magnet_unchecked(self, setup, client):
        """Тест обновления с неотмеченным чекбоксом has_magnet."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        
        response = client.post(
            reverse('city-update', kwargs={'pk': 1}),
            data={
                'city': visited_city.city.id,
                'country': visited_city.city.country.id,
                'region': visited_city.city.region.id,
                'rating': 4,
                # has_magnet не передаем - должно быть False
            }
        )
        
        assert response.status_code == 302
        assert VisitedCity.objects.get(pk=1).has_magnet is False


class TestUpdateFormPrefill:
    """Тесты предзаполнения формы существующими данными."""

    @pytest.mark.django_db
    def test_form_prefilled_with_existing_data(self, setup, client):
        """Форма должна быть предзаполнена существующими данными."""
        client.login(username='username1', password='password')
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        
        visited_city = VisitedCity.objects.get(pk=1)
        form = response.context['form']
        
        assert form.initial['city'] == visited_city.city.id
        assert form.initial['country'] == visited_city.city.country.id

    @pytest.mark.django_db
    def test_form_shows_current_rating(self, setup, client):
        """Форма должна показывать текущий рейтинг."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        
        assert response.context['form'].instance.rating == visited_city.rating

    @pytest.mark.django_db
    def test_form_shows_current_has_magnet(self, setup, client):
        """Форма должна показывать текущее значение has_magnet."""
        client.login(username='username1', password='password')
        visited_city = VisitedCity.objects.get(pk=1)
        response = client.get(reverse('city-update', kwargs={'pk': 1}))
        
        assert response.context['form'].instance.has_magnet == visited_city.has_magnet
