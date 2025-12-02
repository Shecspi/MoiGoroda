"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Конфигурация приложения новостей."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'Новости'
