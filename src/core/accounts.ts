export interface AccountInfo {
  name: string;
  type: string;
  regime: string;
  status?: string;
  note?: string;
}

export type ChartOfAccounts = Record<string, AccountInfo>;

export const CHART_OF_ACCOUNTS_TT99: ChartOfAccounts = {
  "111": { name: "Tiền mặt", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "1111": { name: "Tiền Việt Nam", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "1112": { name: "Ngoại tệ", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "112": { name: "Tiền gửi không kỳ hạn", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC", note: "Đổi tên từ 'Tiền gửi ngân hàng' theo TT 99, phản ánh tiền gửi không kỳ hạn" },
  "1121": { name: "Tiền Việt Nam gửi không kỳ hạn", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "1122": { name: "Ngoại tệ gửi không kỳ hạn", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "121": { name: "Chứng khoán kinh doanh", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "128": { name: "Đầu tư nắm giữ đến ngày đáo hạn", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "131": { name: "Phải thu của khách hàng", type: "Lưỡng tính (Tài sản/Nợ)", regime: "Thông tư 99/2025/TT-BTC" },
  "133": { name: "Thuế GTGT được khấu trừ", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "1331": { name: "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "1332": { name: "Thuế GTGT được khấu trừ của tài sản cố định", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "1388": { name: "Phải thu khác (bồi thường tổn thất...)", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "141": { name: "Tạm ứng", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "151": { name: "Hàng mua đang đi đường", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "152": { name: "Nguyên liệu, vật liệu", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "153": { name: "Công cụ, dụng cụ", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "154": { name: "Chi phí sản xuất, kinh doanh dở dang", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "155": { name: "Sản phẩm", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC", note: "Đổi tên từ 'Thành phẩm', bãi bỏ tiểu khoản 1551/1557 bắt buộc" },
  "156": { name: "Hàng hóa", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "157": { name: "Hàng gửi đi bán", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "161": { name: "Chi sự nghiệp", type: "Tài khoản bãi bỏ", status: "Bãi bỏ", regime: "Thông tư 99/2025/TT-BTC", note: "Bãi bỏ hoàn toàn theo Thông tư 99/2025/TT-BTC" },
  "211": { name: "Tài sản cố định hữu hình", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "213": { name: "Tài sản cố định vô hình", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "214": { name: "Hao mòn tài sản cố định", type: "Điều chỉnh giảm tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "215": { name: "Tài sản sinh học", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC", note: "Bổ sung mới theo Thông tư 99/2025/TT-BTC" },
  "242": { name: "Chi phí trả trước", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC" },
  "244": { name: "Ký quỹ, ký cược", type: "Tài sản", regime: "Thông tư 99/2025/TT-BTC", note: "Đổi tên từ 'Cầm cố, thế chấp, ký quỹ, ký cược'" },
  "331": { name: "Phải trả cho người bán", type: "Lưỡng tính (Nợ/Tài sản)", regime: "Thông tư 99/2025/TT-BTC" },
  "333": { name: "Thuế và các khoản phải nộp Nhà nước", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "3331": { name: "Thuế giá trị gia tăng phải nộp", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "33311": { name: "Thuế GTGT đầu ra", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "3334": { name: "Thuế thu nhập doanh nghiệp", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "3335": { name: "Thuế thu nhập cá nhân", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "334": { name: "Phải trả người lao động (Lương)", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "338": { name: "Phải trả, phải nộp khác (BHXH, BHYT, KPCĐ)", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "341": { name: "Vay và nợ thuê tài chính", type: "Nợ phải trả", regime: "Thông tư 99/2025/TT-BTC" },
  "411": { name: "Vốn đầu tư của chủ sở hữu", type: "Vốn chủ sở hữu", regime: "Thông tư 99/2025/TT-BTC" },
  "421": { name: "Lợi nhuận sau thuế chưa phân phối", type: "Vốn chủ sở hữu", regime: "Thông tư 99/2025/TT-BTC" },
  "441": { name: "Nguồn vốn đầu tư XDCB", type: "Tài khoản bãi bỏ", status: "Bãi bỏ", regime: "Thông tư 99/2025/TT-BTC", note: "Bãi bỏ hoàn toàn theo Thông tư 99/2025/TT-BTC" },
  "511": { name: "Doanh thu bán hàng và cung cấp dịch vụ", type: "Doanh thu", regime: "Thông tư 99/2025/TT-BTC" },
  "515": { name: "Doanh thu hoạt động tài chính", type: "Doanh thu", regime: "Thông tư 99/2025/TT-BTC" },
  "611": { name: "Mua hàng", type: "Tài khoản bãi bỏ", status: "Bãi bỏ", regime: "Thông tư 99/2025/TT-BTC", note: "Bãi bỏ hoàn toàn theo Thông tư 99/2025/TT-BTC" },
  "621": { name: "Chi phí nguyên liệu, vật liệu trực tiếp", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "622": { name: "Chi phí nhân công trực tiếp", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "623": { name: "Chi phí sử dụng máy thi công", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "627": { name: "Chi phí sản xuất chung", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "631": { name: "Giá thành sản xuất", type: "Tài khoản bãi bỏ", status: "Bãi bỏ", regime: "Thông tư 99/2025/TT-BTC", note: "Bãi bỏ hoàn toàn theo Thông tư 99/2025/TT-BTC" },
  "632": { name: "Giá vốn hàng bán", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "635": { name: "Chi phí tài chính", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "641": { name: "Chi phí bán hàng", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "642": { name: "Chi phí quản lý doanh nghiệp", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "711": { name: "Thu nhập khác", type: "Thu nhập", regime: "Thông tư 99/2025/TT-BTC" },
  "811": { name: "Chi phí khác", type: "Chi phí", regime: "Thông tư 99/2025/TT-BTC" },
  "911": { name: "Xác định kết quả kinh doanh", type: "Trung gian kết chuyển", regime: "Thông tư 99/2025/TT-BTC" }
};

export const CHART_OF_ACCOUNTS_TT200: ChartOfAccounts = {
  "111": { name: "Tiền mặt", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1111": { name: "Tiền Việt Nam", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1112": { name: "Ngoại tệ", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "112": { name: "Tiền gửi ngân hàng", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1121": { name: "Tiền Việt Nam gửi ngân hàng", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1122": { name: "Ngoại tệ gửi ngân hàng", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "121": { name: "Chứng khoán kinh doanh", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "128": { name: "Đầu tư nắm giữ đến ngày đáo hạn", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "131": { name: "Phải thu của khách hàng", type: "Lưỡng tính (Tài sản/Nợ)", regime: "Thông tư 200/2014/TT-BTC" },
  "133": { name: "Thuế GTGT được khấu trừ", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1331": { name: "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1332": { name: "Thuế GTGT được khấu trừ của tài sản cố định", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1388": { name: "Phải thu khác (bồi thường tổn thất...)", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "141": { name: "Tạm ứng", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "151": { name: "Hàng mua đang đi đường", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "152": { name: "Nguyên liệu, vật liệu", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "153": { name: "Công cụ, dụng cụ", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "154": { name: "Chi phí sản xuất, kinh doanh dở dang", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "155": { name: "Thành phẩm", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1551": { name: "Thành phẩm nhập kho", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "1557": { name: "Thành phẩm bất động sản", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "156": { name: "Hàng hóa", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "157": { name: "Hàng gửi đi bán", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "161": { name: "Chi sự nghiệp", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "211": { name: "Tài sản cố định hữu hình", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "213": { name: "Tài sản cố định vô hình", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "214": { name: "Hao mòn tài sản cố định", type: "Điều chỉnh giảm tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "242": { name: "Chi phí trả trước", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "244": { name: "Cầm cố, thế chấp, ký quỹ, ký cược", type: "Tài sản", regime: "Thông tư 200/2014/TT-BTC" },
  "331": { name: "Phải trả cho người bán", type: "Lưỡng tính (Nợ/Tài sản)", regime: "Thông tư 200/2014/TT-BTC" },
  "333": { name: "Thuế và các khoản phải nộp Nhà nước", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "3331": { name: "Thuế giá trị gia tăng phải nộp", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "33311": { name: "Thuế GTGT đầu ra", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "3334": { name: "Thuế thu nhập doanh nghiệp", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "3335": { name: "Thuế thu nhập cá nhân", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "334": { name: "Phải trả người lao động", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "338": { name: "Phải trả, phải nộp khác", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "341": { name: "Vay và nợ thuê tài chính", type: "Nợ phải trả", regime: "Thông tư 200/2014/TT-BTC" },
  "411": { name: "Vốn đầu tư của chủ sở hữu", type: "Vốn chủ sở hữu", regime: "Thông tư 200/2014/TT-BTC" },
  "421": { name: "Lợi nhuận sau thuế chưa phân phối", type: "Vốn chủ sở hữu", regime: "Thông tư 200/2014/TT-BTC" },
  "441": { name: "Nguồn vốn đầu tư XDCB", type: "Vốn chủ sở hữu", regime: "Thông tư 200/2014/TT-BTC" },
  "511": { name: "Doanh thu bán hàng và cung cấp dịch vụ", type: "Doanh thu", regime: "Thông tư 200/2014/TT-BTC" },
  "515": { name: "Doanh thu hoạt động tài chính", type: "Doanh thu", regime: "Thông tư 200/2014/TT-BTC" },
  "611": { name: "Mua hàng (KKĐK)", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "621": { name: "Chi phí nguyên liệu, vật liệu trực tiếp", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "622": { name: "Chi phí nhân công trực tiếp", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "623": { name: "Chi phí sử dụng máy thi công", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "627": { name: "Chi phí sản xuất chung", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "631": { name: "Giá thành sản xuất (KKĐK)", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "632": { name: "Giá vốn hàng bán", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "635": { name: "Chi phí tài chính", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "641": { name: "Chi phí bán hàng", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "642": { name: "Chi phí quản lý doanh nghiệp", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "711": { name: "Thu nhập khác", type: "Thu nhập", regime: "Thông tư 200/2014/TT-BTC" },
  "811": { name: "Chi phí khác", type: "Chi phí", regime: "Thông tư 200/2014/TT-BTC" },
  "911": { name: "Xác định kết quả kinh doanh", type: "Trung gian kết chuyển", regime: "Thông tư 200/2014/TT-BTC" }
};

export const CHART_OF_ACCOUNTS_TT133: ChartOfAccounts = {
  "111": { name: "Tiền mặt", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "112": { name: "Tiền gửi ngân hàng", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "131": { name: "Phải thu của khách hàng", type: "Lưỡng tính (Tài sản/Nợ)", regime: "Thông tư 133/2016/TT-BTC" },
  "133": { name: "Thuế GTGT được khấu trừ", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "152": { name: "Nguyên liệu, vật liệu", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "153": { name: "Công cụ, dụng cụ", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "154": { name: "Chi phí sản xuất, kinh doanh dở dang", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC", note: "TT 133 không dùng TK 621, 622, 627; tập hợp trực tiếp vào 154" },
  "1541": { name: "Chi phí nguyên liệu, vật liệu trực tiếp", type: "Tiểu khoản 154", regime: "Thông tư 133/2016/TT-BTC" },
  "1542": { name: "Chi phí nhân công trực tiếp", type: "Tiểu khoản 154", regime: "Thông tư 133/2016/TT-BTC" },
  "1543": { name: "Chi phí máy thi công", type: "Tiểu khoản 154", regime: "Thông tư 133/2016/TT-BTC" },
  "1547": { name: "Chi phí sản xuất chung", type: "Tiểu khoản 154", regime: "Thông tư 133/2016/TT-BTC" },
  "155": { name: "Thành phẩm", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "156": { name: "Hàng hóa", type: "Tài sản", regime: "Thông tư 133/2016/TT-BTC" },
  "331": { name: "Phải trả cho người bán", type: "Lưỡng tính (Nợ/Tài sản)", regime: "Thông tư 133/2016/TT-BTC" },
  "333": { name: "Thuế và các khoản phải nộp Nhà nước", type: "Nợ phải trả", regime: "Thông tư 133/2016/TT-BTC" },
  "334": { name: "Phải trả người lao động", type: "Nợ phải trả", regime: "Thông tư 133/2016/TT-BTC" },
  "621": { name: "Chi phí NVL trực tiếp (Không dùng)", type: "Không áp dụng", status: "Không áp dụng", regime: "Thông tư 133/2016/TT-BTC", note: "TT 133 sử dụng TK 1541 thay thế" },
  "622": { name: "Chi phí Nhân công trực tiếp (Không dùng)", type: "Không áp dụng", status: "Không áp dụng", regime: "Thông tư 133/2016/TT-BTC", note: "TT 133 sử dụng TK 1542 thay thế" },
  "627": { name: "Chi phí SXC (Không dùng)", type: "Không áp dụng", status: "Không áp dụng", regime: "Thông tư 133/2016/TT-BTC", note: "TT 133 sử dụng TK 1547 thay thế" },
  "632": { name: "Giá vốn hàng bán", type: "Chi phí", regime: "Thông tư 133/2016/TT-BTC" },
  "642": { name: "Chi phí quản lý kinh doanh", type: "Chi phí", regime: "Thông tư 133/2016/TT-BTC" },
  "6421": { name: "Chi phí bán hàng", type: "Tiểu khoản 642", regime: "Thông tư 133/2016/TT-BTC" },
  "6422": { name: "Chi phí quản lý doanh nghiệp", type: "Tiểu khoản 642", regime: "Thông tư 133/2016/TT-BTC" },
  "911": { name: "Xác định kết quả kinh doanh", type: "Trung gian kết chuyển", regime: "Thông tư 133/2016/TT-BTC" }
};

export function lookupAccountingAccount(query: string, regime = "TT99") {
  const regimeKey = regime.toUpperCase().replace(/\s+|_/g, "");
  let chart: ChartOfAccounts;
  let regimeLabel: string;

  if (regimeKey.includes("133")) {
    chart = CHART_OF_ACCOUNTS_TT133;
    regimeLabel = "Thông tư 133/2016/TT-BTC";
  } else if (regimeKey.includes("200")) {
    chart = CHART_OF_ACCOUNTS_TT200;
    regimeLabel = "Thông tư 200/2014/TT-BTC";
  } else {
    chart = CHART_OF_ACCOUNTS_TT99;
    regimeLabel = "Thông tư 99/2025/TT-BTC";
  }

  const queryLower = query.toLowerCase().trim();
  const results: ChartOfAccounts = {};

  for (const [code, info] of Object.entries(chart)) {
    if (code.toLowerCase().includes(queryLower) || info.name.toLowerCase().includes(queryLower)) {
      results[code] = info;
    }
  }

  return {
    regime: regimeLabel,
    query,
    results,
    count: Object.keys(results).length,
  };
}
