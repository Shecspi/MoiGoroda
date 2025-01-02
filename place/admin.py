from django.contrib import admin

from place.models import TagOSM, TypeObject, Place


@admin.register(TagOSM)
class TagOSMAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(TypeObject)
class TypeObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tags')
    search_fields = ('name',)

    def get_tags(self, obj):
        tags = obj.tags.all()
        return ', '.join([str(item) for item in tags])


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'type_object', 'created_at', 'updated_at')
    search_fields = ('name',)
