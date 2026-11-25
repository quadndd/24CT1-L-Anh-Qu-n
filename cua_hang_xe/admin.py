from django.contrib import admin

from .models import DanhGiaXe, HangXe, HinhAnhXe, LichLaiThu, LoaiXe, Xe, XeYeuThich


class HinhAnhXeNoiTiep(admin.TabularInline):
    model = HinhAnhXe
    extra = 1


@admin.register(HangXe)
class QuanLyHangXe(admin.ModelAdmin):
    list_display = ('ten_hang', 'quoc_gia', 'duong_dan')
    prepopulated_fields = {'duong_dan': ('ten_hang',)}
    search_fields = ('ten_hang', 'quoc_gia')


@admin.register(LoaiXe)
class QuanLyLoaiXe(admin.ModelAdmin):
    list_display = ('ten_loai', 'duong_dan')
    prepopulated_fields = {'duong_dan': ('ten_loai',)}
    search_fields = ('ten_loai',)


@admin.register(Xe)
class QuanLyXe(admin.ModelAdmin):
    list_display = (
        'ten_xe',
        'hang_xe',
        'loai_xe',
        'gia_ban',
        'gia_khuyen_mai',
        'nam_san_xuat',
        'so_luong_ton',
        'xe_noi_bat',
        'dang_kinh_doanh',
    )
    list_filter = ('hang_xe', 'loai_xe', 'nhien_lieu', 'hop_so', 'xe_noi_bat', 'dang_kinh_doanh')
    search_fields = ('ten_xe', 'hang_xe__ten_hang', 'dong_co')
    prepopulated_fields = {'duong_dan': ('ten_xe',)}
    inlines = [HinhAnhXeNoiTiep]


@admin.register(DanhGiaXe)
class QuanLyDanhGiaXe(admin.ModelAdmin):
    list_display = ('xe', 'nguoi_dung', 'so_sao', 'ngay_danh_gia')
    list_filter = ('so_sao',)
    search_fields = ('xe__ten_xe', 'nguoi_dung__username', 'noi_dung')


@admin.register(XeYeuThich)
class QuanLyXeYeuThich(admin.ModelAdmin):
    list_display = ('nguoi_dung', 'xe', 'ngay_them')


@admin.register(LichLaiThu)
class QuanLyLichLaiThu(admin.ModelAdmin):
    list_display = ('ho_ten', 'so_dien_thoai', 'xe', 'ngay_hen', 'gio_hen', 'trang_thai')
    list_filter = ('trang_thai', 'ngay_hen')
    search_fields = ('ho_ten', 'so_dien_thoai', 'xe__ten_xe')
