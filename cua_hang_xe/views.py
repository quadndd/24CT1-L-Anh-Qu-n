from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render

from .bieu_mau import (
    BieuMauDanhGia,
    BieuMauDatLichLaiThu,
    BieuMauThemHangXe,
    BieuMauThemLoaiXe,
    BieuMauThemSuaXe,
)
from .models import HangXe, HinhAnhXe, LoaiXe, Xe, XeYeuThich
from .tien_ich import chuyen_khong_dau_slug


def trang_chu(yeu_cau):
    """Trang chủ hiển thị xe nổi bật, xe khuyến mãi, hãng xe và loại xe."""
    xe_dang_ban = Xe.objects.filter(dang_kinh_doanh=True).select_related('hang_xe', 'loai_xe')
    xe_noi_bat = xe_dang_ban.filter(xe_noi_bat=True)[:6]
    xe_khuyen_mai = xe_dang_ban.filter(gia_khuyen_mai__isnull=False, gia_khuyen_mai__lt=F('gia_ban'))[:4]
    xe_moi_nhat = xe_dang_ban.order_by('-ngay_tao')[:8]

    return render(
        yeu_cau,
        'cua_hang_xe/trang_chu.html',
        {
            'xe_noi_bat': xe_noi_bat,
            'xe_khuyen_mai': xe_khuyen_mai,
            'xe_moi_nhat': xe_moi_nhat,
            'tong_so_xe': xe_dang_ban.count(),
            'tong_hang_xe': HangXe.objects.count(),
        },
    )


def danh_sach_xe(yeu_cau):
    """Trang danh sách xe có tìm kiếm, lọc đa tiêu chí và sắp xếp."""
    bo_loc = Xe.objects.filter(dang_kinh_doanh=True).select_related('hang_xe', 'loai_xe')

    tu_khoa = yeu_cau.GET.get('tu_khoa', '').strip()
    hang_slug = yeu_cau.GET.get('hang', '').strip()
    loai_slug = yeu_cau.GET.get('loai', '').strip()
    nhien_lieu = yeu_cau.GET.get('nhien_lieu', '').strip()
    hop_so = yeu_cau.GET.get('hop_so', '').strip()
    tinh_trang = yeu_cau.GET.get('tinh_trang', '').strip()
    muc_gia = yeu_cau.GET.get('muc_gia', '').strip()
    sap_xep = yeu_cau.GET.get('sap_xep', 'moi_nhat').strip()

    if tu_khoa:
        bo_loc = bo_loc.filter(
            Q(ten_xe__icontains=tu_khoa)
            | Q(hang_xe__ten_hang__icontains=tu_khoa)
            | Q(mo_ta_ngan__icontains=tu_khoa)
            | Q(dong_co__icontains=tu_khoa)
        )
    if hang_slug:
        bo_loc = bo_loc.filter(hang_xe__duong_dan=hang_slug)
    if loai_slug:
        bo_loc = bo_loc.filter(loai_xe__duong_dan=loai_slug)
    if nhien_lieu:
        bo_loc = bo_loc.filter(nhien_lieu=nhien_lieu)
    if hop_so:
        bo_loc = bo_loc.filter(hop_so=hop_so)
    if tinh_trang:
        bo_loc = bo_loc.filter(tinh_trang=tinh_trang)

    if muc_gia == 'duoi_700':
        bo_loc = bo_loc.filter(gia_ban__lt=700_000_000)
    elif muc_gia == '700_1500':
        bo_loc = bo_loc.filter(gia_ban__gte=700_000_000, gia_ban__lte=1_500_000_000)
    elif muc_gia == '1500_3000':
        bo_loc = bo_loc.filter(gia_ban__gt=1_500_000_000, gia_ban__lte=3_000_000_000)
    elif muc_gia == 'tren_3000':
        bo_loc = bo_loc.filter(gia_ban__gt=3_000_000_000)

    if sap_xep == 'gia_tang':
        bo_loc = bo_loc.order_by('gia_ban')
    elif sap_xep == 'gia_giam':
        bo_loc = bo_loc.order_by('-gia_ban')
    elif sap_xep == 'xem_nhieu':
        bo_loc = bo_loc.order_by('-luot_xem')
    else:
        bo_loc = bo_loc.order_by('-xe_noi_bat', '-ngay_tao')

    phan_trang = Paginator(bo_loc, 9)
    so_trang = yeu_cau.GET.get('trang', 1)
    trang_hien_tai = phan_trang.get_page(so_trang)

    return render(
        yeu_cau,
        'cua_hang_xe/danh_sach_xe.html',
        {
            'trang_xe': trang_hien_tai,
            'tu_khoa': tu_khoa,
            'hang_slug': hang_slug,
            'loai_slug': loai_slug,
            'nhien_lieu': nhien_lieu,
            'hop_so': hop_so,
            'tinh_trang': tinh_trang,
            'muc_gia': muc_gia,
            'sap_xep': sap_xep,
            'lua_chon_nhien_lieu': Xe.LUA_CHON_NHIEN_LIEU,
            'lua_chon_hop_so': Xe.LUA_CHON_HOP_SO,
            'lua_chon_tinh_trang': Xe.LUA_CHON_TINH_TRANG,
        },
    )


def chi_tiet_xe(yeu_cau, duong_dan):
    """Hiển thị thông số kỹ thuật, thư viện ảnh, đánh giá và xe liên quan."""
    xe = get_object_or_404(
        Xe.objects.select_related('hang_xe', 'loai_xe'),
        duong_dan=duong_dan,
        dang_kinh_doanh=True,
    )
    Xe.objects.filter(pk=xe.pk).update(luot_xem=F('luot_xem') + 1)
    xe.refresh_from_db()

    da_yeu_thich = False
    if yeu_cau.user.is_authenticated:
        da_yeu_thich = XeYeuThich.objects.filter(nguoi_dung=yeu_cau.user, xe=xe).exists()

    if yeu_cau.method == 'POST':
        if not yeu_cau.user.is_authenticated:
            messages.warning(yeu_cau, 'Vui lòng đăng nhập để gửi đánh giá xe.')
            return redirect('tai_khoan:dang_nhap')
        bieu_mau_danh_gia = BieuMauDanhGia(yeu_cau.POST)
        if bieu_mau_danh_gia.is_valid():
            danh_gia = bieu_mau_danh_gia.save(commit=False)
            danh_gia.xe = xe
            danh_gia.nguoi_dung = yeu_cau.user
            danh_gia.save()
            messages.success(yeu_cau, 'Cảm ơn bạn đã gửi đánh giá về mẫu xe này!')
            return redirect('cua_hang_xe:chi_tiet_xe', duong_dan=xe.duong_dan)
    else:
        bieu_mau_danh_gia = BieuMauDanhGia()

    xe_lien_quan = (
        Xe.objects.filter(dang_kinh_doanh=True)
        .filter(Q(hang_xe=xe.hang_xe) | Q(loai_xe=xe.loai_xe))
        .exclude(pk=xe.pk)
        .select_related('hang_xe', 'loai_xe')[:4]
    )

    return render(
        yeu_cau,
        'cua_hang_xe/chi_tiet_xe.html',
        {
            'xe': xe,
            'thu_vien_anh': xe.thu_vien_anh.all(),
            'cac_danh_gia': xe.cac_danh_gia.select_related('nguoi_dung'),
            'bieu_mau_danh_gia': bieu_mau_danh_gia,
            'da_yeu_thich': da_yeu_thich,
            'xe_lien_quan': xe_lien_quan,
        },
    )


def dat_lich_lai_thu(yeu_cau):
    """Đặt lịch hẹn lái thử xe tại showroom."""
    du_lieu_ban_dau = {}
    ma_xe = yeu_cau.GET.get('xe')
    if ma_xe:
        xe_chon = Xe.objects.filter(pk=ma_xe, dang_kinh_doanh=True).first()
        if xe_chon:
            du_lieu_ban_dau['xe'] = xe_chon

    if yeu_cau.user.is_authenticated:
        ho_so = getattr(yeu_cau.user, 'ho_so', None)
        du_lieu_ban_dau.setdefault('email', yeu_cau.user.email)
        if ho_so:
            du_lieu_ban_dau.setdefault('ho_ten', ho_so.lay_ten_hien_thi())
            du_lieu_ban_dau.setdefault('so_dien_thoai', ho_so.so_dien_thoai)

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauDatLichLaiThu(yeu_cau.POST)
        if bieu_mau.is_valid():
            lich_hen = bieu_mau.save(commit=False)
            if yeu_cau.user.is_authenticated:
                lich_hen.nguoi_dung = yeu_cau.user
            lich_hen.save()
            messages.success(
                yeu_cau,
                f'Đã tiếp nhận lịch hẹn lái thử {lich_hen.xe.ten_xe}. Nhân viên sẽ liên hệ xác nhận sớm nhất!',
            )
            return redirect('cua_hang_xe:dat_lich_lai_thu')
    else:
        bieu_mau = BieuMauDatLichLaiThu(initial=du_lieu_ban_dau)
        bieu_mau.fields['xe'].queryset = Xe.objects.filter(dang_kinh_doanh=True)

    return render(yeu_cau, 'cua_hang_xe/dat_lich_lai_thu.html', {'bieu_mau': bieu_mau})


@login_required
def danh_sach_yeu_thich(yeu_cau):
    """Hiển thị danh sách xe yêu thích của người dùng."""
    cac_muc = XeYeuThich.objects.filter(nguoi_dung=yeu_cau.user).select_related(
        'xe', 'xe__hang_xe', 'xe__loai_xe'
    )
    return render(yeu_cau, 'cua_hang_xe/yeu_thich.html', {'cac_muc_yeu_thich': cac_muc})


@login_required
def chuyen_doi_yeu_thich(yeu_cau, ma_xe):
    """Thêm hoặc bỏ một mẫu xe khỏi danh sách yêu thích."""
    xe = get_object_or_404(Xe, pk=ma_xe, dang_kinh_doanh=True)
    muc, da_tao = XeYeuThich.objects.get_or_create(nguoi_dung=yeu_cau.user, xe=xe)
    if da_tao:
        messages.success(yeu_cau, f'Đã thêm {xe.ten_xe} vào danh sách yêu thích.')
    else:
        muc.delete()
        messages.info(yeu_cau, f'Đã bỏ {xe.ten_xe} khỏi danh sách yêu thích.')

    trang_truoc = yeu_cau.META.get('HTTP_REFERER')
    if trang_truoc:
        return redirect(trang_truoc)
    return redirect('cua_hang_xe:chi_tiet_xe', duong_dan=xe.duong_dan)


def kiem_tra_quyen_quan_tri(yeu_cau):
    """Chỉ cho phép tài khoản quản trị tối cao (admin / superuser) can thiệp dữ liệu xe."""
    if not yeu_cau.user.is_superuser:
        messages.error(yeu_cau, 'Chỉ tài khoản admin mới có quyền truy cập mục Thêm xe và chỉnh sửa dữ liệu.')
        return False
    return True


def tao_duong_dan_duy_nhat(ten_xe, ma_xe_bo_qua=None):
    """Sinh slug duy nhất cho mẫu xe mới hoặc cập nhật."""
    slug_goc = chuyen_khong_dau_slug(ten_xe) or 'xe-o-to'
    slug_thu = slug_goc
    dem = 1
    while True:
        truy_van = Xe.objects.filter(duong_dan=slug_thu)
        if ma_xe_bo_qua:
            truy_van = truy_van.exclude(pk=ma_xe_bo_qua)
        if not truy_van.exists():
            return slug_thu
        dem += 1
        slug_thu = f'{slug_goc}-{dem}'


@login_required
def quan_ly_xe(yeu_cau):
    """Trang quản lý thêm xe, thêm loại/hãng xe và nhập số lượng tồn kho."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    danh_sach = Xe.objects.select_related('hang_xe', 'loai_xe').order_by('-ngay_tao')
    return render(
        yeu_cau,
        'cua_hang_xe/quan_ly_xe.html',
        {
            'danh_sach_xe': danh_sach,
            'bieu_mau_loai_xe': BieuMauThemLoaiXe(),
            'bieu_mau_hang_xe': BieuMauThemHangXe(),
        },
    )


@login_required
def nhap_them_so_luong(yeu_cau, ma_xe):
    """Cộng thêm số lượng tồn kho cho mẫu xe đã đăng."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    xe = get_object_or_404(Xe, pk=ma_xe)
    if yeu_cau.method == 'POST':
        try:
            so_luong_nhap = int(yeu_cau.POST.get('so_luong_nhap', 1))
        except (TypeError, ValueError):
            so_luong_nhap = 0
        if so_luong_nhap > 0:
            xe.so_luong_ton += so_luong_nhap
            xe.save(update_fields=['so_luong_ton'])
            messages.success(
                yeu_cau,
                f'Đã nhập thêm {so_luong_nhap} chiếc cho "{xe.ten_xe}" (Tồn kho mới: {xe.so_luong_ton}).',
            )
        else:
            messages.warning(yeu_cau, 'Số lượng nhập thêm phải lớn hơn 0.')
    return redirect('cua_hang_xe:quan_ly_xe')


@login_required
def them_loai_xe(yeu_cau):
    """Thêm loại xe mới (ví dụ: Coupe, Hatchback...) trực tiếp trên web."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauThemLoaiXe(yeu_cau.POST)
        if bieu_mau.is_valid():
            loai_moi = bieu_mau.save(commit=False)
            loai_moi.duong_dan = chuyen_khong_dau_slug(loai_moi.ten_loai) or 'loai-xe'
            loai_moi.save()
            messages.success(yeu_cau, f'Đã thêm loại xe mới: "{loai_moi.ten_loai}".')
        else:
            messages.error(yeu_cau, 'Không thể thêm loại xe (có thể tên loại xe đã tồn tại).')
    return redirect('cua_hang_xe:quan_ly_xe')


@login_required
def them_hang_xe(yeu_cau):
    """Thêm hãng xe mới trực tiếp trên web."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauThemHangXe(yeu_cau.POST)
        if bieu_mau.is_valid():
            hang_moi = bieu_mau.save(commit=False)
            hang_moi.duong_dan = chuyen_khong_dau_slug(hang_moi.ten_hang) or 'hang-xe'
            hang_moi.save()
            messages.success(yeu_cau, f'Đã thêm hãng xe mới: "{hang_moi.ten_hang}".')
        else:
            messages.error(yeu_cau, 'Không thể thêm hãng xe (có thể tên hãng đã tồn tại).')
    return redirect('cua_hang_xe:quan_ly_xe')


@login_required
def them_xe_moi(yeu_cau):
    """Thêm mẫu xe mới trực tiếp từ giao diện web."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauThemSuaXe(yeu_cau.POST, yeu_cau.FILES)
        if bieu_mau.is_valid():
            xe_moi = bieu_mau.save(commit=False)
            xe_moi.duong_dan = tao_duong_dan_duy_nhat(xe_moi.ten_xe)
            xe_moi.save()

            for anh_phu in yeu_cau.FILES.getlist('anh_phu'):
                HinhAnhXe.objects.create(xe=xe_moi, hinh_anh=anh_phu)

            messages.success(yeu_cau, f'Đã thêm mẫu xe "{xe_moi.ten_xe}" thành công!')
            return redirect('cua_hang_xe:quan_ly_xe')
    else:
        bieu_mau = BieuMauThemSuaXe()

    return render(
        yeu_cau,
        'cua_hang_xe/bieu_mau_xe.html',
        {'bieu_mau': bieu_mau, 'tieu_de_trang': 'Thêm xe mới', 'che_do_sua': False},
    )


@login_required
def sua_xe(yeu_cau, ma_xe):
    """Chỉnh sửa thông tin mẫu xe hiện có."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    xe = get_object_or_404(Xe, pk=ma_xe)
    if yeu_cau.method == 'POST':
        bieu_mau = BieuMauThemSuaXe(yeu_cau.POST, yeu_cau.FILES, instance=xe)
        if bieu_mau.is_valid():
            xe_da_luu = bieu_mau.save(commit=False)
            xe_da_luu.duong_dan = tao_duong_dan_duy_nhat(xe_da_luu.ten_xe, ma_xe_bo_qua=xe.pk)
            xe_da_luu.save()

            for anh_phu in yeu_cau.FILES.getlist('anh_phu'):
                HinhAnhXe.objects.create(xe=xe_da_luu, hinh_anh=anh_phu)

            messages.success(yeu_cau, f'Đã cập nhật thông tin xe "{xe_da_luu.ten_xe}".')
            return redirect('cua_hang_xe:quan_ly_xe')
    else:
        bieu_mau = BieuMauThemSuaXe(instance=xe)

    return render(
        yeu_cau,
        'cua_hang_xe/bieu_mau_xe.html',
        {'bieu_mau': bieu_mau, 'xe': xe, 'tieu_de_trang': f'Chỉnh sửa: {xe.ten_xe}', 'che_do_sua': True},
    )


@login_required
def xoa_xe(yeu_cau, ma_xe):
    """Xóa mẫu xe khỏi hệ thống."""
    if not kiem_tra_quyen_quan_tri(yeu_cau):
        return redirect('cua_hang_xe:trang_chu')

    xe = get_object_or_404(Xe, pk=ma_xe)
    if yeu_cau.method == 'POST':
        ten_xe = xe.ten_xe
        xe.delete()
        messages.info(yeu_cau, f'Đã xóa mẫu xe "{ten_xe}".')
    return redirect('cua_hang_xe:quan_ly_xe')
