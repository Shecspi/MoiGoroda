"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib import admin

from country.models import PartOfTheWorld, Country, Location

admin.site.register([PartOfTheWorld, Location, Country])
