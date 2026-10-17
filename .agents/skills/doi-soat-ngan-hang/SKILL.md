---
name: doi-soat-ngan-hang
description: Quy trình đối soát sao kê tài khoản ngân hàng (Bank Reconciliation) với Sổ tiền gửi ngân hàng (TK 112) để tìm chênh lệch và sai lệch dòng tiền.
---

# Quy trình Đối soát Sao kê Ngân hàng (Bank Reconciliation)

## Khi nào sử dụng:
Khi người dùng tải lên file sao kê ngân hàng (Vietcombank, Techcombank, MB, BIDV, VPBank...) dạng Excel/CSV và muốn:
- Khớp dòng tiền vào/ra với sổ sách kế toán.
- Phát hiện các khoản thu chưa hạch toán (khách hàng thanh toán nhưng chưa xuất hóa đơn/chưa vào sổ).
- Phát hiện các khoản phí ngân hàng, lãi tiền gửi chưa hạch toán.
- Kiểm tra số dư đầu kỳ, cuối kỳ giữa ngân hàng và sổ cái TK 112.

## Các bước thực hiện:
1. Đọc file sao kê ngân hàng qua `pandas` hoặc `excel-mcp`.
2. Chuẩn hóa các cột: Ngày giao dịch, Số tiền ghi Nợ (Tiền chi ra), Số tiền ghi Có (Tiền thu vào), Nội dung giao dịch, Số dư sau giao dịch.
3. So khớp với dữ liệu phát sinh sổ cái TK 112 (trong SQLite hoặc file Excel).
4. Phân loại các giao dịch:
   - Đã khớp (Matched)
   - Chỉ có trên sao kê ngân hàng (Bank-only: thường là phí duy trì, lãi tiền gửi, tiền khách chuyển chưa rõ nội dung).
   - Chỉ có trên sổ sách kế toán (Ledger-only: séc chưa rút, lệnh chuyển tiền đang xử lý).
5. Xuất Biên bản đối soát sao kê ra file Excel kèm các bút toán điều chỉnh đề xuất.
