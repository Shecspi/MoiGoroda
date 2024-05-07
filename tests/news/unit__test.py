"""

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import pytest

from news.models import News
from news.repository import annotate_news_with_number_of_users_who_read_news

from django.urls import reverse


url = reverse('news-list')


@pytest.mark.django_db
def test__annotate_news_with_number_of_users_who_read_news(setup, client):
    news = annotate_news_with_number_of_users_who_read_news(News.objects.all())
    assert news[0].number_of_users_who_read_news == 0

    client.login(username='username1', password='password')
    client.get(url)

    news = annotate_news_with_number_of_users_who_read_news(News.objects.all())
    assert news[0].number_of_users_who_read_news == 1


@pytest.mark.django_db
def test__user_can_be_annotated_as_read_news_only_one_time(setup, client):
    client.login(username='username1', password='password')
    client.get(url)
    news = annotate_news_with_number_of_users_who_read_news(News.objects.all())
    assert news[0].number_of_users_who_read_news == 1

    client.get(url)
    news = annotate_news_with_number_of_users_who_read_news(News.objects.all())
    assert news[0].number_of_users_who_read_news == 1

    client.get(url)
    news = annotate_news_with_number_of_users_who_read_news(News.objects.all())
    assert news[0].number_of_users_who_read_news == 1
