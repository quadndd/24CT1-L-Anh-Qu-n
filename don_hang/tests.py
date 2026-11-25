from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cua_hang_xe.models import HangXe, LoaiXe, Xe
from don_hang.models import DonHang


class KiemThuHeThongBanXe(TestCase):
    """Kiểm thử toàn bộ luồng nghiệp vụ chính của website bán xe."""

    def setUp(self):
        self.hang = HangXe.objects.create(
            ten_hang='VinFast',
            duong_dan='vinfast',
            quoc_gia='Việt Nam',
        )
        self.loai = LoaiXe.objects.create(
            ten_loai='SUV',
            duong_dan='suv',
        )
        self.xe = Xe.objects.create(
            ten_xe='VF 8 Test',
            duong_dan='vf-8-test',
            hang_xe=self.hang,
            loai_xe=self.loai,
            gia_ban=1_200_000_000,
            gia_khuyen_mai=1_100_000_000,
            nam_san_xuat=2026,
            dong_co='2 Motor điện',
            so_luong_ton=5,
            mo_ta_ngan='Xe điện thông minh',
            mo_ta_chi_tiet='Chi tiết xe điện thông minh',
            xe_noi_bat=True,
        )

    def test_cac_trang_cong_khai(self):
        self.assertEqual(self.client.get(reverse('cua_hang_xe:trang_chu')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cua_hang_xe:danh_sach_xe')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('cua_hang_xe:chi_tiet_xe', args=[self.xe.duong_dan])).status_code,
            200,
        )
        self.assertEqual(self.client.get(reverse('cua_hang_xe:dat_lich_lai_thu')).status_code, 200)

    def test_dang_ky_gio_hang_va_dat_hang(self):
        # Thêm xe vào giỏ trước khi đăng nhập (giỏ hàng phiên)
        phan_hoi_them = self.client.post(
            reverse('don_hang:them_vao_gio', args=[self.xe.pk]),
            {'so_luong': 2, 'mau_da_chon': 'Đen'},
        )
        self.assertEqual(phan_hoi_them.status_code, 302)

        # Đăng ký tài khoản mới -> tự động gộp giỏ hàng và đăng nhập
        phan_hoi_dk = self.client.post(
            reverse('tai_khoan:dang_ky'),
            {
                'username': 'khachhang1',
                'email': 'khach1@example.com',
                'ho_va_ten': 'Nguyễn Văn Khách',
                'so_dien_thoai': '0912345678',
                'dia_chi': 'Hà Nội',
                'password1': 'MatKhauManh@123',
                'password2': 'MatKhauManh@123',
            },
        )
        self.assertEqual(phan_hoi_dk.status_code, 302)
        self.assertTrue(User.objects.filter(username='khachhang1').exists())

        # Kiểm tra giỏ hàng vẫn giữ 2 xe sau khi gộp
        phan_hoi_gio = self.client.get(reverse('don_hang:xem_gio_hang'))
        self.assertContains(phan_hoi_gio, 'VF 8 Test')

        # Đặt hàng
        phan_hoi_dat = self.client.post(
            reverse('don_hang:dat_hang'),
            {
                'ho_ten_nguoi_nhan': 'Nguyễn Văn Khách',
                'so_dien_thoai': '0912345678',
                'email': 'khach1@example.com',
                'dia_chi_giao_xe': '123 Cầu Giấy, Hà Nội',
                'phuong_thuc_nhan_xe': 'giao_tan_noi',
                'phuong_thuc_thanh_toan': 'chuyen_khoan',
                'ghi_chu': 'Giao buổi sáng',
            },
        )
        self.assertEqual(phan_hoi_dat.status_code, 302)

        don_hang = DonHang.objects.first()
        self.assertIsNotNone(don_hang)
        self.assertEqual(don_hang.tong_tien, 2_200_000_000)
        self.assertEqual(don_hang.phi_van_chuyen, 5_000_000)

        self.xe.refresh_from_db()
        self.assertEqual(self.xe.so_luong_ton, 3)

        # Hủy đơn hàng -> hoàn lại tồn kho
        phan_hoi_huy = self.client.post(
            reverse('don_hang:huy_don_hang', args=[don_hang.ma_don_hang])
        )
        self.assertEqual(phan_hoi_huy.status_code, 302)
        don_hang.refresh_from_db()
        self.xe.refresh_from_db()
        self.assertEqual(don_hang.trang_thai, 'da_huy')
        self.assertEqual(self.xe.so_luong_ton, 5)

    def test_quan_ly_them_sua_xoa_xe(self):
        # Người dùng thường (kể cả staff không phải superuser) không được phép vào mục Thêm xe
        User.objects.create_user('khachthuong', 'thuong@example.com', 'MatKhau@123', is_staff=True)
        self.client.login(username='khachthuong', password='MatKhau@123')
        phan_hoi_chan = self.client.get(reverse('cua_hang_xe:them_xe_moi'))
        self.assertEqual(phan_hoi_chan.status_code, 302)

        # Tài khoản staff/admin thêm, sửa, xóa xe thành công
        User.objects.create_superuser('quantri', 'admin@example.com', 'MatKhau@123')
        self.client.login(username='quantri', password='MatKhau@123')
        self.assertEqual(self.client.get(reverse('cua_hang_xe:quan_ly_xe')).status_code, 200)

        phan_hoi_them = self.client.post(
            reverse('cua_hang_xe:them_xe_moi'),
            {
                'ten_xe': 'VinFast VF 7 Plus',
                'hang_xe': self.hang.pk,
                'loai_xe': self.loai.pk,
                'gia_ban': 999_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Trắng',
                'dong_co': '2 Motor điện',
                'hop_so': 'don_cap',
                'nhien_lieu': 'dien',
                'so_cho_ngoi': 5,
                'xuat_xu': 'Việt Nam',
                'tinh_trang': 'xe_moi',
                'so_luong_ton': 4,
                'mo_ta_ngan': 'SUV điện cỡ C',
                'mo_ta_chi_tiet': 'Mô tả chi tiết VF 7 Plus',
                'dang_kinh_doanh': 'on',
            },
        )
        self.assertEqual(phan_hoi_them.status_code, 302)
        xe_moi = Xe.objects.get(ten_xe='VinFast VF 7 Plus')
        self.assertEqual(xe_moi.duong_dan, 'vinfast-vf-7-plus')

        # Sửa xe
        phan_hoi_sua = self.client.post(
            reverse('cua_hang_xe:sua_xe', args=[xe_moi.pk]),
            {
                'ten_xe': 'VinFast VF 7 Plus 2026',
                'hang_xe': self.hang.pk,
                'loai_xe': self.loai.pk,
                'gia_ban': 950_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Đen',
                'dong_co': '2 Motor điện',
                'hop_so': 'don_cap',
                'nhien_lieu': 'dien',
                'so_cho_ngoi': 5,
                'xuat_xu': 'Việt Nam',
                'tinh_trang': 'xe_moi',
                'so_luong_ton': 6,
                'mo_ta_ngan': 'SUV điện cỡ C mới',
                'mo_ta_chi_tiet': 'Mô tả chi tiết VF 7 Plus 2026',
                'dang_kinh_doanh': 'on',
            },
        )
        self.assertEqual(phan_hoi_sua.status_code, 302)
        xe_moi.refresh_from_db()
        self.assertEqual(xe_moi.gia_ban, 950_000_000)

        # Nhập thêm số lượng tồn kho
        phan_hoi_nhap = self.client.post(
            reverse('cua_hang_xe:nhap_them_so_luong', args=[xe_moi.pk]),
            {'so_luong_nhap': 5},
        )
        self.assertEqual(phan_hoi_nhap.status_code, 302)
        xe_moi.refresh_from_db()
        self.assertEqual(xe_moi.so_luong_ton, 11)

        # Thêm loại xe và hãng xe mới
        self.client.post(
            reverse('cua_hang_xe:them_loai_xe'),
            {'ten_loai': 'Coupe', 'mo_ta': 'Xe thể thao 2 cửa'},
        )
        self.assertTrue(LoaiXe.objects.filter(ten_loai='Coupe').exists())

        self.client.post(
            reverse('cua_hang_xe:them_hang_xe'),
            {'ten_hang': 'BMW', 'quoc_gia': 'Đức', 'mo_ta': 'Xe sang Đức'},
        )
        self.assertTrue(HangXe.objects.filter(ten_hang='BMW').exists())

        # Xóa xe
        phan_hoi_xoa = self.client.post(reverse('cua_hang_xe:xoa_xe', args=[xe_moi.pk]))
        self.assertEqual(phan_hoi_xoa.status_code, 302)
        self.assertFalse(Xe.objects.filter(pk=xe_moi.pk).exists())
