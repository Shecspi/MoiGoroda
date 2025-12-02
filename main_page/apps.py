"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.apps import AppConfig


class MainPageConfig(AppConfig):
    """Конфигурация приложения главной страницы."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_page'
    verbose_name = 'Главная страница'
