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
from utils.LoggingMixin import LoggingMixin


class NewsList(ListView, LoggingMixin):
    """
    Отображает список всех новостей с разделением по страницам.
    """
    model = News
    paginate_by = 5
    ordering = '-created'
    template_name = 'news/news__l' \
                    'ist.html'

    def get(self, *args, **kwargs):
        self.set_message(self.request, 'Viewing the news list')

        return super().get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'news'
        context['page_title'] = 'Новости'
        context['page_description'] = 'Новости проекта "Мои городв"'

        return context
