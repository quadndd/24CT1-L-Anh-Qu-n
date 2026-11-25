from don_hang.tien_ich_gio_hang import lay_gio_hang_hien_tai

from .models import HangXe, LoaiXe, XeYeuThich


def du_lieu_toan_cuc(yeu_cau):
    """Cung cấp dữ liệu dùng chung cho thanh điều hướng và chân trang."""
    gio_hang = lay_gio_hang_hien_tai(yeu_cau)
    tong_so_luong_gio_hang = gio_hang.tong_so_luong() if gio_hang else 0

    so_xe_yeu_thich = 0
    if yeu_cau.user.is_authenticated:
        so_xe_yeu_thich = XeYeuThich.objects.filter(nguoi_dung=yeu_cau.user).count()

    return {
        'danh_sach_hang_xe': HangXe.objects.all(),
        'danh_sach_loai_xe': LoaiXe.objects.all(),
        'tong_so_luong_gio_hang': tong_so_luong_gio_hang,
        'so_xe_yeu_thich': so_xe_yeu_thich,
    }
