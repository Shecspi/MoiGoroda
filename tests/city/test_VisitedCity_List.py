from datetime import datetime
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy, reverse

from city.models import City, VisitedCity
from region.models import Area, Region


class Test_VisiitedCity_List(TestCase):
    # ToDo Проверить фильтры и сортировку
    url = reverse_lazy('city-all')
    login_url = reverse_lazy('signin')
    create_url = reverse('city-create')
    user_data = {'username': 'user', 'password': 'password'}

    def setUp(self) -> None:
        user = User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        area = Area.objects.create(title='Area #1')
        region = Region.objects.create(area=area, title='Region #1', type='O')
        city_1 = City.objects.create(title='City #1', region=region, population=1000000, date_of_foundation=1900,
                                     coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        city_2 = City.objects.create(title='City #2', region=region, population=1000000, date_of_foundation=1900,
                                     coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        VisitedCity.objects.create(user=user, region=region, city=city_1, has_magnet=True,
                                   date_of_visit=str(datetime.today().year) + '-08-29', rating='5')
        VisitedCity.objects.create(user=user, region=region, city=city_2, has_magnet=False,
                                   date_of_visit=str(datetime.today().year - 1) + '-08-29', rating='5')

    def test_access_not_auth_user(self):
        """
        Неавторизованный пользователь должен быть перенаправлен на страницу авторизации.
        """
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response,
                             self.login_url + f"?next={self.url}",
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account/signin.html')

    def test_access_auth_user(self):
        """
        Авторизованный пользователь должен иметь доступ к странице.
        """
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(self.url)
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'city/visited_cities__list.html')

        # На странице имеется 2 карточки с посещёнными городами
        assert len(source.find_all('div', {'class': 'card-visited_city'})) == 2

        # На странице должно отображаться меню с вкладками "Список" и "Карта"
        assert source.find(
            'div', {'class': 'nav flex-column nav-pills'}
        ).find(
            'button', {'class': 'nav-link active'}
        ).find(
            'i', {'class': 'fa-solid fa-list'}
        ) is not None
        assert 'Список' in source.find(
            'div', {'class': 'nav flex-column nav-pills'}
        ).find(
            'button', {'class': 'nav-link active'}
        ).text
        assert source.find(
            'div', {'class': 'nav flex-column nav-pills'}
        ).find(
            'button', {'id': 'map-tab'}
        ).find(
            'i', {'class': 'fa-solid fa-map-location-dot'}
        ) is not None
        assert 'Карта' in source.find(
            'div', {'class': 'nav flex-column nav-pills'}
        ).find(
            'button', {'id': 'map-tab'}
        ).text

        # На странице имеется кнопка "Добавить город"
        assert source.find(
            'a', {'class': 'btn', 'href': self.create_url}
        ).find(
            'i', {'class', 'fa-solid fa-city'}
        ) is not None
        assert 'Добавить город' in source.find('a', {'class': 'btn', 'href': self.create_url}).text

    def test__filter__without_magnet(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(self.url + '?filter=magnet')
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        self.client.logout()

        # На странице имеется 1 карточка с посещёнными городами с магнитом
        assert len(source.find_all('div', {'class': 'card-visited_city'})) == 1
        assert 'City #2' in source.find('div', {'class': 'card-visited_city'}).text

    def test_filter__this_year(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(self.url + '?filter=current_year')
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        self.client.logout()

        # На странице имеется 1 карточка с посещёнными городом в этом году
        assert len(source.find_all('div', {'class': 'card-visited_city'})) == 1
        assert 'City #1' in source.find('div', {'class': 'card-visited_city'}).text

    def test_filter__last_year(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(self.url + '?filter=last_year')
        source = BeautifulSoup(response.content.decode(), 'html.parser')
        self.client.logout()

        # На странице имеется 1 карточка с посещёнными городом в прошлом году
        assert len(source.find_all('div', {'class': 'card-visited_city'})) == 1
        assert 'City #2' in source.find('div', {'class': 'card-visited_city'}).text
