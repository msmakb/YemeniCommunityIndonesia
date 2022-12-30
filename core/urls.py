from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main.constants import ADMIN_SITE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('member.urls')),
]

# Static and Media URL Patterns
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site settings
admin.site.site_header = ADMIN_SITE.SITE_HEADER
admin.site.site_title = ADMIN_SITE.SITE_TITLE
admin.site.index_title = ADMIN_SITE.INDEX_TITLE
