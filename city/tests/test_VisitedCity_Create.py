from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy

from city.forms import VisitedCity_Create_Form
from city.models import Area, Region, City, VisitedCity


class Test_VisitedCity_Create(TestCase):
    # ToDO Не хватает тестирования работы формы
    url_create = reverse_lazy('city-create')
    url_list = reverse_lazy('city-all')
    url_login = reverse_lazy('signin')
    user_data = {'username1': 'user1', 'password1': 'password', 'username2': 'user2', 'password2': 'password'}

    def setUp(self):
        user_1 = User.objects.create_user(username=self.user_data['username1'], password=self.user_data['password1'])
        user_2 = User.objects.create_user(username=self.user_data['username2'], password=self.user_data['password2'])

        area = Area.objects.create(title='Area 1')
        region = Region.objects.create(area=area, title='Region 1', type='O')
        city = City.objects.create(title='City 1', region=region, population=1000000, date_of_foundation=1900,
                                   coordinate_width=55.5, coordinate_longitude=44.4, wiki='There is a link')
        VisitedCity.objects.create(user=user_1, region=region, city=city, has_magnet=False,
                                   date_of_visit='1990-08-29', rating='5')
        VisitedCity.objects.create(user=user_2, region=region, city=city, has_magnet=False,
                                   date_of_visit='1990-08-29', rating='5')

    def test_access_not_auth_user(self):
        """
        Неавторизованные пользователи должны быть перенаправлены на страницу авторизации.
        """
        url_update = reverse_lazy('city-update', kwargs={'pk': '1'})
        response_create = self.client.get(self.url_create, follow=True)
        response_update = self.client.get(url_update, follow=True)

        self.assertRedirects(response_create,
                             self.url_login + f"?next={self.url_create}",
                             status_code=302,
                             target_status_code=200)
        self.assertRedirects(response_update,
                             self.url_login + f"?next={url_update}",
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response_create, 'account/signin.html')

    def test_access_auth_user(self):
        """
        Авторизованный пользователь должен иметь доступ к странице.
        """
        self.client.login(username=self.user_data['username1'], password=self.user_data['password1'])
        response_create = self.client.get(self.url_create)
        response_update = self.client.get(reverse_lazy('city-update', kwargs={'pk': '1'}))
        self.client.logout()

        self.assertEqual(response_create.status_code, 200)
        self.assertEqual(response_update.status_code, 200)
        self.assertTemplateUsed(response_create, 'travel/visited_city/create.html')
        self.assertTemplateUsed(response_update, 'travel/visited_city/create.html')

    def test_access_to_not_his_cities(self):
        """
        Редактировать можно только свои и сцществующие записи.
        """
        self.client.login(username=self.user_data['username1'], password=self.user_data['password1'])
        response_update_1 = self.client.get(reverse_lazy('city-update', kwargs={'pk': '2'}), follow=True)
        response_update_2 = self.client.get(reverse_lazy('city-update', kwargs={'pk': '999'}), follow=True)
        self.client.logout()

        self.assertRedirects(response_update_1,
                             self.url_list,
                             status_code=302,
                             target_status_code=200)
        self.assertRedirects(response_update_2,
                             self.url_list,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response_update_1, 'travel/visited_city/list.html')
        self.assertTemplateUsed(response_update_2, 'travel/visited_city/list.html')

    def test_form_has_fields(self):
        """
        Проверка наличия всех элементов формы.
        """
        form = VisitedCity_Create_Form()
        self.assertIn('region', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('date_of_visit', form.fields)
        self.assertIn('has_magnet', form.fields, 'f')
        self.assertIn('impression', form.fields)
        self.assertIn('rating', form.fields)
