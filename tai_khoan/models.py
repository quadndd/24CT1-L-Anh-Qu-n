from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class HoSoNguoiDung(models.Model):
    """Lưu trữ thông tin bổ sung của tài khoản người dùng."""

    nguoi_dung = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ho_so',
        verbose_name='Tài khoản',
    )
    ho_va_ten = models.CharField('Họ và tên', max_length=150, blank=True)
    so_dien_thoai = models.CharField('Số điện thoại', max_length=20, blank=True)
    dia_chi = models.TextField('Địa chỉ', blank=True)
    thanh_pho = models.CharField('Tỉnh / Thành phố', max_length=100, blank=True)
    ngay_sinh = models.DateField('Ngày sinh', null=True, blank=True)
    anh_dai_dien = models.ImageField(
        'Ảnh đại diện',
        upload_to='anh_dai_dien/',
        null=True,
        blank=True,
    )
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', auto_now=True)

    class Meta:
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

    def __str__(self):
        return self.ho_va_ten or self.nguoi_dung.username

    def lay_ten_hien_thi(self):
        """Trả về tên hiển thị ưu tiên của người dùng."""
        if self.ho_va_ten:
            return self.ho_va_ten
        ten_day_du = self.nguoi_dung.get_full_name().strip()
        return ten_day_du or self.nguoi_dung.username


@receiver(post_save, sender=User)
def tao_ho_so_tu_dong(sender, instance, created, **kwargs):
    """Tự động tạo hồ sơ khi có tài khoản mới được tạo."""
    if created:
        HoSoNguoiDung.objects.create(
            nguoi_dung=instance,
            ho_va_ten=instance.get_full_name().strip(),
        )
