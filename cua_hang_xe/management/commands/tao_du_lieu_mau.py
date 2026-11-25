from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from cua_hang_xe.models import HangXe, LoaiXe, Xe
from cua_hang_xe.tien_ich import chuyen_khong_dau_slug


def tao_anh_svg_xe(ten_tep, tieu_de, mau_nen, mau_xe):
    """Tạo ảnh minh họa SVG sắc nét cho xe trong thư mục tĩnh."""
    thu_muc_anh = Path(settings.BASE_DIR) / 'tai_nguyen' / 'hinh_anh'
    thu_muc_anh.mkdir(parents=True, exist_ok=True)
    noi_dung_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="nen" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{mau_nen}"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="800" height="450" fill="url(#nen)"/>
  <ellipse cx="400" cy="355" rx="280" ry="26" fill="rgba(0,0,0,0.45)"/>
  <path d="M160 285 L210 215 Q245 180 320 175 L485 175 Q555 180 600 220 L655 245 Q675 260 670 290 L150 295 Z" fill="{mau_xe}"/>
  <path d="M240 220 L275 188 L470 188 L535 220 Z" fill="#cbd5e1" opacity="0.88"/>
  <circle cx="255" cy="300" r="46" fill="#111827"/>
  <circle cx="255" cy="300" r="24" fill="#94a3b8"/>
  <circle cx="565" cy="300" r="46" fill="#111827"/>
  <circle cx="565" cy="300" r="24" fill="#94a3b8"/>
  <rect x="625" y="250" width="32" height="12" rx="6" fill="#fef08a"/>
  <rect x="152" y="255" width="24" height="12" rx="4" fill="#ef4444"/>
  <text x="40" y="65" fill="#ffffff" font-family="Segoe UI, Arial" font-size="30" font-weight="bold">{tieu_de}</text>
  <text x="40" y="98" fill="#cbd5e1" font-family="Segoe UI, Arial" font-size="18">AutoViet Showroom Chính Hãng</text>
</svg>'''
    (thu_muc_anh / ten_tep).write_text(noi_dung_svg, encoding='utf-8')
    return f'hinh_anh/{ten_tep}'


class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho website bán xe AutoViet'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@autoviet.vn', 'Admin@12345')
            self.stdout.write(self.style.SUCCESS('Đã tạo tài khoản quản trị: admin / Admin@12345'))

        danh_sach_hang = [
            ('VinFast', 'Việt Nam', 'Thương hiệu ô tô điện thông minh hàng đầu Việt Nam.'),
            ('Toyota', 'Nhật Bản', 'Bền bỉ, tiết kiệm nhiên liệu và giữ giá hàng đầu.'),
            ('Mazda', 'Nhật Bản', 'Thiết kế KODO sang trọng cùng cảm giác lái thể thao.'),
            ('Hyundai', 'Hàn Quốc', 'Công nghệ hiện đại, tiện nghi vượt trội trong phân khúc.'),
            ('Mercedes-Benz', 'Đức', 'Đẳng cấp xe sang với công nghệ an toàn hàng đầu.'),
            ('Ford', 'Mỹ', 'Mạnh mẽ, cơ bắp với dòng bán tải và SUV đa dụng.'),
        ]
        ban_do_hang = {}
        for ten, quoc_gia, mo_ta in danh_sach_hang:
            hang, _ = HangXe.objects.get_or_create(
                duong_dan=chuyen_khong_dau_slug(ten),
                defaults={'ten_hang': ten, 'quoc_gia': quoc_gia, 'mo_ta': mo_ta},
            )
            ban_do_hang[ten] = hang

        danh_sach_loai = [
            ('SUV', 'Xe gầm cao đa dụng, không gian rộng rãi.'),
            ('Sedan', 'Xe du lịch 4 cửa thanh lịch, êm ái.'),
            ('Xe điện', 'Xe thuần điện thân thiện môi trường, vận hành mượt mà.'),
            ('Bán tải', 'Xe đa dụng mạnh mẽ, chuyên chở linh hoạt.'),
            ('MPV', 'Xe gia đình 7 chỗ rộng rãi, tiện nghi.'),
        ]
        ban_do_loai = {}
        for ten, mo_ta in danh_sach_loai:
            loai, _ = LoaiXe.objects.get_or_create(
                duong_dan=chuyen_khong_dau_slug(ten),
                defaults={'ten_loai': ten, 'mo_ta': mo_ta},
            )
            ban_do_loai[ten] = loai

        danh_sach_xe_mau = [
            {
                'ten_xe': 'VinFast VF 8 Plus',
                'hang': 'VinFast',
                'loai': 'Xe điện',
                'gia_ban': 1_290_000_000,
                'gia_khuyen_mai': 1_190_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Xanh rêu Deep Ocean',
                'dong_co': '2 Motor điện AWD',
                'hop_so': 'don_cap',
                'nhien_lieu': 'dien',
                'so_cho_ngoi': 5,
                'cong_suat': '402 mã lực',
                'xuat_xu': 'Việt Nam',
                'so_luong_ton': 8,
                'xe_noi_bat': True,
                'mau_nen': '#1e3a8a',
                'mau_xe': '#38bdf8',
                'mo_ta_ngan': 'SUV điện cỡ trung thông minh, tầm hoạt động hơn 470 km mỗi lần sạc.',
                'mo_ta_chi_tiet': 'VinFast VF 8 Plus trang bị hệ dẫn động 4 bánh toàn thời gian, gói hỗ trợ lái nâng cao ADAS, màn hình trung tâm 15.6 inch và bảo hành 10 năm.',
            },
            {
                'ten_xe': 'VinFast VF 9 Eco',
                'hang': 'VinFast',
                'loai': 'Xe điện',
                'gia_ban': 1_589_000_000,
                'gia_khuyen_mai': None,
                'nam_san_xuat': 2026,
                'mau_sac': 'Đỏ Crimson',
                'dong_co': '2 Motor điện AWD',
                'hop_so': 'don_cap',
                'nhien_lieu': 'dien',
                'so_cho_ngoi': 7,
                'cong_suat': '402 mã lực',
                'xuat_xu': 'Việt Nam',
                'so_luong_ton': 5,
                'xe_noi_bat': True,
                'mau_nen': '#450a0a',
                'mau_xe': '#ef4444',
                'mo_ta_ngan': 'SUV điện hạng E 7 chỗ ngồi đẳng cấp, không gian thương gia.',
                'mo_ta_chi_tiet': 'VinFast VF 9 mang lại không gian nội thất rộng rãi hàng đầu phân khúc, cửa sổ trời toàn cảnh và hệ thống treo khí nén êm ái.',
            },
            {
                'ten_xe': 'Toyota Camry 2.5Q',
                'hang': 'Toyota',
                'loai': 'Sedan',
                'gia_ban': 1_405_000_000,
                'gia_khuyen_mai': 1_360_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Đen ánh kim',
                'dong_co': '2.5L Dynamic Force',
                'hop_so': 'tu_dong',
                'nhien_lieu': 'xang',
                'so_cho_ngoi': 5,
                'cong_suat': '207 mã lực',
                'xuat_xu': 'Thái Lan',
                'so_luong_ton': 6,
                'xe_noi_bat': True,
                'mau_nen': '#1e293b',
                'mau_xe': '#e2e8f0',
                'mo_ta_ngan': 'Sedan hạng D chuẩn mực doanh nhân, vận hành êm ái và bền bỉ.',
                'mo_ta_chi_tiet': 'Toyota Camry 2.5Q tích hợp gói an toàn Toyota Safety Sense, ghế da cao cấp chỉnh điện đa hướng và hệ thống âm thanh JBL.',
            },
            {
                'ten_xe': 'Toyota Corolla Cross HEV',
                'hang': 'Toyota',
                'loai': 'SUV',
                'gia_ban': 905_000_000,
                'gia_khuyen_mai': 875_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Trắng ngọc trai',
                'dong_co': '1.8L Hybrid',
                'hop_so': 'cvt',
                'nhien_lieu': 'hybrid',
                'so_cho_ngoi': 5,
                'cong_suat': '122 mã lực',
                'xuat_xu': 'Thái Lan',
                'so_luong_ton': 10,
                'xe_noi_bat': False,
                'mau_nen': '#064e3b',
                'mau_xe': '#f8fafc',
                'mo_ta_ngan': 'SUV đô thị Hybrid siêu tiết kiệm nhiên liệu chỉ 4.2L/100km.',
                'mo_ta_chi_tiet': 'Toyota Corolla Cross HEV kết hợp động cơ xăng và điện mượt mà, trang bị camera 360 độ và cửa sổ trời toàn cảnh.',
            },
            {
                'ten_xe': 'Mazda CX-5 2.0 Premium',
                'hang': 'Mazda',
                'loai': 'SUV',
                'gia_ban': 829_000_000,
                'gia_khuyen_mai': 799_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Đỏ Soul Red Crystal',
                'dong_co': '2.0L SkyActiv-G',
                'hop_so': 'tu_dong',
                'nhien_lieu': 'xang',
                'so_cho_ngoi': 5,
                'cong_suat': '154 mã lực',
                'xuat_xu': 'Việt Nam',
                'so_luong_ton': 12,
                'xe_noi_bat': True,
                'mau_nen': '#7f1d1d',
                'mau_xe': '#dc2626',
                'mo_ta_ngan': 'Mẫu SUV 5 chỗ bán chạy hàng đầu với thiết kế KODO tinh tế.',
                'mo_ta_chi_tiet': 'Mazda CX-5 trang bị màn hình HUD, âm thanh 10 loa Bose, hệ thống kiểm soát gia tốc GVC Plus và gói an toàn i-Activsense.',
            },
            {
                'ten_xe': 'Hyundai Santa Fe Calligraphy',
                'hang': 'Hyundai',
                'loai': 'SUV',
                'gia_ban': 1_365_000_000,
                'gia_khuyen_mai': None,
                'nam_san_xuat': 2026,
                'mau_sac': 'Xám titan',
                'dong_co': '2.5L Turbo GDI',
                'hop_so': 'tu_dong',
                'nhien_lieu': 'xang',
                'so_cho_ngoi': 7,
                'cong_suat': '281 mã lực',
                'xuat_xu': 'Việt Nam',
                'so_luong_ton': 7,
                'xe_noi_bat': True,
                'mau_nen': '#312e81',
                'mau_xe': '#94a3b8',
                'mo_ta_ngan': 'SUV 7 chỗ thế hệ mới với diện mạo vuông vức đầy uy lực.',
                'mo_ta_chi_tiet': 'Hyundai Santa Fe Calligraphy sở hữu cụm màn hình cong 12.3 inch kép, ghế thư giãn không trọng lực và hệ dẫn động HTRAC.',
            },
            {
                'ten_xe': 'Mercedes-Benz C300 AMG',
                'hang': 'Mercedes-Benz',
                'loai': 'Sedan',
                'gia_ban': 2_099_000_000,
                'gia_khuyen_mai': 1_999_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Trắng Polar',
                'dong_co': '2.0L Turbo Mild-Hybrid',
                'hop_so': 'tu_dong',
                'nhien_lieu': 'hybrid',
                'so_cho_ngoi': 5,
                'cong_suat': '258 mã lực',
                'xuat_xu': 'Việt Nam',
                'so_luong_ton': 4,
                'xe_noi_bat': True,
                'mau_nen': '#0f172a',
                'mau_xe': '#f1f5f9',
                'mo_ta_ngan': 'Sedan hạng sang thể thao với đèn Digital Light và nội thất S-Class thu nhỏ.',
                'mo_ta_chi_tiet': 'Mercedes-Benz C300 AMG mang lại trải nghiệm sang trọng với hệ thống MBUX thế hệ 2, loa Burmester 3D và đèn viền nội thất 64 màu.',
            },
            {
                'ten_xe': 'Ford Ranger Wildtrak',
                'hang': 'Ford',
                'loai': 'Bán tải',
                'gia_ban': 979_000_000,
                'gia_khuyen_mai': 945_000_000,
                'nam_san_xuat': 2026,
                'mau_sac': 'Vàng Luxe',
                'dong_co': '2.0L Bi-Turbo Diesel',
                'hop_so': 'tu_dong',
                'nhien_lieu': 'dau',
                'so_cho_ngoi': 5,
                'cong_suat': '210 mã lực',
                'xuat_xu': 'Việt Nam',
                'so_luong_ton': 9,
                'xe_noi_bat': False,
                'mau_nen': '#78350f',
                'mau_xe': '#f59e0b',
                'mo_ta_ngan': 'Vua bán tải với khả năng off-road vượt trội và tiện nghi như SUV.',
                'mo_ta_chi_tiet': 'Ford Ranger Wildtrak trang bị hộp số tự động 10 cấp, màn hình giải trí đặt dọc 12 inch và camera 360 độ.',
            },
        ]

        dem_xe = 0
        for du_lieu in danh_sach_xe_mau:
            duong_dan = chuyen_khong_dau_slug(du_lieu['ten_xe'])
            duong_dan_anh_that = Path(settings.BASE_DIR) / 'tai_nguyen' / 'hinh_anh' / f'{duong_dan}.jpg'
            if duong_dan_anh_that.exists():
                duong_dan_anh = f'hinh_anh/{duong_dan}.jpg'
            else:
                duong_dan_anh = tao_anh_svg_xe(
                    f'{duong_dan}.svg',
                    du_lieu['ten_xe'],
                    du_lieu['mau_nen'],
                    du_lieu['mau_xe'],
                )
            xe, da_tao = Xe.objects.get_or_create(
                duong_dan=duong_dan,
                defaults={
                    'ten_xe': du_lieu['ten_xe'],
                    'hang_xe': ban_do_hang[du_lieu['hang']],
                    'loai_xe': ban_do_loai[du_lieu['loai']],
                    'gia_ban': du_lieu['gia_ban'],
                    'gia_khuyen_mai': du_lieu['gia_khuyen_mai'],
                    'nam_san_xuat': du_lieu['nam_san_xuat'],
                    'mau_sac': du_lieu['mau_sac'],
                    'dong_co': du_lieu['dong_co'],
                    'hop_so': du_lieu['hop_so'],
                    'nhien_lieu': du_lieu['nhien_lieu'],
                    'so_cho_ngoi': du_lieu['so_cho_ngoi'],
                    'cong_suat': du_lieu['cong_suat'],
                    'xuat_xu': du_lieu['xuat_xu'],
                    'so_luong_ton': du_lieu['so_luong_ton'],
                    'mo_ta_ngan': du_lieu['mo_ta_ngan'],
                    'mo_ta_chi_tiet': du_lieu['mo_ta_chi_tiet'],
                    'duong_dan_anh_mau': duong_dan_anh,
                    'xe_noi_bat': du_lieu['xe_noi_bat'],
                    'dang_kinh_doanh': True,
                },
            )
            if not da_tao and xe.duong_dan_anh_mau != duong_dan_anh:
                xe.duong_dan_anh_mau = duong_dan_anh
                xe.save(update_fields=['duong_dan_anh_mau'])
            if da_tao:
                dem_xe += 1

        self.stdout.write(self.style.SUCCESS(f'Đã khởi tạo dữ liệu mẫu thành công ({dem_xe} xe mới).'))
