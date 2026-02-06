from django.contrib import admin

from place.models import TagOSM, Category, Place, PlaceCollection


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


@admin.register(PlaceCollection)
class PlaceCollectionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('id', 'title', 'user', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public',)
    search_fields = ('title',)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        'id',
        'name',
        'latitude',
        'longitude',
        'category',
        'user',
        'is_visited',
        'collection',
        'created_at',
        'updated_at',
    )
    list_filter = ('is_visited',)
    search_fields = ('name',)
