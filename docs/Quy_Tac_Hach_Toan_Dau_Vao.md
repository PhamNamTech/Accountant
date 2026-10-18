# BỘ QUY TẮC ĐẶT MÃ & HẠCH TOÁN ĐẦU VÀO DOANH NGHIỆP

Tài liệu này chuẩn hóa toàn bộ quy tắc quản trị danh mục (Mã Nhà cung cấp, Mã Vật tư - Hàng hóa - CCDC) và quy tắc hạch toán chi phí đầu vào, mua dịch vụ, chi phí vận chuyển theo Chuẩn mực Kế toán Việt Nam (VAS 02) và Chế độ kế toán Doanh nghiệp (Thông tư 133/2016/TT-BTC, Thông tư 200/2014/TT-BTC & Thông tư 99/2025/TT-BTC).

---

## PHẦN 1: QUY TẮC SINH MÃ NHÀ CUNG CẤP (VENDOR CODE)
Mã nhà cung cấp gồm **3 ký tự chữ cái in hoa**, sinh tự động từ tên riêng thương mại của nhà cung cấp (đã loại bỏ tiền tố pháp nhân như *Công ty, TNHH, CP, MTV, DNTN, TM, DV...*).

### 1. Tên riêng có 3 từ:
- **Nguyên tắc:** Lấy ký tự chữ cái đầu tiên của cả 3 từ.
- **Ví dụ:**
  * Hoàng Gia Phát $\rightarrow$ **HGP**
  * Tân Tiến Đạt $\rightarrow$ **TTD**
  * Bình Minh Xanh $\rightarrow$ **BMX**

### 2. Tên riêng có 2 từ:
- **Nguyên tắc:** Lấy chữ cái đầu của từ thứ 1 + chữ cái đầu của từ thứ 2 + chữ cái thứ 2 của từ thứ 2.
- **Ví dụ:**
  * Hưng Phát: `H` (từ 1) + `Ph` (từ 2: chữ thứ nhất `P`, chữ thứ hai `H`) $\rightarrow$ **HPH**
  * Bảo Long: `B` (từ 1) + `Lo` (từ 2: chữ thứ nhất `L`, chữ thứ hai `O`) $\rightarrow$ **BLO**
  * Đại An: `Đ` (từ 1) + `An` (từ 2: chữ thứ nhất `A`, chữ thứ hai `N`) $\rightarrow$ **DAN**

### 3. Quy tắc xử lý khi trùng mã (Collision Handling):
- Nhà cung cấp phát sinh trước: **Giữ nguyên mã ban đầu**.
- Nhà cung cấp phát sinh sau: **Lấy ký tự chữ cái kế tiếp** của từ thứ 2 (hoặc từ phân biệt) để tránh trùng lặp.
- **Ví dụ:**
  * Nhà cung cấp 1 (phát sinh trước): **Hưng Phát** $\rightarrow$ `H + PH` = **HPH**
  * Nhà cung cấp 2 (phát sinh sau): **Hùng Phát** $\rightarrow$ Trùng `HPH`, chuyển sang ký tự thứ 3 của từ "Phát" (chữ `A`) $\rightarrow$ `H + P + A` = **HPA**
  * Nếu phát sinh tiếp nhà cung cấp thứ 3 (ví dụ **Hoàng Phát**): Chuyển sang ký tự thứ 4 của từ "Phát" (chữ `T`) $\rightarrow$ **HPT**, hoặc lấy chữ cái thứ 2 của từ thứ nhất (`O`) $\rightarrow$ **OPH**.

### 4. Quy tắc kế thừa mã lịch sử (Legacy Code - Mã cũ theo Mã số thuế):
- **Bối cảnh:** Trường hợp Nhà cung cấp **đã phát sinh từ trước** trên hệ thống dữ liệu kế toán và đã được người tiền nhiệm đặt mã bằng **Mã số thuế (MST)** (ví dụ: `0311904294`, `0101234567`...).
- **Quy tắc thực hiện:**
  * **Tiếp tục sử dụng mã cũ (Mã số thuế)** để nhập liệu chứng từ mới.
  * **Tuyệt đối KHÔNG đổi mã** và **KHÔNG tạo thêm mã mới** theo quy tắc 3 ký tự.
- **Mục đích kế toán:**
  * Tránh rủi ro nhân đôi đối tượng công nợ (1 nhà cung cấp tồn tại 2 mã khác nhau trên TK 331).
  * Bảo đảm tính liền mạch, nhất quán của sổ chi tiết công nợ, đối chiếu biên bản xác nhận công nợ và báo cáo tài chính qua các niên độ.
- **Quy tắc đặt mã vật tư/CCDC/hàng hóa mới từ NCC này:**
  * Nếu phát sinh mặt hàng mới: Kế thừa mã hàng cũ đã có hoặc đặt theo `[Loại][Bộ phận]1` + `[Mã NCC cũ / MST]` + `[STT]`.

---

## PHẦN 2: QUY TẮC ĐẶT MÃ VẬT TƯ / CÔNG CỤ DỤNG CỤ / HÀNG HÓA (ITEM CODE)

### 1. Cấu trúc mã tổng quát (Đặt theo THƯƠNG HIỆU - BRAND):
$$\text{Mã hàng} = \mathbf{[Phân\ loại][Bộ\ phận]\mathbf{1}} + \mathbf{[Thương\ hiệu\ (3\ ký\ tự)]} + \mathbf{[Số\ thứ\ tự\ (4\ số)]}$$

> [!IMPORTANT]
> **Quy tắc cốt lõi về Thương hiệu (Brand):** Khi đặt mã NVL, CCDC, Hàng hóa, **KHÔNG dựa vào mã nhà cung cấp** mà bắt buộc phải dựa vào **THƯƠNG HIỆU / NHÃN HIỆU (HIỆU GÌ)** của sản phẩm đó:
> - `LOG`: Hiệu Logitech (Chuột, bàn phím) $\rightarrow$ Ví dụ: Chuột M331 là **`AV1LOG0084`**.
> - `BOS`: Hiệu Bosch (Máy mài, chổi than) $\rightarrow$ Ví dụ: Máy mài GWS700 là **`AX1BOS0249`**, Chổi than là **`CX1BOS0659`**.
> - `NOA`: Không thương hiệu / Thông dụng (Nhựa POM, kẹp, lưỡi cưa, chốt, vải nhám, keo 502, tủ thuốc...) $\rightarrow$ Ví dụ: **`CX1NOA0149`**, **`AX1NOA0238`**, **`CX1NOA0128`**.
> - `GUM`: Hiệu Gumac (Quần áo thời trang) $\rightarrow$ Ví dụ: **`BV1GUM0014`** đến **`BV1GUM0021`**.
> - `LCO`: Hiệu Luxury Comfort (Giày dép) $\rightarrow$ Ví dụ: **`BV1LCO0004`**.
> - `PBC`, `RBI`, `LAS`: Hiệu vòng bi $\rightarrow$ Ví dụ: **`CX1PBC0494`**, **`CX1RBI0563`**, **`CX1RBI0564`**.

- **Ký tự 1 (Phân loại kho / tính chất hàng tồn kho):**
  * `C`: **Nguyên vật liệu** (Hạch toán TK 152)
  * `A`: **Công cụ dụng cụ** (Hạch toán TK 153)
  * `B`: **Hàng hóa thương mại** (Hạch toán TK 156)
- **Ký tự 2 (Nơi sử dụng / Mục đích phục vụ):**
  * `X`: Dùng cho **Nhà xưởng** (Sản xuất trực tiếp / Quản lý phân xưởng)
  * `V`: Dùng cho **Văn phòng** (Quản lý doanh nghiệp / Bán hàng)
- **Ký tự 3:** Số `1` (Định danh chuẩn phiên bản phân nhóm).
- **Phần tiếp theo (3 ký tự):** Mã 3 ký tự viết tắt của **Thương hiệu** (`LOG`, `BOS`, `NOA`, `GUM`, `LCO`...).
- **Phần cuối cùng (4 số):** Số thứ tự phát sinh của sản phẩm (`0001, 0002... 0084`).

---

## PHẦN 3: QUY TẮC HẠCH TOÁN DỊCH VỤ MUA VÀO & CHI PHÍ ĐẦU VÀO

### 1. Hình thức chứng từ:
- Tất cả các dịch vụ mua vào (điện, nước, viễn thông, email, tiếp khách, phí ship, xăng xe, phí hải quan...) bắt buộc lập dưới hình thức **"Chứng từ mua dịch vụ"** trên MISA, **không chọn "Mua hàng không qua kho"**.

### 2. Quy tắc mã hàng cho các dịch vụ (Mã `PDV`):
- Toàn bộ các khoản phí sau đều sử dụng thống nhất mã hàng là **`PDV`** (Phí dịch vụ):
  * Phí dịch vụ ship hàng (Lalamove, Tasetco...)
  * Xăng xe (Phúc An...)
  * Tiền nước (Nước bình La Vie, Nước Chợ Lớn...)
  * Cước chuyển phát nhanh, cước viễn thông, phí duy trì email
  * Tiền điện (Điện lực Bình Phú...)
  * Chi phí ăn uống tiếp khách / buffet
  * Các loại phí liên quan tới hải quan, cước vận tải biển, phí bốc xếp CFS, phí chứng từ D/O (M&P...)

### 3. Quy tắc hạch toán Hóa đơn Điện lực:
- Căn cứ tỷ lệ sử dụng thực tế giữa quản lý văn phòng và phân xưởng sản xuất:
  * **70%** đưa vào **TK 6422** (Chi phí quản lý doanh nghiệp).
  * **30%** đưa vào **TK 154** (Chi phí sản xuất dở dang / SXC phân xưởng).
  * Mã hàng: `PDV`. Thuế GTGT 8% phân bổ tương ứng 70% - 30% vào TK 1331.

### 4. Quy tắc hạch toán Hóa đơn Tiếp khách / Ăn uống / Buffet:
- **Tài khoản chi phí:** Hạch toán toàn bộ vào **TK 6421** (Chi phí bán hàng).
- **Tên hàng / Diễn giải:** Chỉ cần ghi thống nhất là **"Chi phí tiếp khách"**. Mã hàng là **`PDV`**.
- **Quy tắc gom dòng:**
  * **Cùng 1 loại thuế suất:** Chỉ cần hạch toán **1 dòng duy nhất** là "Chi phí tiếp khách" và cộng tổng tiền lại.
  * **Có 2 loại thuế suất khác nhau:** Hạch toán **2 dòng "Chi phí tiếp khách"** tương ứng với từng loại thuế suất (ví dụ: dòng 1 thuế 8%, dòng 2 thuế 10%).

### 5. Dịch vụ mua vào phục vụ Nhập khẩu & Chi phí Ship:
- Dịch vụ phục vụ hoạt động **Nhập khẩu** (Cước tàu quốc tế, CFS, D/O theo B/L): Đưa vào **TK 152 / 153 / 156** (vốn hóa vào nguyên giá hàng mua).
- Chi phí **Ship hàng hóa mua vào** (Lalamove, Tasetco): Đưa vào **TK 152 / 153 / 156** tương ứng hàng hóa đó là gì.
- Chi phí phục vụ hoạt động **Xuất khẩu**: Đưa vào **TK 6421** (Chi phí bán hàng).
