"""

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import pytest

from tests.create_db import create_user, create_superuser, create_news


@pytest.fixture
def setup(django_user_model):
    create_user(django_user_model, 1)
    create_superuser(django_user_model, 2)
    create_news(id=1, title='Заголовок новости 1', content='Content 1')
    create_news(id=2, title='Заголовок новости 2', content='Content 2')
    create_news(id=3, title='Заголовок новости 3', content='* list1\r\r1. list2')
    create_news(
        id=4,
        title='Заголовок новости 4',
        content='#H1\r##H2\r###H3\r####H4\r#####H5\r######H6\r'
        '**bold1**\r__bold2__\r*italic1*\r_italic2_\r'
        '[Link](https://link)\r![Изображение](https://link)\r'
        '```somecode1```\r`somecode2`\r> Quoting',
    )
