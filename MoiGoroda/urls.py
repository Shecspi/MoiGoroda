from django.urls import path, include
from django.contrib import admin

from django.conf import settings

urlpatterns = [
    path('', include('main_page.urls'), name='main_page'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('travel/', include('travel.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
