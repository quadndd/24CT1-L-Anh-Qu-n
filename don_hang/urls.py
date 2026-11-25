from django.urls import path

from . import views

app_name = 'don_hang'

urlpatterns = [
    path('gio-hang/', views.xem_gio_hang, name='xem_gio_hang'),
    path('gio-hang/them/<int:ma_xe>/', views.them_vao_gio, name='them_vao_gio'),
    path('gio-hang/cap-nhat/<int:ma_muc>/', views.cap_nhat_gio_hang, name='cap_nhat_gio_hang'),
    path('gio-hang/xoa/<int:ma_muc>/', views.xoa_khoi_gio, name='xoa_khoi_gio'),
    path('dat-hang/', views.dat_hang, name='dat_hang'),
    path('don-hang/', views.lich_su_don_hang, name='lich_su_don_hang'),
    path('don-hang/<str:ma_don_hang>/', views.chi_tiet_don_hang, name='chi_tiet_don_hang'),
    path('don-hang/<str:ma_don_hang>/huy/', views.huy_don_hang, name='huy_don_hang'),
]
