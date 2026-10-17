---
name: ke-toan-gia-thanh
description: Quy trình chi tiết tập hợp chi phí sản xuất, phân bổ chi phí sản xuất chung theo công suất bình thường (VAS 02), đánh giá sản phẩm dở dang cuối kỳ và tính giá thành sản phẩm (Z, z) theo Thông tư 99/2025/TT-BTC, Thông tư 200/2014/TT-BTC và Thông tư 133/2016/TT-BTC.
---

# Quy trình Kế toán Tập hợp Chi phí & Tính Giá thành Sản xuất (Cost Accounting)

## 1. Khi nào kích hoạt Skill này
Kích hoạt khi người dùng yêu cầu:
- Tập hợp và phân loại chi phí sản xuất (Nguyên vật liệu, Nhân công, Sản xuất chung).
- Phân bổ chi phí sản xuất chung (cố định và biến đổi) theo nguyên tắc **Công suất bình thường (VAS 02)**.
- Đánh giá giá trị sản phẩm dở dang cuối kỳ ($D_{\text{cuối kỳ}}$) theo các phương pháp: Chi phí NVL trực tiếp, Sản lượng ước tính tương đương, hoặc Chi phí định mức.
- Tính Tổng giá thành sản xuất ($Z$) và Giá thành đơn vị ($z$) theo các phương pháp: Giản đơn (trực tiếp), Hệ số, Tỷ lệ, Theo đơn đặt hàng (Job Costing), Phân bước (Process Costing).
- Hạch toán nhập kho sản phẩm hoàn thành, xuất bán hoặc kết chuyển chi phí vượt định mức / dưới công suất vào Giá vốn hàng bán.
- Lập và xuất Thẻ tính giá thành sản phẩm ra file Excel.

---

## 2. Bảng Đối chiếu Tài khoản Kế toán Chi phí & Giá thành

| Khoản mục chi phí / Nghiệp vụ | Theo Thông tư 99/2025/TT-BTC (từ năm tài chính 2026) | Theo Thông tư 200/2014/TT-BTC (kỳ cũ trước 2026) | Theo Thông tư 133/2016/TT-BTC (Doanh nghiệp nhỏ và vừa) |
| :--- | :--- | :--- | :--- |
| **Chi phí nguyên liệu, vật liệu trực tiếp** | **TK 621** | **TK 621** | **TK 1541** (Chi phí NVL trực tiếp) |
| **Chi phí nhân công trực tiếp** | **TK 622** | **TK 622** | **TK 1542** (Chi phí nhân công trực tiếp) |
| **Chi phí máy thi công** (xây lắp) | **TK 623** | **TK 623** | **TK 1543** (Chi phí máy thi công) |
| **Chi phí sản xuất chung** | **TK 627** (tiểu khoản 6271-6278) | **TK 627** (tiểu khoản 6271-6278) | **TK 1547** (Chi phí SX chung) |
| **Tập hợp chi phí SXKD dở dang** | **TK 154** | **TK 154** | **TK 154** |
| **Nhập kho sản phẩm hoàn thành** | **TK 155** (*Sản phẩm*) | **TK 1551** (*Thành phẩm* nhập kho) | **TK 155** (*Thành phẩm*) |
| **Chi phí SXC cố định dưới công suất / Giá vốn hàng bán** | **TK 632** | **TK 632** | **TK 632** |
| **Chi phí Bán hàng** (Chi phí thời kỳ) | **TK 641** | **TK 641** | **TK 6421** (Tiểu khoản TK 642) |
| **Chi phí quản lý doanh nghiệp** (Chi phí thời kỳ) | **TK 642** | **TK 642** | **TK 6422** (Tiểu khoản TK 642) |
| **Phế liệu thu hồi nhập kho** | **TK 152** | **TK 152** | **TK 152** |
| **Tổn thất ngoài định mức / Chờ bồi thường** | **TK 1388** | **TK 1388** | **TK 1388** |
| **Xác định kết quả kinh doanh** | **TK 911** | **TK 911** | **TK 911** |

> [!NOTE]
> **Điểm mới về tài khoản theo Thông tư 99/2025/TT-BTC:**
> - TK 155 đổi tên thành "Sản phẩm"; bãi bỏ các tiểu khoản cấp 2 cứng (1551, 1557), doanh nghiệp tự mở chi tiết theo nhu cầu quản trị.
> - Bãi bỏ hoàn toàn **TK 611** (Mua hàng) và **TK 631** (Giá thành sản xuất); phương pháp KKTX là chủ đạo, tập hợp chi phí sản xuất trực tiếp qua TK 154.

---

## 3. Công thức tính Giá thành Sản xuất

### A. Công thức Tổng giá thành ($Z$) và Giá thành đơn vị ($z$):
- **Dạng Text thuần:**
  ```text
  Tổng giá thành SP hoàn thành (Z) = D_đầu_kỳ + (C_NVL + C_Nhân_công + C_SX_chung_hợp_lý) - D_cuối_kỳ - Phế_liệu_thu_hồi - SP_phụ_thu_hồi
  Giá thành đơn vị (z) = Tổng giá thành (Z) / Sản lượng sản phẩm hoàn thành (Q)
  ```
- **Dạng LaTeX KaTeX:**
  $$Z = D_{\text{đầu kỳ}} + (C_{\text{NVL}} + C_{\text{Nhân công}} + C_{\text{SXC hợp lý}}) - D_{\text{cuối kỳ}} - \text{Phế liệu thu hồi} - \text{Sản phẩm phụ}$$
  $$z = \frac{Z}{Q_{\text{hoàn thành}}}$$

---

## 4. Các Phương pháp Đánh giá Sản phẩm Dở dang Cuối kỳ ($D_{\text{cuối kỳ}}$)

### Phương pháp 1: Đánh giá theo Chi phí Nguyên vật liệu trực tiếp
- **Phạm vi áp dụng:** Thích hợp khi chi phí NVL trực tiếp chiếm tỷ trọng áp đảo (thường > 60-70%), chu kỳ sản xuất ngắn.
- **Nguyên tắc:** Toàn bộ chi phí nhân công và chi phí sản xuất chung phát sinh trong kỳ được tính hết cho sản phẩm hoàn thành; sản phẩm dở dang chỉ chịu chi phí NVL trực tiếp.
- **Công thức tính:**
  ```text
  D_cuối = [(D_đầu_NVL + C_NVL_trong_kỳ) / (Q_hoàn_thành + Q_dở_dang)] * Q_dở_dang
  ```
  $$D_{\text{cuối kỳ}} = \frac{D_{\text{đầu kỳ (NVL)}} + C_{\text{NVL trong kỳ}}}{Q_{\text{hoàn thành}} + Q_{\text{dở dang}}} \times Q_{\text{dở dang}}$$

### Phương pháp 2: Đánh giá theo Sản lượng ước tính tương đương (Equivalent Units)
- **Phạm vi áp dụng:** Thích hợp khi chi phí chế biến (nhân công, SXC) chiếm tỷ trọng lớn và sản phẩm dở dang ở nhiều mức độ hoàn thiện khác nhau.
- **Nguyên tắc:**
  - Chi phí NVL chính bỏ vào ngay từ đầu quy trình: Phân bổ theo khối lượng sản phẩm ($Q_{\text{hoàn thành}} + Q_{\text{dở dang}}$).
  - Chi phí chế biến (Nhân công + SXC) bỏ dần theo tiến độ: Phân bổ theo **Sản lượng hoàn thành tương đương**:
    ```text
    Q_tương_đương = Q_dở_dang * % Hoàn thành
    ```
    $$Q_{\text{tương đương}} = Q_{\text{dở dang}} \times \% \text{hoàn thành}$$
- **Công thức tính $D_{\text{cuối kỳ}}$:**
  ```text
  D_cuối = D_cuối_NVL + D_cuối_Nhân_công + D_cuối_SXC
  ```
  $$D_{\text{cuối (chế biến)}} = \frac{D_{\text{đầu (CB)}} + C_{\text{CB trong kỳ}}}{Q_{\text{hoàn thành}} + (Q_{\text{dở dang}} \times \% \text{hoàn thành})} \times (Q_{\text{dở dang}} \times \% \text{hoàn thành})$$

### Phương pháp 3: Đánh giá theo Chi phí định mức / Đơn giá kế hoạch
- Căn cứ vào định mức kinh tế kỹ thuật tiêu hao ở từng công đoạn công nghệ để nhân với khối lượng dở dang thực tế kiểm kê cuối kỳ.

---

## 5. Nguyên tắc Công suất bình thường (Normal Capacity - Chuẩn mực VAS 02)

> [!IMPORTANT]
> **Phân bổ Chi phí Sản xuất chung (SXC):**
> 1. **Chi phí SXC biến đổi:** Phân bổ toàn bộ vào chi phí chế biến cho mỗi đơn vị sản phẩm theo chi phí thực tế phát sinh.
> 2. **Chi phí SXC cố định (khấu hao máy móc, nhà xưởng, lương quản lý xưởng...):** Bắt buộc phân bổ vào chi phí chế biến trên cơ sở **công suất bình thường**.
> 3. **Khi thực tế sản xuất DƯỚI công suất bình thường:**
>    - Chi phí SXC cố định phân bổ vào giá thành đơn vị sản phẩm vẫn giữ nguyên theo mức công suất bình thường.
>    - Phần chi phí SXC cố định không được phân bổ (tương ứng với tỷ lệ công suất thiếu hụt) **TUYỆT ĐỐI KHÔNG ĐƯỢC TÍNH VÀO GIÁ THÀNH SẢN PHẨM (TK 154/TK 155)**, mà phải ghi nhận thẳng vào **Giá vốn hàng bán trong kỳ (TK 632)**.
>    - Định khoản:
>      - TT 99/TT 200: `Nợ TK 632 / Có TK 627` (hoặc kết chuyển qua `TK 154` rồi sang `TK 632`).
>      - TT 133: `Nợ TK 632 / Có TK 1547`.

---

## 6. Xử lý Chi phí ngoài Định mức, Hao hụt, Phế liệu và Sản phẩm phụ

1. **Chi phí nguyên vật liệu, nhân công vượt định mức:**
   - Không được tính vào giá thành sản phẩm hoàn thành.
   - Hạch toán ghi nhận thẳng vào Giá vốn hàng bán: `Nợ TK 632 / Có TK 621, 622` (hoặc qua TK 154 tùy chế độ).
   - *Lưu ý Thuế TNDN:* Phần chi phí vượt định mức sẽ bị loại trừ khi quyết toán thuế TNDN (Luật Thuế TNDN số 67/2025/QH15).
2. **Hao hụt & Sản phẩm hỏng:**
   - *Trong định mức kỹ thuật:* Tính vào tổng giá thành sản phẩm hoàn thành.
   - *Ngoài định mức:* Xác định nguyên nhân, trừ phần cá nhân bồi thường (`Nợ TK 1388`), phần còn lại hạch toán vào Giá vốn hàng bán (`Nợ TK 632`).
3. **Phế liệu thu hồi:**
   - Nhập kho: `Nợ TK 152 / Có TK 154`, làm giảm trừ trực tiếp vào Tổng giá thành $Z$.
4. **Sản phẩm phụ:**
   - Đánh giá theo giá trị thuần có thể thực hiện được hoặc giá bán ước tính trừ chi phí bán hàng: `Nợ TK 152, 155 / Có TK 154`, giảm trừ vào Tổng giá thành sản phẩm chính.

---

## 7. Quy trình Hạch toán & Kết chuyển Cuối kỳ theo từng Chế độ

### A. Theo Thông tư 99/2025/TT-BTC & Thông tư 200/2014/TT-BTC:
1. Tập hợp chi phí trong kỳ:
   - Chi phí NVL trực tiếp: `Nợ TK 621 / Có TK 152`
   - Chi phí Nhân công trực tiếp: `Nợ TK 622 / Có TK 334, 338`
   - Chi phí Sản xuất chung: `Nợ TK 627 / Có TK 111, 112, 153, 214, 242, 331...`
2. Kết chuyển chi phí hợp lý để tính giá thành:
   - `Nợ TK 154 / Có TK 621, Có TK 622, Có TK 627`
3. Chi phí vượt định mức / dưới công suất (nếu có):
   - `Nợ TK 632 / Có TK 621, Có TK 622, Có TK 627` (hoặc `Nợ TK 632 / Có TK 154`)
4. Nhập kho sản phẩm hoàn thành ($Z$):
   - TT 99/2025: `Nợ TK 155 (Sản phẩm) / Có TK 154`
   - TT 200/2014: `Nợ TK 1551 (Thành phẩm nhập kho) / Có TK 154`
5. Xuất bán thẳng không qua kho ($Z$):
   - `Nợ TK 632 / Có TK 154`

### B. Theo Thông tư 133/2016/TT-BTC:
1. Tập hợp chi phí trực tiếp vào các tiểu khoản TK 154:
   - Chi phí NVL trực tiếp: `Nợ TK 1541 / Có TK 152`
   - Chi phí Nhân công trực tiếp: `Nợ TK 1542 / Có TK 334, 338`
   - Chi phí Sản xuất chung: `Nợ TK 1547 / Có TK 111, 112, 153, 214, 242, 331...`
2. Chi phí SXC cố định dưới công suất kết chuyển giá vốn:
   - `Nợ TK 632 / Có TK 1547`
3. Nhập kho thành phẩm hoàn thành ($Z$):
   - `Nợ TK 155 / Có TK 154`
4. Xuất bán trực tiếp:
   - `Nợ TK 632 / Có TK 154`
