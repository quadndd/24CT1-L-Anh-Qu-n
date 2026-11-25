from django.contrib import admin

from .models import HoSoNguoiDung


@admin.register(HoSoNguoiDung)
class QuanLyHoSoNguoiDung(admin.ModelAdmin):
    list_display = ('nguoi_dung', 'ho_va_ten', 'so_dien_thoai', 'thanh_pho', 'ngay_cap_nhat')
    search_fields = ('nguoi_dung__username', 'ho_va_ten', 'so_dien_thoai')
    list_filter = ('thanh_pho',)
