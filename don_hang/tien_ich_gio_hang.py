import random
import string
from django.utils import timezone

from .models import DonHang, GioHang, MucGioHang


def lay_ma_phien(yeu_cau):
    """Đảm bảo phiên làm việc có session_key và trả về mã phiên."""
    if not yeu_cau.session.session_key:
        yeu_cau.session.create()
    return yeu_cau.session.session_key


def lay_gio_hang_hien_tai(yeu_cau):
    """Lấy giỏ hàng hiện tại nếu đã tồn tại (không tự tạo mới)."""
    if yeu_cau.user.is_authenticated:
        return GioHang.objects.filter(nguoi_dung=yeu_cau.user).first()
    ma_phien = yeu_cau.session.session_key
    if not ma_phien:
        return None
    return GioHang.objects.filter(ma_phien=ma_phien, nguoi_dung__isnull=True).first()


def lay_hoac_tao_gio_hang(yeu_cau):
    """Lấy hoặc tạo giỏ hàng cho người dùng đăng nhập hoặc khách vãng lai."""
    if yeu_cau.user.is_authenticated:
        gio_hang, _ = GioHang.objects.get_or_create(nguoi_dung=yeu_cau.user)
        return gio_hang
    ma_phien = lay_ma_phien(yeu_cau)
    gio_hang, _ = GioHang.objects.get_or_create(ma_phien=ma_phien, nguoi_dung=None)
    return gio_hang


def gop_gio_hang_khi_dang_nhap(yeu_cau, nguoi_dung):
    """Gộp giỏ hàng tạm trong phiên vào giỏ hàng tài khoản sau khi đăng nhập."""
    ma_phien = yeu_cau.session.session_key
    if not ma_phien:
        return
    gio_tam = GioHang.objects.filter(ma_phien=ma_phien, nguoi_dung__isnull=True).first()
    if not gio_tam:
        return
    gio_chinh, _ = GioHang.objects.get_or_create(nguoi_dung=nguoi_dung)
    for muc_tam in gio_tam.cac_muc.select_related('xe'):
        muc_ton_tai = MucGioHang.objects.filter(
            gio_hang=gio_chinh,
            xe=muc_tam.xe,
            mau_da_chon=muc_tam.mau_da_chon,
        ).first()
        if muc_ton_tai:
            tong_moi = muc_ton_tai.so_luong + muc_tam.so_luong
            muc_ton_tai.so_luong = min(tong_moi, muc_tam.xe.so_luong_ton)
            muc_ton_tai.save()
        else:
            MucGioHang.objects.create(
                gio_hang=gio_chinh,
                xe=muc_tam.xe,
                so_luong=min(muc_tam.so_luong, muc_tam.xe.so_luong_ton),
                mau_da_chon=muc_tam.mau_da_chon,
            )
    gio_tam.delete()


def tao_ma_don_hang():
    """Sinh mã đơn hàng duy nhất theo định dạng DH-YYYYMMDD-XXXX."""
    ngay_hom_nay = timezone.now().strftime('%Y%m%d')
    while True:
        hau_to = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ma_moi = f'DH-{ngay_hom_nay}-{hau_to}'
        if not DonHang.objects.filter(ma_don_hang=ma_moi).exists():
            return ma_moi
