import fs from "fs";
import { XMLParser } from "fast-xml-parser";
// @ts-ignore
import { PDFParse } from "pdf-parse";

export interface ParsedItem {
  stt?: number | string;
  ten?: string;
  dvt?: string;
  so_luong?: number;
  don_gia?: number;
  thanh_tien?: number;
  thue_suat?: string;
}

export interface ParsedInvoiceData {
  so_hoa_don: string;
  ky_hieu: string;
  ngay_lap: string;
  nguoi_ban: {
    ten: string;
    mst: string;
    dia_chi?: string;
  };
  nguoi_mua: {
    ten: string;
    mst: string;
    dia_chi?: string;
  };
  tong_tien_chua_thue: number;
  tong_tien_thue: number;
  tong_tien_thanh_toan: number;
  chi_tiet_hang_hoa: ParsedItem[];
}

export function parseVietnameseInvoiceXml(filePath: string): ParsedInvoiceData {
  const xmlContent = fs.readFileSync(filePath, "utf-8");
  const parser = new XMLParser({
    ignoreAttributes: false,
    parseTagValue: false, // Giữ nguyên chuỗi để không mất số 0 đầu ở MST và Số HĐ
    trimValues: true,
  });

  const jsonObj = parser.parse(xmlContent);

  const hdon = jsonObj.HDon || jsonObj;
  const dlHDon = hdon.DLHDon || hdon;
  const ndHDon = dlHDon.NDHDon || dlHDon;
  const ttChung = ndHDon.TTChung || dlHDon.TTChung || hdon.TTChung || {};
  const nBan = ndHDon.NBan || {};
  const nMua = ndHDon.NMua || {};
  const tToan = ndHDon.TToan || {};

  const dsContainer = ndHDon.DSHHDVu || ndHDon.DSHHDV || {};
  const dsHHDVu = dsContainer.HHDVu || dsContainer.HHDV || [];

  const rawItems = Array.isArray(dsHHDVu) ? dsHHDVu : [dsHHDVu].filter(Boolean);
  const items: ParsedItem[] = rawItems.map((item: any) => ({
    stt: item.STT || "",
    ten: item.THHDVu || item.THHDV || item.Ten || "",
    dvt: item.DVTinh || item.DVT || "",
    so_luong: Number(item.SLuong || 0),
    don_gia: Number(item.DGia || 0),
    thanh_tien: Number(item.ThTien || 0),
    thue_suat: String(item.TSuat || ""),
  }));

  const rawSoHd = String(ttChung.SHDon || ttChung.SoHoaDon || "").trim();
  const soHoaDon = rawSoHd ? rawSoHd.padStart(7, "0") : "";
  const kyHieu = String(ttChung.KHHDon || ttChung.KHMSHDon || "").trim();
  const ngayLap = String(ttChung.NLap || "");

  const tongChuaThue = Number(tToan.TgTCThue || tToan.TongTienChuaThue || 0);
  const tongThue = Number(tToan.TgTThue || tToan.TongTienThue || 0);
  const tongThanhToan = Number(tToan.TgTTTBSo || tToan.TongTienThanhToan || 0);

  return {
    so_hoa_don: soHoaDon,
    ky_hieu: kyHieu,
    ngay_lap: ngayLap,
    nguoi_ban: {
      ten: nBan.Ten || nBan.TenNNBan || "",
      mst: String(nBan.MST || "").trim(),
      dia_chi: nBan.DChi || "",
    },
    nguoi_mua: {
      ten: nMua.Ten || nMua.TenNNMua || "",
      mst: String(nMua.MST || "").trim(),
      dia_chi: nMua.DChi || "",
    },
    tong_tien_chua_thue: tongChuaThue,
    tong_tien_thue: tongThue,
    tong_tien_thanh_toan: tongThanhToan,
    chi_tiet_hang_hoa: items,
  };
}

export async function parseVietnameseInvoicePdf(filePath: string) {
  const dataBuffer = fs.readFileSync(filePath);
  const parser = new PDFParse({ data: dataBuffer });
  const textResult = await parser.getText();
  const text = typeof textResult === "string" ? textResult : textResult.text || "";

  const soHdMatch = text.match(/(?:So\s*hoa\s*don|Số\s*hóa\s*đơn|Số)\s*[:\.]?\s*(\d{7}|\d+)/i);
  const kyHieuMatch = text.match(/(?:Ky\s*hieu|Ký\s*hiệu)\s*[:\.]?\s*([A-Z0-9]+)/i);
  const mstMatches = [...text.matchAll(/(?:Mã\s*số\s*thuế|Ma\s*so\s*thue|MST)\s*[:\.]?\s*(\d{10,13})/gi)];

  const mstBan = mstMatches[0] ? mstMatches[0][1] : "";
  const mstMua = mstMatches[1] ? mstMatches[1][1] : "";

  const tienHangMatch = text.match(/(?:Cộng\s*tiền\s*hàng|Cong\s*tien\s*hang)\s*[:\.]?\s*([\d\.,]+)/i);
  const tienThueMatch = text.match(/(?:Tiền\s*thuế\s*GTGT|Tien\s*thue\s*GTGT|Tien\s*thue)\s*[:\.]?\s*([\d\.,]+)/i);
  const tongTienMatch = text.match(/(?:Tổng\s*cộng\s*tiền\s*thanh\s*toán|Tong\s*cong\s*tien\s*thanh\s*toan|Tong\s*tien\s*thanh\s*toan|Tổng\s*tiền\s*thanh\s*toán)\s*[:\.]?\s*([\d\.,]+)/i);

  const cleanNum = (str: string | undefined) => {
    if (!str) return 0;
    return parseFloat(str.replace(/[\.,\s]/g, ""));
  };

  return {
    so_hoa_don: soHdMatch ? soHdMatch[1] : "",
    ky_hieu: kyHieuMatch ? kyHieuMatch[1] : "",
    mst_nguoi_ban: mstBan,
    mst_nguoi_mua: mstMua,
    tien_hang: tienHangMatch ? cleanNum(tienHangMatch[1]) : 0,
    tien_thue: tienThueMatch ? cleanNum(tienThueMatch[1]) : 0,
    tong_thanh_toan: tongTienMatch ? cleanNum(tongTienMatch[1]) : 0,
  };
}
