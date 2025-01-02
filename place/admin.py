from django.contrib import admin

from place.models import TagOSM, TypeObject


@admin.register(TagOSM)
class TagOSMAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(TypeObject)
class TypeObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tags')

    def get_tags(self, obj):
        tags = obj.tags.all()
        return ', '.join([str(item) for item in tags])
