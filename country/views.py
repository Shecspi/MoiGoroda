"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.shortcuts import render


def country(request):
    return render(request, 'country/map.html')
