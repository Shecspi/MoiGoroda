"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from dashboard.views import dashboard


urlpatterns = [
    path('', dashboard, name='dashboard'),
]
