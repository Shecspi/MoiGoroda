from django.db.models import QuerySet, Count

from news.models import News


def annotate_news_with_number_of_users_who_read_news(queryset: QuerySet[News]) -> QuerySet[News]:
    return queryset.annotate(
        number_of_users_who_read_news=Count('users_read')
    )
