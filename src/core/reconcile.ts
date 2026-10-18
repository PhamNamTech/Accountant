import * as fs from 'fs';
import * as path from 'path';
import * as xlsx from 'xlsx';
import { getDb } from './database.js';

export interface BankTransaction {
  stt: number;
  ngay: string;
  ghi_no_tien_ra: number;
  ghi_co_tien_vao: number;
  so_du: number;
  noi_dung: string;
}

export interface ReconciledTransaction extends BankTransaction {
  status: 'MATCHED' | 'BANK_ONLY';
  matched_info?: any;
}

export interface ReconciliationResult {
  total_bank_transactions: number;
  matched_count: number;
  bank_only_count: number;
  ledger_only_count: number;
  total_bank_in: number;
  total_bank_out: number;
  transactions: ReconciledTransaction[];
  unmatched_ledger_transactions: any[];
}

/**
 * Phân tích file sao kê Excel Vietcombank (.xls / .xlsx)
 */
export function parseVcbExcel(filePathOrBuffer: string | Buffer): BankTransaction[] {
  let workbook: xlsx.WorkBook;
  if (typeof filePathOrBuffer === 'string') {
    workbook = xlsx.readFile(filePathOrBuffer);
  } else {
    workbook = xlsx.read(filePathOrBuffer, { type: 'buffer' });
  }

  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  const rows: any[][] = xlsx.utils.sheet_to_json(sheet, { header: 1 });

  let headerIdx = -1;
  for (let i = 0; i < rows.length; i++) {
    const rowStr = (rows[i] || []).map((c: any) => String(c ?? '')).join(' ');
    if (
      rowStr.includes('STT') &&
      (rowStr.toLowerCase().includes('debit') ||
        rowStr.toLowerCase().includes('ghi nợ') ||
        rowStr.toLowerCase().includes('tnx date') ||
        rowStr.toLowerCase().includes('ngày'))
    ) {
      headerIdx = i;
      break;
    }
  }

  if (headerIdx === -1) {
    headerIdx = 12; // Fallback VCB standard row 13 (0-indexed 12)
  }

  const records: BankTransaction[] = [];
  for (let i = headerIdx + 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length === 0) continue;

    const sttRaw = row[0];
    if (sttRaw === undefined || sttRaw === null) continue;
    const sttStr = String(sttRaw).trim();
    if (!/^\d+$/.test(sttStr)) continue;

    const ngayVal = String(row[1] ?? '').trim();
    const ngay = ngayVal.includes('/') ? ngayVal.split('/')[0].trim() : ngayVal;

    const parseNum = (val: any): number => {
      if (val === undefined || val === null) return 0;
      const s = String(val).replace(/,/g, '').trim();
      const n = parseFloat(s);
      return isNaN(n) ? 0 : n;
    };

    const debit = parseNum(row[3]);
    const credit = parseNum(row[4]);
    const balance = parseNum(row[5]);
    const content = String(row[6] ?? '').trim();

    records.push({
      stt: parseInt(sttStr, 10),
      ngay,
      ghi_no_tien_ra: debit,
      ghi_co_tien_vao: credit,
      so_du: balance,
      noi_dung: content
    });
  }

  return records;
}

/**
 * Thực hiện đối soát sao kê với Sổ Nhật Ký Chung (TK 112)
 */
export function reconcileBankStatement(
  filePathOrBuffer: string | Buffer,
  dbPath?: string
): ReconciliationResult {
  const bankTxns = parseVcbExcel(filePathOrBuffer);

  const db = getDb(dbPath);
  const ledgerRows = db
    .prepare(
      `SELECT id, ngay_ghi_so, so_chung_tu, dien_giai, tk_no, tk_co, so_tien 
       FROM nhat_ky_chung 
       WHERE tk_no LIKE '112%' OR tk_co LIKE '112%'`
    )
    .all() as any[];

  const ledgerTxns = ledgerRows.map((r) => ({
    id: r.id,
    ngay: r.ngay_ghi_so,
    so_ct: r.so_chung_tu,
    dien_giai: r.dien_giai,
    tk_no: r.tk_no,
    tk_co: r.tk_co,
    so_tien: Number(r.so_tien),
    matched: false
  }));

  const results: ReconciledTransaction[] = [];
  let matchedCount = 0;
  let totalBankIn = 0;
  let totalBankOut = 0;

  for (const b of bankTxns) {
    totalBankIn += b.ghi_co_tien_vao;
    totalBankOut += b.ghi_no_tien_ra;

    let matched = false;
    let matchedLedger: any = null;
    const amt = b.ghi_no_tien_ra > 0 ? b.ghi_no_tien_ra : b.ghi_co_tien_vao;

    for (const l of ledgerTxns) {
      if (!l.matched && Math.abs(l.so_tien - amt) < 1.0) {
        l.matched = true;
        matched = true;
        matchedLedger = l;
        matchedCount++;
        break;
      }
    }

    results.push({
      ...b,
      status: matched ? 'MATCHED' : 'BANK_ONLY',
      matched_info: matchedLedger
    });
  }

  const unmatchedLedger = ledgerTxns.filter((l) => !l.matched);

  return {
    total_bank_transactions: bankTxns.length,
    matched_count: matchedCount,
    bank_only_count: bankTxns.length - matchedCount,
    ledger_only_count: unmatchedLedger.length,
    total_bank_in: totalBankIn,
    total_bank_out: totalBankOut,
    transactions: results,
    unmatched_ledger_transactions: unmatchedLedger
  };
}
