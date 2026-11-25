from django.contrib.auth.models import User
from django.db import models

from cua_hang_xe.models import Xe


class GioHang(models.Model):
    """Giỏ hàng lưu trữ các xe khách hàng đã chọn."""

    nguoi_dung = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='gio_hang',
        verbose_name='Người dùng',
    )
    ma_phien = models.CharField('Mã phiên', max_length=64, null=True, blank=True, db_index=True)
    ngay_tao = models.DateTimeField('Ngày tạo', auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', auto_now=True)

    class Meta:
        verbose_name = 'Giỏ hàng'
        verbose_name_plural = 'Giỏ hàng'

    def __str__(self):
        chu_so_huu = self.nguoi_dung.username if self.nguoi_dung else f'Khách ({self.ma_phien})'
        return f'Giỏ hàng của {chu_so_huu}'

    def tong_so_luong(self):
        """Tổng số lượng xe trong giỏ hàng."""
        return sum(muc.so_luong for muc in self.cac_muc.all())

    def tong_tien(self):
        """Tổng thành tiền của tất cả xe trong giỏ hàng."""
        return sum(muc.thanh_tien() for muc in self.cac_muc.select_related('xe'))


class MucGioHang(models.Model):
    """Từng mẫu xe cụ thể nằm trong giỏ hàng."""

    gio_hang = models.ForeignKey(
        GioHang,
        on_delete=models.CASCADE,
        related_name='cac_muc',
        verbose_name='Giỏ hàng',
    )
    xe = models.ForeignKey(Xe, on_delete=models.CASCADE, verbose_name='Xe')
    so_luong = models.PositiveIntegerField('Số lượng', default=1)
    mau_da_chon = models.CharField('Màu sắc chọn', max_length=80, blank=True)
    ngay_them = models.DateTimeField('Ngày thêm', auto_now_add=True)

    class Meta:
        verbose_name = 'Mục giỏ hàng'
        verbose_name_plural = 'Mục giỏ hàng'

    def __str__(self):
        return f'{self.xe.ten_xe} x {self.so_luong}'

    def thanh_tien(self):
        """Thành tiền của mục giỏ hàng này."""
        return self.xe.lay_gia_hien_tai() * self.so_luong


class DonHang(models.Model):
    """Đơn đặt mua xe của khách hàng."""

    PHUONG_THUC_THANH_TOAN = [
        ('tien_mat', 'Thanh toán khi nhận xe (COD)'),
        ('chuyen_khoan', 'Chuyển khoản ngân hàng'),
        ('tra_gop', 'Đăng ký hỗ trợ trả góp ngân hàng'),
    ]

    PHUONG_THUC_NHAN_XE = [
        ('showroom', 'Nhận xe trực tiếp tại Showroom'),
        ('giao_tan_noi', 'Giao xe tận nơi bằng xe chuyên dụng'),
    ]

    TRANG_THAI_DON_HANG = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('dang_chuan_bi', 'Đang chuẩn bị xe & hồ sơ'),
        ('dang_giao', 'Đang giao xe'),
        ('hoan_thanh', 'Hoàn thành'),
        ('da_huy', 'Đã hủy'),
    ]

    ma_don_hang = models.CharField('Mã đơn hàng', max_length=25, unique=True)
    nguoi_dung = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cac_don_hang',
        verbose_name='Khách hàng',
    )
    ho_ten_nguoi_nhan = models.CharField('Họ tên người nhận', max_length=150)
    so_dien_thoai = models.CharField('Số điện thoại', max_length=20)
    email = models.EmailField('Email liên hệ')
    dia_chi_giao_xe = models.TextField('Địa chỉ giao xe')
    phuong_thuc_thanh_toan = models.CharField(
        'Phương thức thanh toán',
        max_length=30,
        choices=PHUONG_THUC_THANH_TOAN,
        default='chuyen_khoan',
    )
    phuong_thuc_nhan_xe = models.CharField(
        'Phương thức nhận xe',
        max_length=30,
        choices=PHUONG_THUC_NHAN_XE,
        default='showroom',
    )
    tong_tien = models.DecimalField('Tổng tiền xe (VNĐ)', max_digits=15, decimal_places=0)
    phi_van_chuyen = models.DecimalField('Phí vận chuyển (VNĐ)', max_digits=15, decimal_places=0, default=0)
    trang_thai = models.CharField(
        'Trạng thái đơn hàng',
        max_length=30,
        choices=TRANG_THAI_DON_HANG,
        default='cho_xac_nhan',
    )
    da_thanh_toan = models.BooleanField('Đã thanh toán', default=False)
    ghi_chu = models.TextField('Ghi chú đơn hàng', blank=True)
    ngay_dat = models.DateTimeField('Ngày đặt hàng', auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', auto_now=True)

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Danh sách đơn hàng'
        ordering = ['-ngay_dat']

    def __str__(self):
        return f'{self.ma_don_hang} - {self.ho_ten_nguoi_nhan}'

    def tong_thanh_toan(self):
        """Tổng số tiền khách hàng cần thanh toán bao gồm phí vận chuyển."""
        return self.tong_tien + self.phi_van_chuyen

    def co_the_huy(self):
        """Chỉ cho phép hủy đơn khi đơn chưa được giao hoặc hoàn thành."""
        return self.trang_thai in ('cho_xac_nhan', 'da_xac_nhan')


class ChiTietDonHang(models.Model):
    """Thông tin từng mẫu xe thuộc đơn hàng."""

    don_hang = models.ForeignKey(
        DonHang,
        on_delete=models.CASCADE,
        related_name='chi_tiet',
        verbose_name='Đơn hàng',
    )
    xe = models.ForeignKey(
        Xe,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Xe',
    )
    ten_xe = models.CharField('Tên xe', max_length=200)
    don_gia = models.DecimalField('Đơn giá (VNĐ)', max_digits=15, decimal_places=0)
    so_luong = models.PositiveIntegerField('Số lượng', default=1)
    mau_xe = models.CharField('Màu xe', max_length=80, blank=True)

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        return f'{self.ten_xe} x {self.so_luong}'

    def thanh_tien(self):
        """Thành tiền của dòng chi tiết đơn hàng."""
        return self.don_gia * self.so_luong
