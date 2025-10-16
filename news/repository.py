"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import Count, QuerySet

from news.models import News


def annotate_news_with_number_of_users_who_read_news(queryset: QuerySet[News]) -> QuerySet[News]:
    """
    Аннотирует QuerySet новостей количеством пользователей, которые их прочитали.

    Args:
        queryset: QuerySet новостей для аннотации.

    Returns:
        QuerySet[News]: QuerySet с дополнительным полем 'number_of_users_who_read_news'.
    """
    return queryset.annotate(number_of_users_who_read_news=Count('users_read'))
