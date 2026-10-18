import path from "path";
import Database from "better-sqlite3";

const DB_PATH = path.resolve(process.cwd(), "data", "database", "ketoan.db");

let dbInstance: Database.Database | null = null;

export function getDatabase(customPath?: string) {
  if (customPath) {
    const db = new Database(customPath);
    db.pragma("journal_mode = WAL");
    return db;
  }
  if (!dbInstance) {
    dbInstance = new Database(DB_PATH);
    dbInstance.pragma("journal_mode = WAL");
  }
  return dbInstance;
}

export const getDb = getDatabase;

export interface JournalEntry {
  id?: number;
  ngay_ghi_so: string;
  so_chung_tu: string;
  ngay_chung_tu: string;
  dien_giai: string;
  tk_no: string;
  tk_co: string;
  so_tien: number;
}

export interface QueryFilters {
  search?: string;
  tk?: string;
  fromDate?: string;
  toDate?: string;
  limit?: number;
  offset?: number;
}

export function getJournalEntries(filters: QueryFilters = {}) {
  const db = getDatabase();
  const { search, tk, fromDate, toDate, limit = 100, offset = 0 } = filters;

  let query = "SELECT * FROM nhat_ky_chung WHERE 1=1";
  const params: any[] = [];

  if (search) {
    query += " AND (so_chung_tu LIKE ? OR dien_giai LIKE ?)";
    params.push(`%${search}%`, `%${search}%`);
  }
  if (tk) {
    query += " AND (tk_no LIKE ? OR tk_co LIKE ?)";
    params.push(`${tk}%`, `${tk}%`);
  }
  if (fromDate) {
    query += " AND ngay_ghi_so >= ?";
    params.push(fromDate);
  }
  if (toDate) {
    query += " AND ngay_ghi_so <= ?";
    params.push(toDate);
  }

  query += " ORDER BY id DESC LIMIT ? OFFSET ?";
  params.push(limit, offset);

  const rows = db.prepare(query).all(...params);

  const countRow: any = db.prepare("SELECT COUNT(*) as count, COALESCE(SUM(so_tien), 0) as total FROM nhat_ky_chung").get();

  return {
    total_records: countRow.count,
    total_amount: countRow.total,
    items: rows,
  };
}

export function createJournalEntry(entry: JournalEntry) {
  const db = getDatabase();
  const stmt = db.prepare(`
    INSERT INTO nhat_ky_chung (ngay_ghi_so, so_chung_tu, ngay_chung_tu, dien_giai, tk_no, tk_co, so_tien)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  const info = stmt.run(
    entry.ngay_ghi_so,
    entry.so_chung_tu,
    entry.ngay_chung_tu,
    entry.dien_giai,
    entry.tk_no,
    entry.tk_co,
    entry.so_tien
  );

  return {
    status: "success",
    id: info.lastInsertRowid,
    message: "Đã ghi sổ thành công",
  };
}

export function getJournalStats() {
  const db = getDatabase();
  const totalRow: any = db.prepare("SELECT COUNT(*) as count, COALESCE(SUM(so_tien), 0) as total FROM nhat_ky_chung").get();

  const topDebit = db.prepare(`
    SELECT tk_no, SUM(so_tien) as total 
    FROM nhat_ky_chung 
    GROUP BY tk_no 
    ORDER BY total DESC LIMIT 5
  `).all();

  const topCredit = db.prepare(`
    SELECT tk_co, SUM(so_tien) as total 
    FROM nhat_ky_chung 
    GROUP BY tk_co 
    ORDER BY total DESC LIMIT 5
  `).all();

  return {
    total_transactions: totalRow.count,
    total_amount: totalRow.total,
    top_debit_accounts: topDebit,
    top_credit_accounts: topCredit,
  };
}

export function getAllJournalEntriesForExport() {
  const db = getDatabase();
  return db.prepare(`
    SELECT ngay_ghi_so, so_chung_tu, ngay_chung_tu, dien_giai, tk_no, tk_co, so_tien 
    FROM nhat_ky_chung 
    ORDER BY ngay_ghi_so ASC, id ASC
  `).all();
}
