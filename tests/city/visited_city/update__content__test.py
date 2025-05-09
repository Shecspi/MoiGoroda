import pytest
from bs4 import BeautifulSoup
from django.urls import reverse


@pytest.mark.django_db
def test__content__header(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    page_header = content.find('h1', {'id': 'section-page_header'})

    assert 'city/city_create.html' in (t.name for t in response.templates)
    assert content
    assert page_header
    assert 'Редактирование города' in page_header.get_text()


@pytest.mark.django_db
def test__form_region(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    form = content.find('form')
    block = form.find('div', {'id': 'div_id_region'})
    label = block.find('label')
    select = block.find('select', {'id': 'id_region'})
    hint = block.find('div', {'id': 'hint_id_region'})

    assert form
    assert block
    assert 'Регион*' in label.get_text()
    assert select
    assert hint


@pytest.mark.django_db
def test__form_city(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    form = content.find('form')
    block = form.find('div', {'id': 'div_id_city'})
    label = block.find('label')
    select = block.find('select', {'id': 'id_city'})
    hint = block.find('div', {'id': 'hint_id_city'})

    assert form
    assert block
    assert 'Город*' in label.get_text()
    assert select
    assert hint


@pytest.mark.django_db
def test__form_date_of_visit(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    form = content.find('form')
    block = form.find('div', {'id': 'div_id_date_of_visit'})
    label = block.find('label')
    input_text = form.find('input', {'type': 'date', 'id': 'id_date_of_visit'})
    hint = form.find('div', {'id': 'hint_id_date_of_visit'})

    assert form
    assert block
    assert 'Дата посещения' in label.get_text()
    assert input_text
    assert hint


@pytest.mark.django_db
def test__form_has_magnet(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    form = content.find('form')
    block = form.find('div', {'id': 'div_id_has_magnet'})
    label = block.find('label')
    input_checkbox = block.find('input', {'type': 'checkbox', 'id': 'id_has_magnet'})
    hint = block.find('div', {'id': 'hint_id_has_magnet'})

    assert form
    assert block
    assert 'Наличие сувенира из города' in label.get_text()
    assert input_checkbox
    assert hint


@pytest.mark.django_db
def test__form_rating(setup, client):
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

    assert form
    assert block
    assert 'Оценка города*' in label.get_text()
    assert input_radio_1
    assert '1' in label_1.get_text()
    assert input_radio_2
    assert '2' in label_2.get_text()
    assert input_radio_3
    assert '3' in label_3.get_text()
    assert input_radio_4
    assert '4' in label_4.get_text()
    assert input_radio_5
    assert '5' in label_5.get_text()
    assert hint


@pytest.mark.django_db
def test__form_impression(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    form = content.find('form')
    block = form.find('div', {'id': 'div_id_impression'})
    label = block.find('label')
    textarea = block.find('textarea', {'id': 'id_impression'})

    assert form
    assert block
    assert 'Впечатления о городе' in label.get_text()
    assert textarea


@pytest.mark.django_db
def test__form_button_submit(setup, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    form = content.find('form')
    button = form.find('input', {'type': 'submit', 'id': 'submit-id-save', 'value': 'Сохранить'})

    assert form
    assert button
