from datetime import datetime

from django.test import TestCase
from django.urls import reverse_lazy

from news.models import News


class TestNews(TestCase):
    url = reverse_lazy('news-list')

    def test_page_exists(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'news/list.html')
