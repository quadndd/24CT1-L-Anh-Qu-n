from django.urls import path

from . import views

app_name = 'tai_khoan'

urlpatterns = [
    path('dang-ky/', views.dang_ky, name='dang_ky'),
    path('dang-nhap/', views.dang_nhap, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat, name='dang_xuat'),
    path('ho-so/', views.ho_so_nguoi_dung, name='ho_so'),
    path('doi-mat-khau/', views.doi_mat_khau, name='doi_mat_khau'),
]
