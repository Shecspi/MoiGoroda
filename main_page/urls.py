"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='main_page'),
    path('help/', views.help_index, name='help-index'),
    path('help/premium-photos/', views.help_premium_photos, name='help-premium-photos'),
]
