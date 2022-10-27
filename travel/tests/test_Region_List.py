from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy


class Test_Region_List(TestCase):
    url = reverse_lazy('region-all')
    login_url = reverse_lazy('signin')
    user_data = {'username': 'user', 'password': 'password'}

    def setUp(self) -> None:
        User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])

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
