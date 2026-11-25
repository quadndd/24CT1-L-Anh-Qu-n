from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from cua_hang_xe.models import LichLaiThu
from don_hang.models import DonHang
from don_hang.tien_ich_gio_hang import gop_gio_hang_khi_dang_nhap

from .bieu_mau import (
    BieuMauCapNhatHoSo,
    BieuMauCapNhatTaiKhoan,
    BieuMauDangKy,
    BieuMauDangNhap,
    BieuMauDoiMatKhau,
)
from .models import HoSoNguoiDung


def dang_ky(yeu_cau):
    """Xử lý đăng ký tài khoản mới cho khách hàng."""
    if yeu_cau.user.is_authenticated:
        return redirect('cua_hang_xe:trang_chu')

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauDangKy(yeu_cau.POST)
        if bieu_mau.is_valid():
            nguoi_dung = bieu_mau.save(commit=False)
            nguoi_dung.email = bieu_mau.cleaned_data['email']
            nguoi_dung.save()

            ho_so, _ = HoSoNguoiDung.objects.get_or_create(nguoi_dung=nguoi_dung)
            ho_so.ho_va_ten = bieu_mau.cleaned_data['ho_va_ten']
            ho_so.so_dien_thoai = bieu_mau.cleaned_data['so_dien_thoai']
            ho_so.dia_chi = bieu_mau.cleaned_data['dia_chi']
            ho_so.save()

            gop_gio_hang_khi_dang_nhap(yeu_cau, nguoi_dung)
            login(yeu_cau, nguoi_dung)
            messages.success(yeu_cau, 'Đăng ký tài khoản thành công! Chào mừng bạn đến với AutoViet.')
            return redirect('cua_hang_xe:trang_chu')
    else:
        bieu_mau = BieuMauDangKy()

    return render(yeu_cau, 'tai_khoan/dang_ky.html', {'bieu_mau': bieu_mau})


def dang_nhap(yeu_cau):
    """Xử lý đăng nhập và đồng bộ giỏ hàng tạm."""
    if yeu_cau.user.is_authenticated:
        return redirect('cua_hang_xe:trang_chu')

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauDangNhap(yeu_cau, data=yeu_cau.POST)
        if bieu_mau.is_valid():
            nguoi_dung = bieu_mau.get_user()
            gop_gio_hang_khi_dang_nhap(yeu_cau, nguoi_dung)
            login(yeu_cau, nguoi_dung)
            messages.success(yeu_cau, f'Xin chào {nguoi_dung.username}, bạn đã đăng nhập thành công!')
            duong_dan_tiep = yeu_cau.GET.get('next') or yeu_cau.POST.get('next')
            if duong_dan_tiep:
                return redirect(duong_dan_tiep)
            return redirect('cua_hang_xe:trang_chu')
    else:
        bieu_mau = BieuMauDangNhap()

    return render(
        yeu_cau,
        'tai_khoan/dang_nhap.html',
        {'bieu_mau': bieu_mau, 'duong_dan_tiep': yeu_cau.GET.get('next', '')},
    )


def dang_xuat(yeu_cau):
    """Đăng xuất khỏi hệ thống."""
    logout(yeu_cau)
    messages.info(yeu_cau, 'Bạn đã đăng xuất khỏi tài khoản.')
    return redirect('cua_hang_xe:trang_chu')


@login_required
def ho_so_nguoi_dung(yeu_cau):
    """Xem và cập nhật thông tin cá nhân, lịch sử đơn hàng và lịch lái thử."""
    ho_so, _ = HoSoNguoiDung.objects.get_or_create(nguoi_dung=yeu_cau.user)

    if yeu_cau.method == 'POST':
        bieu_mau_tai_khoan = BieuMauCapNhatTaiKhoan(yeu_cau.POST, instance=yeu_cau.user)
        bieu_mau_ho_so = BieuMauCapNhatHoSo(
            yeu_cau.POST,
            yeu_cau.FILES,
            instance=ho_so,
        )
        if bieu_mau_tai_khoan.is_valid() and bieu_mau_ho_so.is_valid():
            bieu_mau_tai_khoan.save()
            bieu_mau_ho_so.save()
            messages.success(yeu_cau, 'Cập nhật thông tin cá nhân thành công!')
            return redirect('tai_khoan:ho_so')
    else:
        bieu_mau_tai_khoan = BieuMauCapNhatTaiKhoan(instance=yeu_cau.user)
        bieu_mau_ho_so = BieuMauCapNhatHoSo(instance=ho_so)

    cac_don_hang = DonHang.objects.filter(nguoi_dung=yeu_cau.user)[:5]
    cac_lich_lai_thu = LichLaiThu.objects.filter(nguoi_dung=yeu_cau.user).select_related('xe')[:5]

    return render(
        yeu_cau,
        'tai_khoan/ho_so.html',
        {
            'ho_so': ho_so,
            'bieu_mau_tai_khoan': bieu_mau_tai_khoan,
            'bieu_mau_ho_so': bieu_mau_ho_so,
            'cac_don_hang': cac_don_hang,
            'cac_lich_lai_thu': cac_lich_lai_thu,
        },
    )


@login_required
def doi_mat_khau(yeu_cau):
    """Đổi mật khẩu tài khoản hiện tại."""
    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauDoiMatKhau(yeu_cau.user, yeu_cau.POST)
        if bieu_mau.is_valid():
            nguoi_dung = bieu_mau.save()
            update_session_auth_hash(yeu_cau, nguoi_dung)
            messages.success(yeu_cau, 'Đổi mật khẩu thành công!')
            return redirect('tai_khoan:ho_so')
    else:
        bieu_mau = BieuMauDoiMatKhau(yeu_cau.user)

    return render(yeu_cau, 'tai_khoan/doi_mat_khau.html', {'bieu_mau': bieu_mau})
