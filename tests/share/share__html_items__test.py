import pytest

from bs4 import BeautifulSoup
from django.urls import reverse

from tests.share.conftest import create_permissions_in_db


@pytest.mark.django_db
def test__dashboard_page_has_title(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})

    title = content.find('h1', {'id': 'block-page_header'})
    assert title
    assert 'Статистика пользователя username1' in title.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_tab_panel(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})

    assert tab_panel
    assert len(tab_panel.find('div')) == 3


@pytest.mark.django_db
def test__dashboard_page_has_active_dashboard_button(setup, client):
    """
    При открытии страницы дашбоард соответствующая кнопка должна быть выделена и неактивна.
    """
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    btn_dashboard = tab_panel.find('button', {'id': 'tab-button-dashboard', 'class': 'btn-primary'})

    assert btn_dashboard
    assert btn_dashboard.has_attr('disabled')
    assert 'Общая информация' in btn_dashboard.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_active_city_map_button(setup, client):
    """
    При открытии страницы с картой городов соответствующая кнопка должна быть выделена и неактивна.
    """
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1, 'requested_page': 'city_map'}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    btn_dashboard = tab_panel.find('button', {'id': 'tab-button-city_map', 'class': 'btn-primary'})

    assert btn_dashboard
    assert btn_dashboard.has_attr('disabled')
    assert 'Карта посещённых городов' in btn_dashboard.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_active_region_map_button(setup, client):
    """
    При открытии страницы с картой регионов соответствующая кнопка должна быть выделена и неактивна.
    """
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1, 'requested_page': 'region_map'}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    btn_dashboard = tab_panel.find(
        'button', {'id': 'tab-button-region_map', 'class': 'btn-primary'}
    )

    assert btn_dashboard
    assert btn_dashboard.has_attr('disabled')
    assert 'Карта посещённых регионов' in btn_dashboard.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_city_map_button(setup, client):
    """
    В случае, если запрещено отображать информацию про посещённые регионы,
    то в таб-панели должна быть неактивная кнопка.
    """
    create_permissions_in_db(1, (True, True, False, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    btn_city_map = tab_panel.find(
        'button', {'id': 'tab-button-city_map', 'class': 'btn-outline-primary'}
    )

    assert btn_city_map
    assert btn_city_map.has_attr('disabled')
    assert 'Карта посещённых городов' in btn_city_map.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_city_map_link(setup, client):
    """
    В случае, если разрешено отображать информацию про посещённые города,
    то в таб-панели должна быть активная ссылка.
    """
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    link_city_map = tab_panel.find('a', {'id': 'tab-link-city_map', 'class': 'btn-outline-primary'})

    assert link_city_map
    assert 'Карта посещённых городов' in link_city_map.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_region_map_button(setup, client):
    """
    В случае, если запрещено отображать информацию про посещённые регионы,
    то в таб-панели должна быть неактивная кнопка.
    """
    create_permissions_in_db(1, (True, True, True, False))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    btn_region_map = tab_panel.find(
        'button', {'id': 'tab-button-region_map', 'class': 'btn-outline-primary'}
    )

    assert btn_region_map
    assert btn_region_map.has_attr('disabled')
    assert 'Карта посещённых регионов' in btn_region_map.get_text()


@pytest.mark.django_db
def test__dashboard_page_has_region_map_link(setup, client):
    """
    В случае, если разрешено отображать информацию про посещённые регионы,
    то в таб-панели должна быть активная ссылка.
    """
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    tab_panel = content.find('div', {'id': 'tab-panel'})
    link_region_map = tab_panel.find(
        'a', {'id': 'tab-link-region_map', 'class': 'btn-outline-primary'}
    )

    assert link_region_map
    assert 'Карта посещённых регионов' in link_region_map.get_text()


@pytest.mark.django_db
def test__city_map_has_map(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1, 'requested_page': 'city_map'}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    div_map = content.find('div', {'id': 'map'})

    assert div_map


@pytest.mark.django_db
def test__dashboard_has_cards__row_city_cards(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    row_city_stats = content.find('div', {'id': 'row-city-stats'})
    card_number_of_visited_cities = row_city_stats.find(
        'div', {'id': 'card_number_of_visited_cities'}
    )
    card_number_of_not_visited_cities = row_city_stats.find(
        'div', {'id': 'card_number_of_not_visited_cities'}
    )
    card_number_of_visited_cities_current_year = row_city_stats.find(
        'div', {'id': 'card_number_of_visited_cities_current_year'}
    )
    card_number_of_visited_cities_prev_year = row_city_stats.find(
        'div', {'id': 'card_number_of_visited_cities_prev_year'}
    )

    assert row_city_stats
    assert card_number_of_visited_cities
    assert card_number_of_not_visited_cities
    assert card_number_of_visited_cities_current_year
    assert card_number_of_visited_cities_prev_year


@pytest.mark.django_db
def test__dashboard_has_cards__row_pie_charts(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    row_pie_charts = content.find('div', {'id': 'row-pie-charts'})
    chart_number_of_cities = row_pie_charts.find('div', {'id': 'chart_number_of_cities'})
    chart_number_of_cities_current_and_prev_years = row_pie_charts.find(
        'div', {'id': 'chart_number_of_cities_current_and_prev_years'}
    )
    chart_number_of_regions = row_pie_charts.find('div', {'id': 'chart_number_of_regions'})
    chart__number_of_finished_regions = row_pie_charts.find(
        'div', {'id': 'chart_number_of_finished_regions'}
    )

    assert row_pie_charts
    assert chart_number_of_cities
    assert chart_number_of_cities_current_and_prev_years
    assert chart_number_of_regions
    assert chart__number_of_finished_regions


@pytest.mark.django_db
def test__dashboard_has_cards__row_region_cards(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    row_region_stats = content.find('div', {'id': 'row-region-stats'})
    number_of_visited_regions = row_region_stats.find('div', {'id': 'number_of_visited_regions'})
    number_of_not_visited_regions = row_region_stats.find(
        'div', {'id': 'number_of_not_visited_regions'}
    )
    number_of_finished_regions = row_region_stats.find('div', {'id': 'number_of_finished_regions'})
    number_of_half_finished_regions = row_region_stats.find(
        'div', {'id': 'number_of_half_finished_regions'}
    )

    assert row_region_stats
    assert number_of_visited_regions
    assert number_of_not_visited_regions
    assert number_of_finished_regions
    assert number_of_half_finished_regions


@pytest.mark.django_db
def test__dashboard_has_cards__row_bar_charts(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    row_bar_charts = content.find('div', {'id': 'row-bar-charts'})
    chart_cities_by_month = row_bar_charts.find('div', {'id': 'chart_cities_by_month'})
    chart_cities_by_year = row_bar_charts.find('div', {'id': 'chart_cities_by_year'})

    assert row_bar_charts
    assert chart_cities_by_month
    assert chart_cities_by_year


@pytest.mark.django_db
def test__dashboard_has_cards__row_list_cards(setup, client):
    create_permissions_in_db(1, (True, True, True, True))
    client.login(username='username1', password='password')
    response = client.get(reverse('share', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    content = source.find('div', {'id': 'section-content'})
    list_cards = content.find('div', {'id': 'list_cards'})
    list_last_visited_cities = list_cards.find('div', {'id': 'list_last_visited_cities'})
    list_most_popular_regions = list_cards.find('div', {'id': 'list_most_popular_regions'})
    list_areas = list_cards.find('div', {'id': 'list_areas'})

    assert list_cards
    assert list_last_visited_cities
    assert list_most_popular_regions
    assert list_areas
