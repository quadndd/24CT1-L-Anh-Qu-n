from django import forms

from .models import DanhGiaXe, HangXe, LichLaiThu, LoaiXe, Xe


class BieuMauThemLoaiXe(forms.ModelForm):
    """Biểu mẫu thêm loại xe mới (SUV, Sedan, Coupe...)."""

    class Meta:
        model = LoaiXe
        fields = ('ten_loai', 'mo_ta')
        widgets = {
            'ten_loai': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ví dụ: Hatchback, Coupe...'}),
            'mo_ta': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Mô tả ngắn gọn'}),
        }


class BieuMauThemHangXe(forms.ModelForm):
    """Biểu mẫu thêm hãng xe mới."""

    class Meta:
        model = HangXe
        fields = ('ten_hang', 'quoc_gia', 'mo_ta')
        widgets = {
            'ten_hang': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ví dụ: Kia, Honda, BMW...'}),
            'quoc_gia': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ví dụ: Hàn Quốc, Đức...'}),
            'mo_ta': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Mô tả ngắn gọn'}),
        }


class BieuMauThemSuaXe(forms.ModelForm):
    """Biểu mẫu thêm mới hoặc chỉnh sửa thông tin xe ô tô."""

    class Meta:
        model = Xe
        fields = (
            'ten_xe',
            'hang_xe',
            'loai_xe',
            'gia_ban',
            'gia_khuyen_mai',
            'nam_san_xuat',
            'mau_sac',
            'dong_co',
            'hop_so',
            'nhien_lieu',
            'so_cho_ngoi',
            'cong_suat',
            'xuat_xu',
            'tinh_trang',
            'so_luong_ton',
            'mo_ta_ngan',
            'mo_ta_chi_tiet',
            'hinh_anh_chinh',
            'xe_noi_bat',
            'dang_kinh_doanh',
        )
        widgets = {
            'ten_xe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: VinFast VF 7 Plus'}),
            'hang_xe': forms.Select(attrs={'class': 'form-select'}),
            'loai_xe': forms.Select(attrs={'class': 'form-select'}),
            'gia_ban': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1000000}),
            'gia_khuyen_mai': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1000000}),
            'nam_san_xuat': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2030}),
            'mau_sac': forms.TextInput(attrs={'class': 'form-control'}),
            'dong_co': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 2.0L Turbo'}),
            'hop_so': forms.Select(attrs={'class': 'form-select'}),
            'nhien_lieu': forms.Select(attrs={'class': 'form-select'}),
            'so_cho_ngoi': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 16}),
            'cong_suat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 200 mã lực'}),
            'xuat_xu': forms.TextInput(attrs={'class': 'form-control'}),
            'tinh_trang': forms.Select(attrs={'class': 'form-select'}),
            'so_luong_ton': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'mo_ta_ngan': forms.TextInput(attrs={'class': 'form-control'}),
            'mo_ta_chi_tiet': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hinh_anh_chinh': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'xe_noi_bat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dang_kinh_doanh': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        du_lieu = super().clean()
        gia_ban = du_lieu.get('gia_ban')
        gia_km = du_lieu.get('gia_khuyen_mai')
        if gia_ban is not None and gia_km is not None and gia_km >= gia_ban:
            self.add_error('gia_khuyen_mai', 'Giá khuyến mãi phải nhỏ hơn giá niêm yết.')
        return du_lieu


class BieuMauDanhGia(forms.ModelForm):
    """Biểu mẫu gửi đánh giá và nhận xét xe."""

    class Meta:
        model = DanhGiaXe
        fields = ('so_sao', 'noi_dung')
        widgets = {
            'so_sao': forms.Select(attrs={'class': 'form-select'}),
            'noi_dung': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Chia sẻ cảm nhận của bạn về mẫu xe này...',
                }
            ),
        }


class BieuMauDatLichLaiThu(forms.ModelForm):
    """Biểu mẫu đặt lịch hẹn lái thử xe tại showroom."""

    class Meta:
        model = LichLaiThu
        fields = ('xe', 'ho_ten', 'so_dien_thoai', 'email', 'ngay_hen', 'gio_hen', 'ghi_chu')
        widgets = {
            'xe': forms.Select(attrs={'class': 'form-select'}),
            'ho_ten': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}
            ),
            'so_dien_thoai': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '09xx xxx xxx'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'example@email.com'}
            ),
            'ngay_hen': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gio_hen': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'ghi_chu': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Yêu cầu thêm (ví dụ: lái thử phiên bản màu đen...)',
                }
            ),
        }
