from django.contrib import admin

from place.models import TagOSM, Category, Place


@admin.register(TagOSM)
class TagOSMAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'get_tags')
    search_fields = ('name',)

    def get_tags(self, obj: Category) -> str:
        tags = obj.tags.all()
        return ', '.join([str(item) for item in tags])


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'name',
        'latitude',
        'longitude',
        'category',
        'user',
        'created_at',
        'updated_at',
    )
    search_fields = ('name',)
