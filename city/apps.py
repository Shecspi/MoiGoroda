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

    def ready(self):
        import city.signals
