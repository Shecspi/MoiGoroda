"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.apps import AppConfig


class PlaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'place'
    verbose_name = 'Интересные места'
