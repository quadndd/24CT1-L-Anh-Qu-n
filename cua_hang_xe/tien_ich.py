import re
import unicodedata


def dinh_dang_tien_vnd(so_tien):
    """Định dạng số tiền sang chuẩn VNĐ (ví dụ: 1.250.000.000 đ)."""
    if so_tien is None:
        return '0 đ'
    gia_tri = int(so_tien)
    return f'{gia_tri:,}'.replace(',', '.') + ' đ'


def chuyen_khong_dau_slug(chuoi):
    """Chuyển chuỗi tiếng Việt có dấu thành slug không dấu."""
    chuoi = unicodedata.normalize('NFKD', chuoi)
    chuoi = chuoi.encode('ascii', 'ignore').decode('utf-8')
    chuoi = chuoi.lower().strip()
    chuoi = re.sub(r'[^a-z0-9]+', '-', chuoi)
    return chuoi.strip('-')
