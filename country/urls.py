"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.country, name='country'),
]
