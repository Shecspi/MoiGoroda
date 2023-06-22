from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy

from city.models import City, VisitedCity
from region.models import Area, Region


class Test_VisitedCity_Delete(TestCase):
    url_login = reverse_lazy('signin')
    url_success = reverse_lazy('city-all')
    user_data = {'username1': 'user1', 'password1': 'password1', 'username2': 'user2', 'password2': 'password2'}

    def setUp(self):
        self.user_1 = User.objects.create_user(username=self.user_data['username1'], password=self.user_data['password1'])
        self.user_2 = User.objects.create_user(username=self.user_data['username2'], password=self.user_data['password2'])

        area = Area.objects.create(title='Area 1')
        region = Region.objects.create(area=area, title='Region 1', type='O')
        city = City.objects.create(title='City 1', region=region, population=1000000, date_of_foundation=1900,
                                   coordinate_width=55.5, coordinate_longitude=44.4, wiki='No link')
        self.visited_city_1 = VisitedCity.objects.create(user=self.user_1, region=region, city=city, has_magnet=False,
                                                         date_of_visit='1990-08-29', rating='5')
        self.visited_city_2 = VisitedCity.objects.create(user=self.user_2, region=region, city=city, has_magnet=False,
                                                         date_of_visit='1990-08-29', rating='5')

    def test_access_not_auth_user(self):
        """
        Неавторизованные пользователи должны быть перенаправлены на страницу авторизации.
        """
        url = reverse_lazy('city-delete', kwargs={'pk': '1'})
        response = self.client.get(url, follow=True)

        self.assertRedirects(response,
                             self.url_login + f"?next={url}",
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account/signin.html')

    def test_delete_is_correct(self):
        """
        Проверка удаления записи, к которой пользователь имеет доступ.
        """
        self.client.login(username=self.user_data['username1'], password=self.user_data['password1'])
        response = self.client.post(
            reverse_lazy('city-delete', kwargs={'pk': self.visited_city_1.id}),
            follow=True
        )
        self.client.logout()

        self.assertRedirects(response, self.url_success, status_code=302)
        self.assertTemplateUsed('travel/visited_city/news__list.html')

    def test_delete_is_not_correct(self):
        """
        Проверка удаления несуществующей записи и записи, к которой у пользователя нет доступа.
        """
        self.client.login(username=self.user_data['username1'], password=self.user_data['password1'])
        # Запись другого пользователя
        response_1 = self.client.post(
            reverse_lazy('city-delete', kwargs={'pk': self.visited_city_2.id}),
            follow=True
        )
        # Несуществующая запись
        response_2 = self.client.post(
            reverse_lazy('city-delete', kwargs={'pk': '999'}),
            follow=True
        )
        self.client.logout()

        self.assertEqual(response_1.status_code, 403)
        self.assertEqual(response_2.status_code, 403)
