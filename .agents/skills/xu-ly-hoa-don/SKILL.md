---
name: xu-ly-hoa-don
description: Quy trình tự động bóc tách hóa đơn điện tử XML (chuẩn Thông tư 78), xuất bảng kê mua vào/bán ra và kiểm tra tính hợp lệ thuế GTGT.
---

# Quy trình Xử lý Hóa đơn Điện tử & Lập Bảng kê Thuế

## Khi nào sử dụng skill này:
Kích hoạt skill này khi người dùng cung cấp các file hóa đơn điện tử (XML/PDF) hoặc yêu cầu:
- Đọc nội dung hóa đơn điện tử.
- Xuất bảng kê hàng hóa mua vào, bán ra sang file Excel.
- Kiểm tra tính hợp lệ, đối soát tổng tiền, tiền thuế GTGT.
- Lập bút toán định khoản kế toán từ hóa đơn.

## Các bước thực hiện:

1. **Kiểm tra thư mục hóa đơn**:
   - Xác định đường dẫn thư mục chứa các file XML hóa đơn (đầu vào hoặc đầu ra).
2. **Bóc tách tự động**:
   - Sử dụng tool `batch_export_invoices_to_excel` từ MCP `ketoan-vn` hoặc script Python để quét toàn bộ hóa đơn.
   - Trích xuất đầy đủ: Ký hiệu mẫu số, ký hiệu HĐ, số HĐ, ngày hóa đơn, tên & MST người bán, tên & MST người mua, tổng tiền hàng chưa thuế, tiền thuế GTGT, tổng thanh toán.
3. **Kiểm tra & Hạch toán**:
   - Đối với hóa đơn đầu vào (Mua hàng/Dịch vụ):
     * Ghi nhận Nợ TK chi phí/kho (152, 153, 156, 642, 242...).
     * Ghi nhận Nợ TK thuế GTGT được khấu trừ (1331 hoặc 1332).
     * Ghi nhận Có TK công nợ/tiền (331, 111, 112).
   - Đối với hóa đơn đầu ra (Bán hàng/Cung cấp dịch vụ):
     * Ghi nhận Nợ TK phải thu/tiền (131, 111, 112).
     * Ghi nhận Có TK doanh thu (511).
     * Ghi nhận Có TK thuế GTGT đầu ra phải nộp (33311).
4. **Báo cáo kết quả**:
   - Cung cấp đường dẫn file Excel bảng kê vừa tạo cho người dùng kiểm tra.
   - Tóm tắt tổng số hóa đơn hợp lệ, tổng doanh số chưa thuế và tổng tiền thuế GTGT.
