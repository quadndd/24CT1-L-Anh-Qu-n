from django.contrib import admin

from .models import ChiTietDonHang, DonHang, GioHang, MucGioHang


class ChiTietDonHangNoiTiep(admin.TabularInline):
    model = ChiTietDonHang
    extra = 0
    readonly_fields = ('xe', 'ten_xe', 'don_gia', 'so_luong', 'mau_xe')


@admin.register(DonHang)
class QuanLyDonHang(admin.ModelAdmin):
    list_display = (
        'ma_don_hang',
        'nguoi_dung',
        'ho_ten_nguoi_nhan',
        'so_dien_thoai',
        'tong_tien',
        'phuong_thuc_thanh_toan',
        'trang_thai',
        'da_thanh_toan',
        'ngay_dat',
    )
    list_filter = ('trang_thai', 'phuong_thuc_thanh_toan', 'da_thanh_toan', 'ngay_dat')
    search_fields = ('ma_don_hang', 'ho_ten_nguoi_nhan', 'so_dien_thoai', 'nguoi_dung__username')
    inlines = [ChiTietDonHangNoiTiep]


@admin.register(GioHang)
class QuanLyGioHang(admin.ModelAdmin):
    list_display = ('id', 'nguoi_dung', 'ma_phien', 'ngay_cap_nhat')


@admin.register(MucGioHang)
class QuanLyMucGioHang(admin.ModelAdmin):
    list_display = ('gio_hang', 'xe', 'so_luong', 'mau_da_chon')
