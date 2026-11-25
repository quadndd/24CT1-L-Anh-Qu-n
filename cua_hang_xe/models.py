from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class HangXe(models.Model):
    """Thông tin hãng sản xuất xe ô tô."""

    ten_hang = models.CharField('Tên hãng xe', max_length=100, unique=True)
    duong_dan = models.SlugField('Đường dẫn', max_length=120, unique=True)
    quoc_gia = models.CharField('Quốc gia', max_length=80, blank=True)
    mo_ta = models.TextField('Mô tả', blank=True)
    logo = models.ImageField('Logo hãng', upload_to='hang_xe/', null=True, blank=True)

    class Meta:
        verbose_name = 'Hãng xe'
        verbose_name_plural = 'Hãng xe'
        ordering = ['ten_hang']

    def __str__(self):
        return self.ten_hang


class LoaiXe(models.Model):
    """Phân loại dòng xe (SUV, Sedan, Hatchback, Bán tải, Xe điện...)."""

    ten_loai = models.CharField('Tên loại xe', max_length=100, unique=True)
    duong_dan = models.SlugField('Đường dẫn', max_length=120, unique=True)
    mo_ta = models.TextField('Mô tả', blank=True)

    class Meta:
        verbose_name = 'Loại xe'
        verbose_name_plural = 'Loại xe'
        ordering = ['ten_loai']

    def __str__(self):
        return self.ten_loai


class Xe(models.Model):
    """Thông tin chi tiết một mẫu xe đang kinh doanh."""

    LUA_CHON_HOP_SO = [
        ('tu_dong', 'Số tự động'),
        ('so_san', 'Số sàn'),
        ('cvt', 'Vô cấp CVT'),
        ('don_cap', 'Đơn cấp (Xe điện)'),
    ]

    LUA_CHON_NHIEN_LIEU = [
        ('xang', 'Xăng'),
        ('dau', 'Dầu Diesel'),
        ('dien', 'Điện'),
        ('hybrid', 'Hybrid'),
    ]

    LUA_CHON_TINH_TRANG = [
        ('xe_moi', 'Xe mới 100%'),
        ('xe_luot', 'Xe lướt / Đã qua sử dụng'),
    ]

    ten_xe = models.CharField('Tên xe', max_length=200)
    duong_dan = models.SlugField('Đường dẫn', max_length=220, unique=True)
    hang_xe = models.ForeignKey(
        HangXe,
        on_delete=models.CASCADE,
        related_name='danh_sach_xe',
        verbose_name='Hãng xe',
    )
    loai_xe = models.ForeignKey(
        LoaiXe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='danh_sach_xe',
        verbose_name='Loại xe',
    )
    gia_ban = models.DecimalField('Giá niêm yết (VNĐ)', max_digits=15, decimal_places=0)
    gia_khuyen_mai = models.DecimalField(
        'Giá khuyến mãi (VNĐ)',
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
    )
    nam_san_xuat = models.PositiveIntegerField('Năm sản xuất', default=2026)
    mau_sac = models.CharField('Màu sắc ngoại thất', max_length=100, default='Trắng ngọc trai')
    dong_co = models.CharField('Động cơ', max_length=120)
    hop_so = models.CharField('Hộp số', max_length=30, choices=LUA_CHON_HOP_SO, default='tu_dong')
    nhien_lieu = models.CharField('Nhiên liệu', max_length=30, choices=LUA_CHON_NHIEN_LIEU, default='xang')
    so_cho_ngoi = models.PositiveSmallIntegerField('Số chỗ ngồi', default=5)
    cong_suat = models.CharField('Công suất tối đa', max_length=100, blank=True)
    xuat_xu = models.CharField('Xuất xứ', max_length=100, default='Việt Nam')
    tinh_trang = models.CharField('Tình trạng', max_length=30, choices=LUA_CHON_TINH_TRANG, default='xe_moi')
    so_luong_ton = models.PositiveIntegerField('Số lượng tồn kho', default=5)
    mo_ta_ngan = models.CharField('Mô tả ngắn', max_length=300)
    mo_ta_chi_tiet = models.TextField('Mô tả chi tiết')
    hinh_anh_chinh = models.ImageField('Hình ảnh chính', upload_to='xe/', null=True, blank=True)
    duong_dan_anh_mau = models.CharField(
        'Đường dẫn ảnh mẫu tĩnh',
        max_length=255,
        blank=True,
        help_text='Dùng ảnh tĩnh trong thư mục tai_nguyen nếu chưa tải ảnh lên.',
    )
    xe_noi_bat = models.BooleanField('Xe nổi bật', default=False)
    dang_kinh_doanh = models.BooleanField('Đang kinh doanh', default=True)
    luot_xem = models.PositiveIntegerField('Lượt xem', default=0)
    ngay_tao = models.DateTimeField('Ngày tạo', auto_now_add=True)

    class Meta:
        verbose_name = 'Xe ô tô'
        verbose_name_plural = 'Danh sách xe'
        ordering = ['-xe_noi_bat', '-ngay_tao']

    def __str__(self):
        return f'{self.hang_xe.ten_hang} {self.ten_xe} ({self.nam_san_xuat})'

    def lay_gia_hien_tai(self):
        """Trả về giá bán thực tế (ưu tiên giá khuyến mãi nếu hợp lệ)."""
        if self.gia_khuyen_mai and 0 < self.gia_khuyen_mai < self.gia_ban:
            return self.gia_khuyen_mai
        return self.gia_ban

    def co_giam_gia(self):
        """Kiểm tra xe có đang được giảm giá hay không."""
        return bool(self.gia_khuyen_mai and 0 < self.gia_khuyen_mai < self.gia_ban)

    def phan_tram_giam(self):
        """Tính phần trăm giảm giá làm tròn."""
        if not self.co_giam_gia():
            return 0
        ti_le = (self.gia_ban - self.gia_khuyen_mai) * 100 / self.gia_ban
        return int(round(ti_le))

    def con_hang(self):
        """Kiểm tra xe còn hàng trong kho."""
        return self.dang_kinh_doanh and self.so_luong_ton > 0

    def diem_trung_binh(self):
        """Tính điểm đánh giá trung bình của xe."""
        ket_qua = self.cac_danh_gia.aggregate(trung_binh=Avg('so_sao'))
        diem = ket_qua.get('trung_binh')
        return round(diem, 1) if diem else 0


class HinhAnhXe(models.Model):
    """Thư viện ảnh phụ của từng mẫu xe."""

    xe = models.ForeignKey(
        Xe,
        on_delete=models.CASCADE,
        related_name='thu_vien_anh',
        verbose_name='Xe',
    )
    hinh_anh = models.ImageField('Hình ảnh', upload_to='xe/thu_vien/')
    chu_thich = models.CharField('Chú thích', max_length=150, blank=True)

    class Meta:
        verbose_name = 'Hình ảnh xe'
        verbose_name_plural = 'Thư viện hình ảnh xe'

    def __str__(self):
        return f'Ảnh của {self.xe.ten_xe}'


class DanhGiaXe(models.Model):
    """Đánh giá và nhận xét của khách hàng về mẫu xe."""

    xe = models.ForeignKey(
        Xe,
        on_delete=models.CASCADE,
        related_name='cac_danh_gia',
        verbose_name='Xe',
    )
    nguoi_dung = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cac_danh_gia_xe',
        verbose_name='Người đánh giá',
    )
    so_sao = models.PositiveSmallIntegerField(
        'Số sao',
        choices=[(i, f'{i} sao') for i in range(1, 6)],
        default=5,
    )
    noi_dung = models.TextField('Nội dung nhận xét')
    ngay_danh_gia = models.DateTimeField('Ngày đánh giá', auto_now_add=True)

    class Meta:
        verbose_name = 'Đánh giá xe'
        verbose_name_plural = 'Đánh giá xe'
        ordering = ['-ngay_danh_gia']

    def __str__(self):
        return f'{self.nguoi_dung.username} - {self.xe.ten_xe} ({self.so_sao} sao)'


class XeYeuThich(models.Model):
    """Danh sách xe yêu thích của người dùng."""

    nguoi_dung = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='xe_yeu_thich',
        verbose_name='Người dùng',
    )
    xe = models.ForeignKey(
        Xe,
        on_delete=models.CASCADE,
        related_name='luot_yeu_thich',
        verbose_name='Xe',
    )
    ngay_them = models.DateTimeField('Ngày thêm', auto_now_add=True)

    class Meta:
        verbose_name = 'Xe yêu thích'
        verbose_name_plural = 'Xe yêu thích'
        unique_together = ('nguoi_dung', 'xe')

    def __str__(self):
        return f'{self.nguoi_dung.username} thích {self.xe.ten_xe}'


class LichLaiThu(models.Model):
    """Lịch hẹn lái thử xe tại showroom."""

    TRANG_THAI_LICH = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('da_hoan_thanh', 'Đã hoàn thành'),
        ('da_huy', 'Đã hủy'),
    ]

    nguoi_dung = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lich_lai_thu',
        verbose_name='Tài khoản',
    )
    xe = models.ForeignKey(
        Xe,
        on_delete=models.CASCADE,
        related_name='cac_lich_lai_thu',
        verbose_name='Mẫu xe lái thử',
    )
    ho_ten = models.CharField('Họ và tên', max_length=150)
    so_dien_thoai = models.CharField('Số điện thoại', max_length=20)
    email = models.EmailField('Email', blank=True)
    ngay_hen = models.DateField('Ngày hẹn')
    gio_hen = models.TimeField('Giờ hẹn')
    ghi_chu = models.TextField('Ghi chú thêm', blank=True)
    trang_thai = models.CharField(
        'Trạng thái',
        max_length=30,
        choices=TRANG_THAI_LICH,
        default='cho_xac_nhan',
    )
    ngay_tao = models.DateTimeField('Ngày đặt lịch', auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch lái thử'
        verbose_name_plural = 'Danh sách lịch lái thử'
        ordering = ['-ngay_tao']

    def __str__(self):
        return f'{self.ho_ten} - {self.xe.ten_xe} ({self.ngay_hen})'
