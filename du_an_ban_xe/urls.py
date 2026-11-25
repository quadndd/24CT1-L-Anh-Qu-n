from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Quản Trị Hệ Thống AutoViet'
admin.site.site_title = 'AutoViet Admin'
admin.site.index_title = 'Bảng điều khiển quản lý bán xe'

urlpatterns = [
    path('quan-tri/', admin.site.urls),
    path('', include('cua_hang_xe.urls')),
    path('tai-khoan/', include('tai_khoan.urls')),
    path('', include('don_hang.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
