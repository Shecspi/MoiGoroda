"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.apps import AppConfig


class UiDemoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ui_demo'
    verbose_name = 'Демо UI-компонентов'
