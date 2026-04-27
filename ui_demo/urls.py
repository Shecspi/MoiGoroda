"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from . import views

app_name = 'ui_demo'

urlpatterns = [
    path('', views.index, name='index'),
    path('buttons/', views.buttons, name='buttons'),
    path('badges/', views.badges, name='badges'),
    path('forms/', views.forms, name='forms'),
    path('misc/', views.misc, name='misc'),
    path('city-popup/', views.city_popup, name='city_popup'),
]
