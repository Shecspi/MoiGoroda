"""
Реализует функции, взаимодействующие с моделью News.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import QuerySet, Exists, OuterRef

from news.models import News


def annotate_news_as_read(queryset: QuerySet[News], user_id: int) -> QuerySet[News]:
    """
    Добавляет к QuerySet булево поле 'is_read', которое равно True, если пользователь
    с указанным user_id уже прочитал новость, иначе False.
    """
    return queryset.annotate(
        is_read=Exists(
            News.users_read.through.objects.filter(user_id=user_id, news_id=OuterRef('pk'))
        )
    )
