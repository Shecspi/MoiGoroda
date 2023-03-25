from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy
from travel.models import Region, Area


class Test_Region_List(TestCase):
    url = reverse_lazy('region-all')
    login_url = reverse_lazy('signin')
    user_data = {'username': 'user', 'password': 'password'}
    regions = (
        ('Московская область', 'O', 'RU-MOS'),
        ('Москва', 'G', 'RU-MOW'),
        ('Волгоградская область', 'O', 'RU-VGG'),
        ('Вологодская область', 'O', 'RU-VLG'),
    )

    def setUp(self) -> None:
        User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        area = Area.objects.create(title='Центральный федеральный округ')
        for region in self.regions:
            Region.objects.create(area=area, title=region[0], type=region[1], iso3166=region[2])

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
        self.assertTemplateUsed(response, 'travel/region/list.html')

    def test_filter(self):
        """
        Тестирует работу фильтров для поиска регионов.
        На странице должны отображаться только регионы, начинающиеся на 'вол' без учета регистра.
        """
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response1 = self.client.get(self.url + '?filter=Вол')
        response2 = self.client.get(self.url + '?filter=вол')

        self.assertContains(response1, self.regions[2][0])
        self.assertContains(response1, self.regions[3][0])
        self.assertNotContains(response1, self.regions[0][0])
        self.assertNotContains(response1, self.regions[1][0])
        self.assertContains(response2, self.regions[2][0])
        self.assertContains(response2, self.regions[3][0])
        self.assertNotContains(response2, self.regions[0][0])
        self.assertNotContains(response2, self.regions[1][0])

        self.client.logout()
