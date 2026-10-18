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
   - **Quy tắc đặt mã danh mục đầu vào (Tham khảo chi tiết tại `docs/Quy_Tac_Hach_Toan_Dau_Vao.md`)**:
     * **Kế thừa mã NCC cũ (Mã số thuế)**: Nếu NCC đã tồn tại trên phần mềm do kế toán cũ đặt bằng MST, tiếp tục sử dụng mã MST cũ, **tuyệt đối không đổi hay tạo mã mới**.
     * **Mã Hàng hóa / CCDC / NVL đặt theo THƯƠNG HIỆU (HIỆU GÌ)**: Bắt buộc dựa vào nhãn hiệu sản phẩm (không dựa vào mã NCC). Cấu trúc: `[Loại][Bộ phận]1` + `[Thương hiệu (3 ký tự)]` + `[STT (4 số)]` (VD: Logitech là `LOG` -> `AV1LOG0084`, Bosch là `BOS` -> `AX1BOS0249`, không hiệu là `NOA` -> `CX1NOA0149`).
     * **Mã Dịch vụ (PDV)**: Toàn bộ phí dịch vụ ship hàng, xăng xe, tiền nước, cước chuyển phát nhanh, tiền điện, buffet, phí hải quan đều dùng mã **`PDV`**.
   - **Định khoản hóa đơn đầu vào (Mua hàng / Dịch vụ)**:
     * **Hình thức chứng từ**: Các chứng từ dịch vụ mua vào lập loại **"Chứng từ mua dịch vụ"** (không chọn mua hàng không qua kho).
     * **Chi phí tiếp khách / buffet**: Đưa vào **TK 6421** (Chi phí bán hàng), tên hàng ghi **"Chi phí tiếp khách"**. Hóa đơn cùng loại thuế suất gom 1 dòng; 2 loại thuế suất gom 2 dòng.
     * **Hóa đơn tiền điện**: Phân bổ **70% vào TK 6422** (văn phòng), **30% vào TK 154** (phân xưởng).
     * Dịch vụ phục vụ hoạt động **Nhập khẩu** & Chi phí **Ship hàng mua vào**: Vốn hóa vào nguyên giá hàng mua -> Nợ TK 152, 153, 156 tương ứng.
     * Dịch vụ phục vụ hoạt động **Xuất khẩu**: Ghi nhận chi phí bán hàng -> Nợ TK 6421 (TT 133).
     * Thuế GTGT đầu vào: Nợ TK 1331.
     * Công nợ / Tiền thanh toán: Có TK 331.
   - Đối với hóa đơn đầu ra (Bán hàng/Cung cấp dịch vụ):
     * Ghi nhận Nợ TK phải thu/tiền (131, 111, 112).
     * Ghi nhận Có TK doanh thu (511).
     * Ghi nhận Có TK thuế GTGT đầu ra phải nộp (33311).
4. **Báo cáo kết quả**:
   - Cung cấp đường dẫn file Excel bảng kê vừa tạo cho người dùng kiểm tra.
   - Tóm tắt tổng số hóa đơn hợp lệ, tổng doanh số chưa thuế và tổng tiền thuế GTGT.
