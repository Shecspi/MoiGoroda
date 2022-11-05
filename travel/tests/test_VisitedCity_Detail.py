from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy

from travel.models import Area, Region, City, VisitedCity


class Test_VisitedCity_Detail(TestCase):
    url_1 = reverse_lazy('city-selected', kwargs={'pk': '1'})
    url_2 = reverse_lazy('city-selected', kwargs={'pk': '2'})
    url_city_all = reverse_lazy('city-all')
    url_login = reverse_lazy('signin')

    user = {
        'username1': 'user_1', 'password1': 'password',
        'username2': 'user_2', 'password2': 'password'
    }

    def setUp(self) -> None:
        user_1 = User.objects.create_user(username=self.user['username1'], password=self.user['password1'],
                                          is_staff=True)
        user_2 = User.objects.create_user(username=self.user['username2'], password=self.user['password2'],
                                          is_staff=False)

        area = Area.objects.create(title='Area 1')
        region = Region.objects.create(area=area, title='Region 1', type='O')
        city_1 = City.objects.create(title='City 1', region=region, population=1000000, date_of_foundation=1900,
                                     coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        city_2 = City.objects.create(title='City 2', region=region, population=1000000, date_of_foundation=1900,
                                     coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        VisitedCity.objects.create(user=user_1, region=region, city=city_1, has_magnet=False,
                                                    date_of_visit='1990-08-29', rating='5')
        VisitedCity.objects.create(user=user_2, region=region, city=city_2, has_magnet=False,
                                                    date_of_visit='1990-08-29', rating='5')

    def test_access_not_auth_user(self):
        """
        Неавторизованные пользователи должны быть перенаправлены на страницу авторизации.
        """
        response = self.client.get(self.url_1, follow=True)

        self.assertRedirects(response,
                             self.url_login + f"?next={self.url_1}",
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account/signin.html')

    def test_access_auth_user_to_his_notes(self):
        """
        Авторизованный пользователь имеет доступ к своим записям.
        """
        self.client.login(username=self.user['username1'], password=self.user['password1'])
        response = self.client.get(self.url_1, follow=True)
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/visited_city/detail.html')

    def test_access_auth_user_to_not_his_notes(self):
        """
        Авторизованный пользователь при попытке просмотра чужой записи, перенаправляется в список всех городов.
        """
        self.client.login(username=self.user['username1'], password=self.user['password1'])
        response = self.client.get(self.url_2, follow=True)
        self.client.logout()

        self.assertRedirects(response,
                             self.url_city_all,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'travel/visited_city/list.html')
