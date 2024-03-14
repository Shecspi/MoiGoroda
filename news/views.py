"""
Реализует классы для отображения новостей.

* NewsList - Отображает список всех новостей с разделением по страницам.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.views.generic import ListView

from news.models import News
from services import logger
from services.db.news_repo import annotate_news_as_read


class NewsList(ListView):
    """
    Отображает список всех новостей с разделением по страницам.
    """

    model = News
    paginate_by = 5
    ordering = '-created'
    template_name = 'news/news__list.html'

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            '(News) Viewing the news list',
        )
        return super().get(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            queryset = annotate_news_as_read(queryset, self.request.user.pk)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
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
        context['page_description'] = 'Новости проекта "Мои городв"'

        return context
