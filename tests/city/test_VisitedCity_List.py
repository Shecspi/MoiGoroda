from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy

from city.models import City, VisitedCity
from region.models import Area, Region


class Test_VisiitedCity_List(TestCase):
    # ToDo Проверить фильтры и сортировку
    url = reverse_lazy('city-all')
    url_region = reverse_lazy('region-selected', kwargs={'pk': '999'})
    login_url = reverse_lazy('signin')
    user_data = {'username': 'user', 'password': 'password'}

    def setUp(self) -> None:
        user = User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        area = Area.objects.create(title='Area #1')
        region = Region.objects.create(area=area, title='Region #1', type='O')
        city_1 = City.objects.create(title='City #1', region=region, population=1000000, date_of_foundation=1900,
                                     coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        city_2 = City.objects.create(title='City #2', region=region, population=1000000, date_of_foundation=1900,
                                     coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        VisitedCity.objects.create(user=user, region=region, city=city_1, has_magnet=False,
                                   date_of_visit='1990-08-29', rating='5')
        VisitedCity.objects.create(user=user, region=region, city=city_2, has_magnet=False,
                                   date_of_visit='1990-08-29', rating='5')

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
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/visited_city/news__list.html')

    def test_access_region_not_auth_user(self):
        """
        Неавторизованный пользователь должен быть перенаправлен на страницу авторизации.
        """
        url_exist = reverse_lazy('region-selected', kwargs={'pk': '1'})
        url_not_exist = reverse_lazy('region-selected', kwargs={'pk': '999'})
        response_exist = self.client.get(url_exist, follow=True)
        response_not_exist = self.client.get(url_not_exist, follow=True)

        self.assertRedirects(response_exist,
                             self.login_url + f"?next={url_exist}",
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response_exist, 'account/signin.html')
        self.assertRedirects(response_not_exist,
                             self.login_url + f"?next={url_not_exist}",
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response_not_exist, 'account/signin.html')

    def test_access_region_auth_user_is_correct(self):
        """
        Авторизованный пользователь может зайти на страницу региона, даже если у него нет посещённых городов в нём.
        """
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(reverse_lazy('region-selected', kwargs={'pk': '1'}), follow=True)
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/visited_city/news__list.html')

    def test_access_region_auth_user_is_not_correct(self):
        """
        При обращении авторизованного пользователя к несуществующему региону должна отдавать страница 404
        """
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(reverse_lazy('region-selected', kwargs={'pk': '999'}), follow=True)
        self.client.logout()

        self.assertEqual(response.status_code, 404)
