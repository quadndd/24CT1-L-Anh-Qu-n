from django import template

from cua_hang_xe.tien_ich import dinh_dang_tien_vnd

register = template.Library()


@register.filter(name='tien_vnd')
def bo_loc_tien_vnd(gia_tri):
    """Bộ lọc template hiển thị số tiền theo định dạng VNĐ."""
    return dinh_dang_tien_vnd(gia_tri)
