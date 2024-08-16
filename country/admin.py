from django.contrib import admin

from country.models import PartOfTheWorld, Country, Location

admin.site.register([PartOfTheWorld, Location, Country])
