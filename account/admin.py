from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from city.models import VisitedCity


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('qty_of_cities',)

    def qty_of_cities(self, obj):
        return VisitedCity.objects.filter(user=obj.id).count()

    qty_of_cities.short_description = 'Количество городов'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
