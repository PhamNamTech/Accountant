import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import os from 'os';
import multer from 'multer';
import { lookupAccountingAccount } from '../core/accounts.js';
import { calculateProductCost, allocateOverheadCosts } from '../core/cost.js';
import {
  getJournalEntries,
  createJournalEntry,
  getJournalStats,
  getAllJournalEntriesForExport,
} from '../core/database.js';
import {
  parseVietnameseInvoiceXml,
  parseVietnameseInvoicePdf,
} from '../core/invoiceParser.js';
import { reconcileBankStatement } from '../core/reconcile.js';

const app = express();
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 8000;
const upload = multer({ dest: os.tmpdir() });

app.use(cors());
app.use(express.json());

// 1. Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    backend: 'Node.js Express / TypeScript Suite',
    current_regime: 'Thông tư 99/2025/TT-BTC (Mặc định cho năm tài chính 2026)',
    timestamp: new Date().toISOString(),
  });
});

// 2. Tra cứu tài khoản kế toán
app.get('/api/accounts/lookup', (req, res) => {
  const query = (req.query.query as string) || '';
  const regime = (req.query.regime as string) || 'TT99';
  const result = lookupAccountingAccount(query, regime);
  res.json(result);
});

// 3. Tính giá thành sản phẩm & VAS 02
app.post('/api/cost/calculate', (req, res) => {
  try {
    const b = req.body;
    const result = calculateProductCost({
      productName: b.product_name || b.productName || 'Sản phẩm mới',
      dDauKy: Number(b.d_dau_ky ?? b.dDauKy ?? 0),
      cpNvlTrucTiep: Number(b.cp_nvl_truc_tiep ?? b.cpNvlTrucTiep ?? 0),
      cpNhanCongTrucTiep: Number(b.cp_nhan_cong_truc_tiep ?? b.cpNhanCongTrucTiep ?? 0),
      cpSanXuatChung: Number(b.cp_san_xuat_chung ?? b.cpSanXuatChung ?? 0),
      dCuoiKy: Number(b.d_cuoi_ky ?? b.dCuoiKy ?? 0),
      slHoanThanh: Number(b.sl_hoan_thanh ?? b.slHoanThanh ?? 1),
      pheLieuThuHoi: Number(b.phe_lieu_thu_hoi ?? b.pheLieuThuHoi ?? 0),
      regime: b.regime || 'TT99',
      congSuatThucTe: b.cong_suat_thuc_te ?? b.congSuatThucTe,
      congSuatDinhMuc: b.cong_suat_dinh_muc ?? b.congSuatDinhMuc,
      tyLeSxcCoDinh: Number(b.ty_le_sxc_co_dinh ?? b.tyLeSxcCoDinh ?? 50.0),
    });
    res.json(result);
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

// 4. Phân bổ chi phí sản xuất chung
app.post('/api/cost/allocate', (req, res) => {
  try {
    const b = req.body;
    const totalOverhead = Number(b.total_overhead ?? b.totalOverhead ?? 0);
    const products = b.products || [];
    const criteria = b.criteria || 'nvl';
    const result = allocateOverheadCosts(totalOverhead, products, criteria);
    res.json(result);
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

// 5. Quản lý sổ Nhật ký chung (SQLite)
app.get('/api/journal/entries', (req, res) => {
  const { search, tk, fromDate, toDate, limit, offset } = req.query;
  const result = getJournalEntries({
    search: search as string,
    tk: tk as string,
    fromDate: fromDate as string,
    toDate: toDate as string,
    limit: limit ? parseInt(limit as string, 10) : 100,
    offset: offset ? parseInt(offset as string, 10) : 0,
  });
  res.json(result);
});

app.post('/api/journal/entries', (req, res) => {
  try {
    const result = createJournalEntry(req.body);
    res.json(result);
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get('/api/journal/stats', (req, res) => {
  res.json(getJournalStats());
});

// 6. Bóc tách hóa đơn điện tử XML
app.post('/api/invoices/parse-xml', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Không tìm thấy file tải lên' });
  }
  try {
    const parsed = parseVietnameseInvoiceXml(req.file.path);
    fs.unlinkSync(req.file.path);
    res.json(parsed);
  } catch (err: any) {
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    res.status(400).json({ error: err.message });
  }
});

// 7. Bóc tách hóa đơn điện tử PDF
app.post('/api/invoices/parse-pdf', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Không tìm thấy file tải lên' });
  }
  try {
    const parsed = await parseVietnameseInvoicePdf(req.file.path);
    fs.unlinkSync(req.file.path);
    res.json(parsed);
  } catch (err: any) {
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    res.status(400).json({ error: err.message });
  }
});

// 8. Đối soát sao kê ngân hàng
app.post('/api/reconcile/bank-statement', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Không tìm thấy file sao kê tải lên' });
  }
  try {
    const result = reconcileBankStatement(req.file.path);
    fs.unlinkSync(req.file.path);
    res.json(result);
  } catch (err: any) {
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    res.status(400).json({ error: err.message });
  }
});

// 9. Căn cứ pháp lý
app.get('/api/legal-basis', (req, res) => {
  const legalPath = path.resolve(process.cwd(), 'legal-basis.md');
  const content = fs.existsSync(legalPath) ? fs.readFileSync(legalPath, 'utf-8') : '';
  res.json({
    status: 'success',
    last_updated: '2026-10-17',
    summary_matrix: [
      {
        category: 'Chế độ Kế toán Doanh nghiệp',
        criterion: 'Xác định theo Năm tài chính',
        rules: [
          { code: 'TT 99/2025/TT-BTC', target: 'Năm tài chính từ 01/01/2026', status: 'Hiệu lực chính' },
          { code: 'TT 200/2014/TT-BTC', target: 'Năm tài chính bắt đầu trước 2026', status: 'Kỳ cũ' },
          { code: 'TT 133/2016/TT-BTC', target: 'Doanh nghiệp nhỏ và vừa (DNNVV)', status: 'Đang áp dụng' },
          { code: 'TT 58/2026/TT-BTC', target: 'Doanh nghiệp siêu nhỏ (Từ 01/07/2026)', status: 'Sắp hiệu lực' },
        ],
      },
      {
        category: 'Hóa đơn & Chứng từ',
        criterion: 'Xác định theo Ngày lập hóa đơn',
        rules: [
          { code: 'NĐ 254/2026/NĐ-CP & TT 91/2026/TT-BTC', target: 'Hóa đơn lập từ 01/07/2026 trở đi', status: 'Mới nhất' },
          { code: 'NĐ 123/2020 & TT 32/2025 (sửa NĐ 70/2025)', target: 'Hóa đơn lập từ 01/06/2025 đến 30/06/2026', status: 'Chuyển tiếp' },
          { code: 'NĐ 123/2020 & TT 78/2021', target: 'Hóa đơn lập trước 01/06/2025', status: 'Kỳ cũ' },
        ],
      },
      {
        category: 'Thuế TNDN & Thuế TNCN',
        criterion: 'Xác định theo Kỳ tính thuế',
        rules: [
          { code: 'Luật Thuế TNDN số 67/2025/QH15', target: 'Kỳ tính thuế từ năm 2025 trở đi', status: 'Hiệu lực' },
          { code: 'Luật Thuế TNCN số 109/2025/QH15 & TT 87/2026', target: 'Kỳ tính thuế từ 2026 (Từ 01/07/2026 toàn diện)', status: 'Hiệu lực' },
        ],
      },
      {
        category: 'Thuế GTGT & Quản lý thuế',
        criterion: 'Xác định theo Thời điểm phát sinh / Ngày nộp',
        rules: [
          { code: 'Luật Thuế GTGT số 48/2024/QH15', target: 'Hiệu lực từ 01/07/2025', status: 'Hiệu lực' },
          { code: 'Luật Quản lý thuế số 108/2025/QH15', target: 'Hiệu lực từ 01/07/2026', status: 'Hiệu lực' },
        ],
      },
    ],
    markdown_full: content,
  });
});

// 10. Phục vụ Frontend static files nếu đã build
const frontendDist = path.resolve(process.cwd(), 'web', 'frontend', 'dist');
if (fs.existsSync(frontendDist)) {
  app.use(express.static(frontendDist));
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api')) return next();
    res.sendFile(path.join(frontendDist, 'index.html'));
  });
}

if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`[Express] Vietnam Accounting Suite đang chạy tại http://localhost:${PORT}`);
  });
}

export default app;
