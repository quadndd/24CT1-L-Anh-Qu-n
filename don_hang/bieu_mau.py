from django import forms

from .models import DonHang


class BieuMauDatHang(forms.ModelForm):
    """Biểu mẫu thông tin đặt mua xe."""

    class Meta:
        model = DonHang
        fields = (
            'ho_ten_nguoi_nhan',
            'so_dien_thoai',
            'email',
            'dia_chi_giao_xe',
            'phuong_thuc_nhan_xe',
            'phuong_thuc_thanh_toan',
            'ghi_chu',
        )
        widgets = {
            'ho_ten_nguoi_nhan': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên người nhận xe'}
            ),
            'so_dien_thoai': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '09xx xxx xxx'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'example@email.com'}
            ),
            'dia_chi_giao_xe': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Nhập địa chỉ nhận xe hoặc địa chỉ làm hồ sơ',
                }
            ),
            'phuong_thuc_nhan_xe': forms.Select(attrs={'class': 'form-select'}),
            'phuong_thuc_thanh_toan': forms.Select(attrs={'class': 'form-select'}),
            'ghi_chu': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Ghi chú thêm về thời gian nhận xe, yêu cầu đăng ký biển số...',
                }
            ),
        }
