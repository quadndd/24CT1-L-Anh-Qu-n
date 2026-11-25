from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cua_hang_xe.models import Xe

from .bieu_mau import BieuMauDatHang
from .models import ChiTietDonHang, DonHang, MucGioHang
from .tien_ich_gio_hang import lay_hoac_tao_gio_hang, tao_ma_don_hang


def xem_gio_hang(yeu_cau):
    """Hiển thị chi tiết giỏ hàng hiện tại."""
    gio_hang = lay_hoac_tao_gio_hang(yeu_cau)
    cac_muc = gio_hang.cac_muc.select_related('xe', 'xe__hang_xe')
    return render(
        yeu_cau,
        'don_hang/gio_hang.html',
        {
            'gio_hang': gio_hang,
            'cac_muc': cac_muc,
        },
    )


def them_vao_gio(yeu_cau, ma_xe):
    """Thêm xe vào giỏ hàng với số lượng và kiểm tra tồn kho."""
    xe = get_object_or_404(Xe, pk=ma_xe, dang_kinh_doanh=True)
    if not xe.con_hang():
        messages.error(yeu_cau, f'Mẫu xe {xe.ten_xe} hiện đã hết hàng.')
        return redirect('cua_hang_xe:chi_tiet_xe', duong_dan=xe.duong_dan)

    try:
        so_luong = int(yeu_cau.POST.get('so_luong', 1))
    except (TypeError, ValueError):
        so_luong = 1
    so_luong = max(1, so_luong)
    mau_chon = yeu_cau.POST.get('mau_da_chon', '').strip() or xe.mau_sac

    gio_hang = lay_hoac_tao_gio_hang(yeu_cau)
    muc, da_tao = MucGioHang.objects.get_or_create(
        gio_hang=gio_hang,
        xe=xe,
        mau_da_chon=mau_chon,
        defaults={'so_luong': min(so_luong, xe.so_luong_ton)},
    )
    if not da_tao:
        so_luong_moi = muc.so_luong + so_luong
        if so_luong_moi > xe.so_luong_ton:
            muc.so_luong = xe.so_luong_ton
            messages.warning(
                yeu_cau,
                f'Số lượng tối đa còn lại của {xe.ten_xe} là {xe.so_luong_ton} chiếc.',
            )
        else:
            muc.so_luong = so_luong_moi
            messages.success(yeu_cau, f'Đã cập nhật số lượng {xe.ten_xe} trong giỏ hàng.')
        muc.save()
    else:
        messages.success(yeu_cau, f'Đã thêm {xe.ten_xe} vào giỏ hàng.')

    if yeu_cau.POST.get('mua_ngay') == '1':
        return redirect('don_hang:dat_hang')

    trang_truoc = yeu_cau.META.get('HTTP_REFERER')
    if trang_truoc:
        return redirect(trang_truoc)
    return redirect('don_hang:xem_gio_hang')


def cap_nhat_gio_hang(yeu_cau, ma_muc):
    """Cập nhật số lượng một mục trong giỏ hàng."""
    gio_hang = lay_hoac_tao_gio_hang(yeu_cau)
    muc = get_object_or_404(MucGioHang, pk=ma_muc, gio_hang=gio_hang)

    if yeu_cau.method == 'POST':
        try:
            so_luong_moi = int(yeu_cau.POST.get('so_luong', 1))
        except (TypeError, ValueError):
            so_luong_moi = 1

        if so_luong_moi <= 0:
            muc.delete()
            messages.info(yeu_cau, f'Đã xóa {muc.xe.ten_xe} khỏi giỏ hàng.')
        elif so_luong_moi > muc.xe.so_luong_ton:
            muc.so_luong = muc.xe.so_luong_ton
            muc.save()
            messages.warning(
                yeu_cau,
                f'{muc.xe.ten_xe} chỉ còn {muc.xe.so_luong_ton} chiếc trong kho.',
            )
        else:
            muc.so_luong = so_luong_moi
            muc.save()
            messages.success(yeu_cau, 'Đã cập nhật giỏ hàng.')

    return redirect('don_hang:xem_gio_hang')


def xoa_khoi_gio(yeu_cau, ma_muc):
    """Xóa một mục khỏi giỏ hàng."""
    gio_hang = lay_hoac_tao_gio_hang(yeu_cau)
    muc = get_object_or_404(MucGioHang, pk=ma_muc, gio_hang=gio_hang)
    ten_xe = muc.xe.ten_xe
    muc.delete()
    messages.info(yeu_cau, f'Đã xóa {ten_xe} khỏi giỏ hàng.')
    return redirect('don_hang:xem_gio_hang')


@login_required
def dat_hang(yeu_cau):
    """Trang xác nhận thông tin và đặt mua xe từ giỏ hàng."""
    gio_hang = lay_hoac_tao_gio_hang(yeu_cau)
    cac_muc = list(gio_hang.cac_muc.select_related('xe', 'xe__hang_xe'))

    if not cac_muc:
        messages.warning(yeu_cau, 'Giỏ hàng của bạn đang trống. Vui lòng chọn xe trước khi đặt hàng.')
        return redirect('cua_hang_xe:danh_sach_xe')

    for muc in cac_muc:
        if not muc.xe.con_hang() or muc.so_luong > muc.xe.so_luong_ton:
            messages.error(
                yeu_cau,
                f'Xe {muc.xe.ten_xe} không đủ số lượng tồn kho (còn {muc.xe.so_luong_ton} chiếc).',
            )
            return redirect('don_hang:xem_gio_hang')

    ho_so = getattr(yeu_cau.user, 'ho_so', None)
    du_lieu_ban_dau = {
        'email': yeu_cau.user.email,
        'ho_ten_nguoi_nhan': ho_so.lay_ten_hien_thi() if ho_so else yeu_cau.user.username,
        'so_dien_thoai': ho_so.so_dien_thoai if ho_so else '',
        'dia_chi_giao_xe': ho_so.dia_chi if ho_so else '',
    }

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauDatHang(yeu_cau.POST)
        if bieu_mau.is_valid():
            with transaction.atomic():
                don_hang = bieu_mau.save(commit=False)
                don_hang.ma_don_hang = tao_ma_don_hang()
                don_hang.nguoi_dung = yeu_cau.user
                don_hang.tong_tien = gio_hang.tong_tien()
                don_hang.phi_van_chuyen = (
                    5_000_000 if don_hang.phuong_thuc_nhan_xe == 'giao_tan_noi' else 0
                )
                don_hang.save()

                for muc in cac_muc:
                    ChiTietDonHang.objects.create(
                        don_hang=don_hang,
                        xe=muc.xe,
                        ten_xe=f'{muc.xe.hang_xe.ten_hang} {muc.xe.ten_xe}',
                        don_gia=muc.xe.lay_gia_hien_tai(),
                        so_luong=muc.so_luong,
                        mau_xe=muc.mau_da_chon,
                    )
                    muc.xe.so_luong_ton = max(0, muc.xe.so_luong_ton - muc.so_luong)
                    muc.xe.save(update_fields=['so_luong_ton'])

                gio_hang.cac_muc.all().delete()

            messages.success(
                yeu_cau,
                f'Đặt hàng thành công! Mã đơn hàng của bạn là {don_hang.ma_don_hang}.',
            )
            return redirect('don_hang:chi_tiet_don_hang', ma_don_hang=don_hang.ma_don_hang)
    else:
        bieu_mau = BieuMauDatHang(initial=du_lieu_ban_dau)

    return render(
        yeu_cau,
        'don_hang/dat_hang.html',
        {
            'bieu_mau': bieu_mau,
            'gio_hang': gio_hang,
            'cac_muc': cac_muc,
        },
    )


@login_required
def lich_su_don_hang(yeu_cau):
    """Hiển thị toàn bộ đơn hàng của người dùng đang đăng nhập."""
    cac_don_hang = DonHang.objects.filter(nguoi_dung=yeu_cau.user).prefetch_related('chi_tiet')
    return render(yeu_cau, 'don_hang/lich_su_don_hang.html', {'cac_don_hang': cac_don_hang})


@login_required
def chi_tiet_don_hang(yeu_cau, ma_don_hang):
    """Xem chi tiết một đơn hàng cụ thể."""
    don_hang = get_object_or_404(
        DonHang.objects.prefetch_related('chi_tiet', 'chi_tiet__xe'),
        ma_don_hang=ma_don_hang,
        nguoi_dung=yeu_cau.user,
    )
    return render(yeu_cau, 'don_hang/chi_tiet_don_hang.html', {'don_hang': don_hang})


@login_required
def huy_don_hang(yeu_cau, ma_don_hang):
    """Hủy đơn hàng nếu đang ở trạng thái cho phép và hoàn lại tồn kho."""
    don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang, nguoi_dung=yeu_cau.user)
    if yeu_cau.method == 'POST' and don_hang.co_the_huy():
        with transaction.atomic():
            for chi_tiet in don_hang.chi_tiet.select_related('xe'):
                if chi_tiet.xe:
                    chi_tiet.xe.so_luong_ton += chi_tiet.so_luong
                    chi_tiet.xe.save(update_fields=['so_luong_ton'])
            don_hang.trang_thai = 'da_huy'
            don_hang.save(update_fields=['trang_thai'])
        messages.info(yeu_cau, f'Đơn hàng {don_hang.ma_don_hang} đã được hủy.')
    else:
        messages.warning(yeu_cau, 'Đơn hàng này không thể hủy ở trạng thái hiện tại.')
    return redirect('don_hang:chi_tiet_don_hang', ma_don_hang=don_hang.ma_don_hang)
