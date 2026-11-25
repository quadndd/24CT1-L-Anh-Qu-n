from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import HoSoNguoiDung


class BieuMauDangKy(UserCreationForm):
    """Biểu mẫu đăng ký tài khoản khách hàng mới."""

    email = forms.EmailField(
        label='Địa chỉ Email',
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'example@email.com'}
        ),
    )
    ho_va_ten = forms.CharField(
        label='Họ và tên',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Nguyễn Văn A'}
        ),
    )
    so_dien_thoai = forms.CharField(
        label='Số điện thoại',
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '09xx xxx xxx'}
        ),
    )
    dia_chi = forms.CharField(
        label='Địa chỉ liên hệ',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố',
            }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'ho_va_ten', 'so_dien_thoai', 'dia_chi')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nhập tên đăng nhập'}
        )
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Tối thiểu 8 ký tự'}
        )
        self.fields['password2'].label = 'Nhập lại mật khẩu'
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nhập lại mật khẩu'}
        )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng cho tài khoản khác.')
        return email


class BieuMauDangNhap(AuthenticationForm):
    """Biểu mẫu đăng nhập hệ thống."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nhập tên đăng nhập'}
        )
        self.fields['password'].label = 'Mật khẩu'
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nhập mật khẩu'}
        )


class BieuMauCapNhatTaiKhoan(forms.ModelForm):
    """Biểu mẫu cập nhật email tài khoản."""

    class Meta:
        model = User
        fields = ('email',)
        labels = {'email': 'Địa chỉ Email'}
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class BieuMauCapNhatHoSo(forms.ModelForm):
    """Biểu mẫu cập nhật thông tin cá nhân người dùng."""

    class Meta:
        model = HoSoNguoiDung
        fields = ('ho_va_ten', 'so_dien_thoai', 'dia_chi', 'thanh_pho', 'ngay_sinh', 'anh_dai_dien')
        widgets = {
            'ho_va_ten': forms.TextInput(attrs={'class': 'form-control'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_chi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'thanh_pho': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'anh_dai_dien': forms.FileInput(attrs={'class': 'form-control'}),
        }


class BieuMauDoiMatKhau(PasswordChangeForm):
    """Biểu mẫu đổi mật khẩu tiếng Việt."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Mật khẩu hiện tại'
        self.fields['new_password1'].label = 'Mật khẩu mới'
        self.fields['new_password2'].label = 'Xác nhận mật khẩu mới'
        for truong in self.fields.values():
            truong.widget.attrs.update({'class': 'form-control'})
