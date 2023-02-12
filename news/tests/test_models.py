from datetime import datetime

from django.test import TestCase
from django.urls import reverse_lazy

from news.models import News


class NewsModelTest(TestCase):
    news_title = 'Заголовок новости'
    news_content = 'Содержание новости'

    title_verbose_name = 'Заголовок'
    content_verbose_name = 'Описание'
    created_verbose_name = 'Создано'
    last_modified_verbose_name = 'Изменено'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title=cls.news_title,
            content=cls.news_content
        )

    def test_is_model_has_all_fields(self):
        """
        Тестирует надичие всех необходимых полей у модели.
        """
        self.assertIsInstance(self.news.title, str)
        self.assertIsInstance(self.news.content, str)
        self.assertIsInstance(self.news.created, datetime)
        self.assertIsInstance(self.news.last_modified, datetime)

    def test_is_fields_have_verbose_name(self):
        """
        Тестирует наличие 'Verbose name' у полей модели.
        """
        news = News.objects.get(pk=1)

        self.assertEqual(news._meta.get_field('title').verbose_name, self.title_verbose_name)
        self.assertEqual(news._meta.get_field('content').verbose_name, self.content_verbose_name)
        self.assertEqual(news._meta.get_field('created').verbose_name, self.created_verbose_name)
        self.assertEqual(news._meta.get_field('last_modified').verbose_name, self.last_modified_verbose_name)

    def test_str_method(self):
        """
        Тестирует корректность возвращаемой информации методом __str__.
        Возвращаться должен заголовок новости.
        """
        self.assertEqual(str(self.news), self.news_title)

