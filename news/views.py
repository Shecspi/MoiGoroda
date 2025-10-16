"""
Реализует классы для отображения новостей.

* NewsList - Отображает список
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.db.models import QuerySet
from django.http import HttpResponse
from django.views.generic import ListView

from news.models import News
from news.repository import annotate_news_with_number_of_users_who_read_news
from services import logger
from services.db.news_repo import annotate_news_as_read


class NewsList(ListView):  # type: ignore[type-arg]
    """
    Отображает список всех новостей с разделением по страницам.
    """

    model = News
    paginate_by = 5
    ordering = '-created'
    template_name = 'news/news__list.html'

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        logger.info(self.request, '(News) Viewing the news list')
        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[News]:
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            queryset = annotate_news_as_read(queryset, self.request.user.pk)

        if self.request.user.is_superuser:
            queryset = annotate_news_with_number_of_users_who_read_news(queryset)

        return queryset

    def get_context_data(  # type: ignore[override]
        self, *, object_list: QuerySet[News] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Непрочитанные пользователем новости отмечаются прочитанными
        # Это реализовано здесь, так как только здесь через context['object_list']
        # удалось получить доступ к записям после пагинации.
        # get_queryset() возвращает все записи без лимитов,
        # а отмечать прочитанными нужно только новости с текущей страницы
        if self.request.user.is_authenticated:
            for news in context['object_list']:
                if not news.is_read:
                    news.users_read.add(self.request.user)

        context['active_page'] = 'news'
        context['page_title'] = 'Новости'
        context['page_description'] = 'Новости проекта «Мои города»'

        return context
