from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from django.conf import settings
from django.views.generic import TemplateView


urlpatterns = [
    path('', include('main_page.urls'), name='main_page'),
    path('account/', include('account.urls')),
    path('city/', include('city.urls.views')),
    path('region/', include('region.urls.views')),
    path('country/', include('country.urls.views')),
    path('place/', include('place.urls.views')),
    path('collection/', include('collection.urls.views')),
    path('news/', include('news.urls')),
    path('subscribe/', include('subscribe.urls')),
    path('share/', include('share.urls')),
    path('dashboard/', include('dashboard.urls.views')),
    path('mdeditor/', include('mdeditor.urls')),
    path('admin/', admin.site.urls),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    # API
    path('api/city/', include('city.urls.api')),
    path('api/country/', include('country.urls.api')),
    path('api/dashboard/', include('dashboard.urls.api')),
    path('api/place/', include('place.urls.api')),
    path('api/region/', include('region.urls.api')),
    path('api/collection/', include('collection.urls.api')),
]

handler403 = 'MoiGoroda.error_handlers.page403'
handler404 = 'MoiGoroda.error_handlers.page404'
handler500 = 'MoiGoroda.error_handlers.page500'

if settings.DEBUG:
    import debug_toolbar  # type: ignore[import-untyped]

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
