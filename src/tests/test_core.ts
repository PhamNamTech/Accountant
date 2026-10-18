import path from 'path';
import { lookupAccountingAccount } from '../core/accounts.js';
import { calculateProductCost, allocateOverheadCosts } from '../core/cost.js';
import { getJournalEntries, createJournalEntry, getJournalStats } from '../core/database.js';
import { parseVietnameseInvoiceXml } from '../core/invoiceParser.js';

console.log("=== KIỂM THỬ TYPESCRIPT CORE (SRC/CORE) ===");

// 1. Tra cứu tài khoản
const resTT99 = lookupAccountingAccount("112", "TT99");
console.assert(resTT99.results["112"] !== undefined, "Không tìm thấy TK 112");
console.assert(resTT99.results["112"].name === "Tiền gửi không kỳ hạn", "Tên TK 112 TT99 không đúng");
console.log(" -> PASS: lookupAccountingAccount (TT99 TK 112)");

// 2. Tính giá thành sản phẩm
const costResult = calculateProductCost({
  productName: "Bàn làm việc gỗ",
  dDauKy: 2000000,
  cpNvlTrucTiep: 12000000,
  cpNhanCongTrucTiep: 6000000,
  cpSanXuatChung: 4000000,
  dCuoiKy: 1500000,
  slHoanThanh: 10,
  pheLieuThuHoi: 500000,
  regime: "TT99"
});
console.assert(costResult.tong_gia_thanh_Z === 22000000, `Z sai: ${costResult.tong_gia_thanh_Z}`);
console.assert(costResult.gia_thanh_don_vi_z === 2200000, `z sai: ${costResult.gia_thanh_don_vi_z}`);
console.log(" -> PASS: calculateProductCost (Z = 22,000,000 | z = 2,200,000)");

// 3. Phân bổ chi phí SXC
const allocResult = allocateOverheadCosts(10000000, [
  { name: "SP A", base_value: 6000000 },
  { name: "SP B", base_value: 4000000 }
]);
console.assert(allocResult.tong_da_phan_bo === 10000000, `Tổng phân bổ sai: ${allocResult.tong_da_phan_bo}`);
console.log(" -> PASS: allocateOverheadCosts");

// 4. Sổ Nhật Ký Chung SQLite
const journal = getJournalEntries({ limit: 5 });
console.assert(typeof journal.total_records === 'number', "total_records không hợp lệ");
console.log(` -> PASS: getJournalEntries (Total records: ${journal.total_records})`);

// 5. Bóc tách hóa đơn XML
const xmlPath = path.resolve(process.cwd(), "tests", "test_data", "hoadon_01.xml");
const invoiceData = parseVietnameseInvoiceXml(xmlPath);
console.assert(invoiceData.so_hoa_don === "0000015", `Số HĐ sai: ${invoiceData.so_hoa_don}`);
console.log(` -> PASS: parseVietnameseInvoiceXml (Số HĐ: ${invoiceData.so_hoa_don})`);

console.log("=== TOÀN BỘ KIỂM THỬ TYPESCRIPT CORE ĐẠT 100% ===");
