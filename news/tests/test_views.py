from datetime import datetime

from django.test import TestCase
from django.urls import reverse_lazy

from news.models import News


class TestNews(TestCase):
    url = reverse_lazy('news')

    def test_page_is_exist(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
