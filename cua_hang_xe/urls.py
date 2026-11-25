from django.urls import path

from . import views

app_name = 'cua_hang_xe'

urlpatterns = [
    path('', views.trang_chu, name='trang_chu'),
    path('danh-sach-xe/', views.danh_sach_xe, name='danh_sach_xe'),
    path('xe/<slug:duong_dan>/', views.chi_tiet_xe, name='chi_tiet_xe'),
    path('dat-lich-lai-thu/', views.dat_lich_lai_thu, name='dat_lich_lai_thu'),
    path('yeu-thich/', views.danh_sach_yeu_thich, name='danh_sach_yeu_thich'),
    path('yeu-thich/chuyen-doi/<int:ma_xe>/', views.chuyen_doi_yeu_thich, name='chuyen_doi_yeu_thich'),
    path('quan-ly-xe/', views.quan_ly_xe, name='quan_ly_xe'),
    path('quan-ly-xe/them/', views.them_xe_moi, name='them_xe_moi'),
    path('quan-ly-xe/sua/<int:ma_xe>/', views.sua_xe, name='sua_xe'),
    path('quan-ly-xe/xoa/<int:ma_xe>/', views.xoa_xe, name='xoa_xe'),
    path('quan-ly-xe/nhap-so-luong/<int:ma_xe>/', views.nhap_them_so_luong, name='nhap_them_so_luong'),
    path('quan-ly-xe/them-loai-xe/', views.them_loai_xe, name='them_loai_xe'),
    path('quan-ly-xe/them-hang-xe/', views.them_hang_xe, name='them_hang_xe'),
]
