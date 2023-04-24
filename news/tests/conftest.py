import pytest
from django.db import transaction

from news.models import News


@pytest.fixture
def setup_db():
    newss = (
        ('Новость 1', 'Текст новости 1'),
        ('Новость 2', 'Текст новости 2'),
    )
    with transaction.atomic():
        for news in newss:
            News.objects.create(
                title=news[0],
                content=news[1],
            )


@pytest.fixture
def create_user(client, django_user_model):
    new_user = django_user_model.objects.create_user(
        username='username', password='password'
    )
    return new_user
