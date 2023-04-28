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


class NewsList(ListView):
    """
    Отображает список всех новостей с разделением по страницам.
    """
    model = News
    paginate_by = 5
    ordering = '-created'
    template_name = 'news/news__list.html'
