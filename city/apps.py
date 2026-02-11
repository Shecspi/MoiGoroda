"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.apps import AppConfig


class CityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'city'
    verbose_name = 'Города'

    def ready(self) -> None:
        import city.signals  # noqa: F401 — регистрация обработчиков сигналов
