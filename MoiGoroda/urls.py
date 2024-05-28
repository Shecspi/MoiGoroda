from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from django.conf import settings
from django.views.generic import TemplateView

import account.views

urlpatterns = [
    path('', include('main_page.urls'), name='main_page'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('share/', include('share.urls')),
    path('news/', include('news.urls')),
    path('collection/', include('collection.urls')),
    path('city/', include('city.urls')),
    path('region/', include('region.urls')),
    path('mdeditor/', include('mdeditor.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    path('dashboard/', include('dashboard.urls')),
    path('subscribe/', include('subscribe.urls')),
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
