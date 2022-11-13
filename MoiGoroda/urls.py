from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from django.conf import settings

urlpatterns = [
    path('', include('main_page.urls'), name='main_page'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('travel/', include('travel.urls')),
    path('collection/', include('collection.urls'))
]

handler403 = 'MoiGoroda.error_handlers.page403'
handler404 = 'MoiGoroda.error_handlers.page404'
handler500 = 'MoiGoroda.error_handlers.page500'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
