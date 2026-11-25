function doiAnhChinh(duongDanAnh) {
  const anhChinh = document.getElementById('anh-xe-chinh');
  if (anhChinh && duongDanAnh) {
    anhChinh.src = duongDanAnh;
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const chonNhanXe = document.getElementById('id_phuong_thuc_nhan_xe');
  const hienThiPhi = document.getElementById('phi-van-chuyen-hien-thi');
  const hienThiTong = document.getElementById('tong-thanh-toan-hien-thi');

  if (chonNhanXe && hienThiPhi && hienThiTong) {
    const tongTienXe = parseInt(hienThiTong.dataset.tongTienXe || '0', 10);
    const dinhDangTien = (so) => so.toLocaleString('vi-VN') + ' đ';

    const capNhatTong = () => {
      const phi = chonNhanXe.value === 'giao_tan_noi' ? 5000000 : 0;
      hienThiPhi.textContent = phi === 0 ? 'Miễn phí' : dinhDangTien(phi);
      hienThiTong.textContent = dinhDangTien(tongTienXe + phi);
    };

    chonNhanXe.addEventListener('change', capNhatTong);
    capNhatTong();
  }
});
