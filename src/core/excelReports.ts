import fs from "fs";
import path from "path";
import ExcelJS from "exceljs";
import { parseVietnameseInvoiceXml, ParsedInvoiceData } from "./invoiceParser.js";

export async function exportCostSheetExcel(
  outputExcelPath: string,
  productName: string,
  kyTinhGiaThanh: string,
  slHoanThanh: number,
  dDauKyDict: Record<string, number>,
  phatSinhDict: Record<string, number>,
  dCuoiKyDict: Record<string, number>
) {
  const dir = path.dirname(path.resolve(outputExcelPath));
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet("The_Tinh_Gia_Thanh");

  ws.getCell("A1").value = "DOANH NGHIỆP SẢN XUẤT";
  ws.getCell("A1").font = { name: "Times New Roman", size: 10, bold: true };
  ws.getCell("A2").value = "Bộ phận: Kế toán Giá thành";
  ws.getCell("A2").font = { name: "Times New Roman", size: 9, italic: true };

  ws.getCell("A4").value = "THẺ TÍNH GIÁ THÀNH SẢN PHẨM";
  ws.getCell("A4").font = { name: "Times New Roman", size: 16, bold: true, color: { argb: "FF002060" } };
  ws.getCell("A4").alignment = { horizontal: "center" };
  ws.mergeCells("A4:G4");

  ws.getCell("A5").value = `Tên sản phẩm: ${productName} | Số lượng hoàn thành: ${slHoanThanh.toLocaleString("vi-VN")} | Kỳ tính: ${kyTinhGiaThanh}`;
  ws.getCell("A5").font = { name: "Times New Roman", size: 11, italic: true };
  ws.getCell("A5").alignment = { horizontal: "center" };
  ws.mergeCells("A5:G5");

  const headers = [
    "STT",
    "Khoản mục chi phí",
    "Dở dang đầu kỳ (D_đk)",
    "Chi phí phát sinh (C)",
    "Dở dang cuối kỳ (D_ck)",
    "Tổng giá thành (Z)",
    "Giá thành đơn vị (z)",
  ];

  const headerRow = ws.getRow(7);
  headers.forEach((h, idx) => {
    const cell = headerRow.getCell(idx + 1);
    cell.value = h;
    cell.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FF1F4E79" },
    };
    cell.font = { name: "Times New Roman", size: 10, bold: true, color: { argb: "FFFFFFFF" } };
    cell.alignment = { horizontal: "center", vertical: "middle", wrapText: true };
  });

  const items = [
    ["1", "Chi phí NVL trực tiếp (TK 621)", dDauKyDict.nvl || 0, phatSinhDict.nvl || 0, dCuoiKyDict.nvl || 0],
    ["2", "Chi phí Nhân công trực tiếp (TK 622)", dDauKyDict.nc || 0, phatSinhDict.nc || 0, dCuoiKyDict.nc || 0],
    ["3", "Chi phí Sản xuất chung (TK 627)", dDauKyDict.sxc || 0, phatSinhDict.sxc || 0, dCuoiKyDict.sxc || 0],
  ];

  items.forEach((item, idx) => {
    const rIdx = 8 + idx;
    const row = ws.getRow(rIdx);
    const zVal = (item[2] as number) + (item[3] as number) - (item[4] as number);
    const zUnit = slHoanThanh > 0 ? zVal / slHoanThanh : 0;

    row.getCell(1).value = item[0];
    row.getCell(2).value = item[1];
    row.getCell(3).value = item[2];
    row.getCell(4).value = item[3];
    row.getCell(5).value = item[4];
    row.getCell(6).value = zVal;
    row.getCell(7).value = Math.round(zUnit);

    for (let c = 1; c <= 7; c++) {
      const cell = row.getCell(c);
      cell.font = { name: "Times New Roman", size: 10 };
      cell.border = {
        top: { style: "thin", color: { argb: "FFD9D9D9" } },
        bottom: { style: "thin", color: { argb: "FFD9D9D9" } },
        left: { style: "thin", color: { argb: "FFD9D9D9" } },
        right: { style: "thin", color: { argb: "FFD9D9D9" } },
      };
      if (c === 1) cell.alignment = { horizontal: "center" };
      if (c >= 3) {
        cell.numFmt = "#,##0";
        cell.alignment = { horizontal: "right" };
      }
    }
  });

  const totalRow = ws.getRow(11);
  totalRow.getCell(2).value = "TỔNG CỘNG";
  totalRow.getCell(2).font = { name: "Times New Roman", size: 10, bold: true };
  totalRow.getCell(2).alignment = { horizontal: "center" };

  for (let c = 3; c <= 7; c++) {
    const colLetter = String.fromCharCode(64 + c);
    const cell = totalRow.getCell(c);
    cell.value = { formula: `SUM(${colLetter}8:${colLetter}10)` };
    cell.font = { name: "Times New Roman", size: 10, bold: true, color: { argb: "FFC00000" } };
    cell.numFmt = "#,##0";
    cell.alignment = { horizontal: "right" };
  }

  const widths = [6, 32, 20, 20, 20, 20, 20];
  widths.forEach((w, idx) => {
    ws.getColumn(idx + 1).width = w;
  });

  await wb.xlsx.writeFile(outputExcelPath);
  return { status: "success", output_excel: outputExcelPath };
}

export async function exportJournalExcel(outputExcelPath: string, rows: any[]) {
  const dir = path.dirname(path.resolve(outputExcelPath));
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet("Nhat_Ky_Chung");

  ws.getCell("A1").value = "DOANH NGHIỆP THƯƠNG MẠI & SẢN XUẤT";
  ws.getCell("A1").font = { name: "Times New Roman", size: 10, bold: true };
  ws.getCell("A2").value = "Mã số thuế: 0108998877";
  ws.getCell("A2").font = { name: "Times New Roman", size: 9, italic: true };

  ws.getCell("A4").value = "SỔ NHẬT KÝ CHUNG";
  ws.getCell("A4").font = { name: "Times New Roman", size: 16, bold: true, color: { argb: "FF002060" } };
  ws.getCell("A4").alignment = { horizontal: "center" };
  ws.mergeCells("A4:G4");

  ws.getCell("A5").value = "Năm tài chính 2026 (Mẫu S03a-DN)";
  ws.getCell("A5").font = { name: "Times New Roman", size: 11, italic: true };
  ws.getCell("A5").alignment = { horizontal: "center" };
  ws.mergeCells("A5:G5");

  const headers = ["Ngày ghi sổ", "Số hiệu CT", "Ngày CT", "Diễn giải", "TK Nợ", "TK Có", "Số tiền (VND)"];
  const headerRow = ws.getRow(7);
  headers.forEach((h, idx) => {
    const cell = headerRow.getCell(idx + 1);
    cell.value = h;
    cell.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FF1F4E79" },
    };
    cell.font = { name: "Times New Roman", size: 10, bold: true, color: { argb: "FFFFFFFF" } };
    cell.alignment = { horizontal: "center", vertical: "middle" };
  });

  rows.forEach((r, idx) => {
    const rIdx = 8 + idx;
    const row = ws.getRow(rIdx);
    row.getCell(1).value = r.ngay_ghi_so;
    row.getCell(2).value = r.so_chung_tu;
    row.getCell(3).value = r.ngay_chung_tu;
    row.getCell(4).value = r.dien_giai;
    row.getCell(5).value = r.tk_no;
    row.getCell(6).value = r.tk_co;
    row.getCell(7).value = Number(r.so_tien);

    for (let c = 1; c <= 7; c++) {
      const cell = row.getCell(c);
      cell.font = { name: "Times New Roman", size: 10 };
      cell.border = {
        top: { style: "thin", color: { argb: "FFD9D9D9" } },
        bottom: { style: "thin", color: { argb: "FFD9D9D9" } },
        left: { style: "thin", color: { argb: "FFD9D9D9" } },
        right: { style: "thin", color: { argb: "FFD9D9D9" } },
      };
      if ([1, 2, 3, 5, 6].includes(c)) cell.alignment = { horizontal: "center" };
      if (c === 7) {
        cell.numFmt = "#,##0";
        cell.alignment = { horizontal: "right" };
      }
    }
  });

  const totalIdx = 8 + rows.length;
  const totRow = ws.getRow(totalIdx);
  totRow.getCell(4).value = "CỘNG PHÁT SINH";
  totRow.getCell(4).font = { name: "Times New Roman", size: 11, bold: true };
  totRow.getCell(4).alignment = { horizontal: "center" };

  const sumCell = totRow.getCell(7);
  sumCell.value = { formula: `SUM(G8:G${totalIdx - 1})` };
  sumCell.font = { name: "Times New Roman", size: 11, bold: true, color: { argb: "FFC00000" } };
  sumCell.numFmt = "#,##0";
  sumCell.alignment = { horizontal: "right" };

  const widths = [15, 15, 15, 45, 12, 12, 20];
  widths.forEach((w, idx) => {
    ws.getColumn(idx + 1).width = w;
  });

  await wb.xlsx.writeFile(outputExcelPath);
  return { status: "success", output_excel: outputExcelPath };
}

export async function batchExportInvoicesToExcel(folderPath: string, outputExcelPath: string) {
  const dir = path.dirname(path.resolve(outputExcelPath));
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const files = fs.readdirSync(folderPath).filter((f) => f.toLowerCase().endsWith(".xml"));
  const parsedInvoices: ParsedInvoiceData[] = [];

  for (const f of files) {
    const fullPath = path.join(folderPath, f);
    try {
      const inv = parseVietnameseInvoiceXml(fullPath);
      parsedInvoices.push(inv);
    } catch (err) {
      console.error("Error parsing", f, err);
    }
  }

  const wb = new ExcelJS.Workbook();

  // Sheet 1: Bang_Ke_Tong_Hop
  const wsSummary = wb.addWorksheet("Bang_Ke_Tong_Hop");
  wsSummary.columns = [
    { header: "Số hóa đơn", key: "so_hoa_don", width: 14 },
    { header: "Ký hiệu", key: "ky_hieu", width: 12 },
    { header: "Ngày lập", key: "ngay_lap", width: 14 },
    { header: "Người bán", key: "nguoi_ban", width: 35 },
    { header: "MST người bán", key: "mst_ban", width: 16 },
    { header: "Người mua", key: "nguoi_mua", width: 35 },
    { header: "MST người mua", key: "mst_mua", width: 16 },
    { header: "Tổng tiền chưa thuế", key: "chua_thue", width: 20 },
    { header: "Tiền thuế GTGT", key: "thue", width: 16 },
    { header: "Tổng tiền thanh toán", key: "thanh_toan", width: 20 },
  ];

  parsedInvoices.forEach((inv) => {
    wsSummary.addRow({
      so_hoa_don: inv.so_hoa_don,
      ky_hieu: inv.ky_hieu,
      ngay_lap: inv.ngay_lap,
      nguoi_ban: inv.nguoi_ban.ten,
      mst_ban: inv.nguoi_ban.mst,
      nguoi_mua: inv.nguoi_mua.ten,
      mst_mua: inv.nguoi_mua.mst,
      chua_thue: inv.tong_tien_chua_thue,
      thue: inv.tong_tien_thue,
      thanh_toan: inv.tong_tien_thanh_toan,
    });
  });

  // Sheet 2: Chi_Tiet_Hang_Hoa
  const wsDetails = wb.addWorksheet("Chi_Tiet_Hang_Hoa");
  wsDetails.columns = [
    { header: "Số hóa đơn", key: "so_hoa_don", width: 14 },
    { header: "Ký hiệu", key: "ky_hieu", width: 12 },
    { header: "Ngày lập", key: "ngay_lap", width: 14 },
    { header: "STT", key: "stt", width: 8 },
    { header: "Tên hàng hóa, dịch vụ", key: "ten", width: 40 },
    { header: "Đơn vị tính", key: "dvt", width: 12 },
    { header: "Số lượng", key: "so_luong", width: 12 },
    { header: "Đơn giá", key: "don_gia", width: 16 },
    { header: "Thành tiền", key: "thanh_tien", width: 18 },
    { header: "Thuế suất", key: "thue_suat", width: 12 },
  ];

  parsedInvoices.forEach((inv) => {
    inv.chi_tiet_hang_hoa.forEach((item) => {
      wsDetails.addRow({
        so_hoa_don: inv.so_hoa_don,
        ky_hieu: inv.ky_hieu,
        ngay_lap: inv.ngay_lap,
        stt: item.stt,
        ten: item.ten,
        dvt: item.dvt,
        so_luong: item.so_luong,
        don_gia: item.don_gia,
        thanh_tien: item.thanh_tien,
        thue_suat: item.thue_suat,
      });
    });
  });

  await wb.xlsx.writeFile(outputExcelPath);

  return {
    status: "success",
    total_invoices_processed: parsedInvoices.length,
    output_excel: outputExcelPath,
  };
}
