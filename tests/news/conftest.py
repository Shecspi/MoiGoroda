import pytest
from django.db import transaction

from news.models import News


@pytest.fixture
def setup_db():
    newss = (
        ('Заголовок новости 1', '* list1\r\r1. list2'),
        ('Заголовок новости 2', '#H1\r##H2\r###H3\r####H4\r#####H5\r######H6\r'
                                '**bold1**\r__bold2__\r*italic1*\r_italic2_\r'
                                '[Link](https://link)\r![Изображение](https://link)\r'
                                '```somecode1```\r`somecode2`\r> Quoting'),
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
