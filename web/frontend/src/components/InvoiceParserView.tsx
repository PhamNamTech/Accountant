import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Building,
  User,
  ArrowRight,
  Download,
  Sparkles,
  Database,
} from 'lucide-react';

interface InvoiceData {
  file_name?: string;
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
  tong_tien_chua_thue?: number;
  tien_thue_gtgt?: number;
  tien_hang?: number | string;
  tien_thue?: number | string;
  tong_tien_thanh_toan?: number;
  tong_thanh_toan?: number | string;
  chi_tiet_hang_hoa?: Array<{
    stt?: number | string;
    ten_hang?: string;
    ten?: string;
    dvt?: string;
    so_luong?: number | string;
    don_gia?: number | string;
    thanh_tien?: number | string;
    thue_suat?: string;
  }>;
}

interface SampleFile {
  name: string;
  path: string;
  type: string;
  folder: string;
}

export const InvoiceParserView: React.FC = () => {
  const [invoice, setInvoice] = useState<InvoiceData | null>(null);
  const [samples, setSamples] = useState<SampleFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSubTab, setActiveSubTab] = useState<'details' | 'items' | 'json'>('details');

  // Ghi sổ trực tiếp từ hóa đơn
  const [recording, setRecording] = useState(false);
  const [recordSuccess, setRecordSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/invoices/samples')
      .then((r) => r.json())
      .then((d) => setSamples(d.samples || []))
      .catch(() => {});
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setRecordSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    const isPdf = file.name.toLowerCase().endsWith('.pdf');
    const endpoint = isPdf ? '/api/invoices/parse-pdf' : '/api/invoices/parse-xml';

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Lỗi bóc tách hóa đơn');
      setInvoice(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async (samplePath: string) => {
    setLoading(true);
    setError(null);
    setRecordSuccess(null);
    try {
      const res = await fetch(`/api/invoices/load-sample?path=${encodeURIComponent(samplePath)}`, {
        method: 'POST',
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Lỗi đọc hóa đơn mẫu');
      setInvoice(data.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordToJournal = async () => {
    if (!invoice) return;
    setRecording(true);
    setRecordSuccess(null);

    try {
      const tienHang = typeof invoice.tong_tien_chua_thue === 'number' 
        ? invoice.tong_tien_chua_thue 
        : parseFloat(String(invoice.tien_hang || '0').replace(/,/g, ''));
      
      const tienThue = typeof invoice.tien_thue_gtgt === 'number' 
        ? invoice.tien_thue_gtgt 
        : parseFloat(String(invoice.tien_thue || '0').replace(/,/g, ''));

      const today = new Date().toISOString().split('T')[0];
      const ngayHd = invoice.ngay_lap && invoice.ngay_lap.includes('/')
        ? invoice.ngay_lap.split('/').reverse().join('-')
        : (invoice.ngay_lap || today);

      // Bút toán 1: Tiền hàng Nợ 152 / Có 331
      if (tienHang > 0) {
        await fetch('/api/journal/entries', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ngay_ghi_so: today,
            so_chung_tu: `PNK-${invoice.so_hoa_don || 'HĐ'}`,
            ngay_chung_tu: ngayHd,
            dien_giai: `Mua hàng từ ${invoice.nguoi_ban?.ten || 'NCC'} (HĐ số ${invoice.so_hoa_don})`,
            tk_no: '152',
            tk_co: '331',
            so_tien: tienHang,
          }),
        });
      }

      // Bút toán 2: Thuế GTGT đầu vào Nợ 1331 / Có 331
      if (tienThue > 0) {
        await fetch('/api/journal/entries', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ngay_ghi_so: today,
            so_chung_tu: `PNK-${invoice.so_hoa_don || 'HĐ'}`,
            ngay_chung_tu: ngayHd,
            dien_giai: `Thuế GTGT đầu vào HĐ số ${invoice.so_hoa_don}`,
            tk_no: '1331',
            tk_co: '331',
            so_tien: tienThue,
          }),
        });
      }

      setRecordSuccess(`Đã ghi sổ thành công bút toán hóa đơn ${invoice.so_hoa_don} vào SQLite (TK 152 & TK 1331 / TK 331)!`);
    } catch (err: any) {
      setError('Lỗi khi ghi sổ hóa đơn: ' + err.message);
    } finally {
      setRecording(false);
    }
  };

  const formatVND = (val: any) => {
    if (!val) return '0 ₫';
    const num = typeof val === 'number' ? val : parseFloat(String(val).replace(/,/g, ''));
    if (isNaN(num)) return String(val) + ' ₫';
    return new Intl.NumberFormat('vi-VN').format(num) + ' ₫';
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header Info */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-kinpaku/10 border border-kinpaku/30 text-kinpaku text-xs font-mono">
                <FileText className="w-3.5 h-3.5" />
                <span>Trình Bóc Tách Hóa Đơn Điện Tử XML & PDF</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Bóc Tách & Hạch Toán Hóa Đơn Tự Động</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Hỗ trợ bóc tách hóa đơn điện tử XML (chuẩn Thông tư 78/2021 & Nghị định 123/2020) và hóa đơn điện tử PDF. Tự động kiểm tra tính toàn vẹn và trích xuất danh mục hàng hóa.
              </p>
            </div>

            {/* Quick action: Batch export button */}
            <a
              href="/api/journal/export-excel"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-graphite hover:bg-graphite-2 text-warm hover:text-champagne border border-white/10 text-xs font-medium transition-colors w-fit cursor-pointer active:scale-95"
            >
              <Download className="w-4 h-4 text-kinpaku" />
              <span>Xuất Sổ Kê Khai Excel</span>
            </a>
          </div>

          {/* Upload Zone & Samples Selector */}
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Drag & Drop Upload Zone */}
            <div className="lg:col-span-7">
              <label className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed border-white/10 hover:border-kinpaku/50 bg-graphite/40 hover:bg-graphite/70 transition-all cursor-pointer group text-center">
                <div className="w-12 h-12 rounded-2xl bg-kinpaku/15 border border-kinpaku/30 flex items-center justify-center text-kinpaku group-hover:scale-110 transition-transform mb-3 shadow-[0_0_15px_-3px_rgba(245,196,81,0.25)]">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-xs font-semibold text-champagne">
                  Kéo thả tệp hóa đơn vào đây hoặc <span className="text-kinpaku underline">chọn tệp từ máy tính</span>
                </p>
                <p className="text-[11px] text-faint mt-1">Định dạng hỗ trợ: .XML (Chuẩn TT 78) hoặc .PDF điện tử</p>
                <input
                  type="file"
                  accept=".xml,.pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>

            {/* Sample Invoices (1-Click Test) */}
            <div className="lg:col-span-5 flex flex-col justify-between p-4 rounded-2xl bg-graphite border border-white/[0.06]">
              <div>
                <div className="flex items-center gap-2 text-xs font-semibold text-champagne mb-2">
                  <Sparkles className="w-3.5 h-3.5 text-kinpaku" />
                  <span>Nạp Hóa Đơn Mẫu Có Sẵn (1-Click Test)</span>
                </div>
                <p className="text-[11px] text-muted mb-3">
                  Chọn ngay hóa đơn mẫu từ bộ kiểm thử của dự án để xem kết quả bóc tách ngay lập tức:
                </p>

                <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                  {samples.map((s) => (
                    <button
                      key={s.path}
                      onClick={() => handleLoadSample(s.path)}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-lacquer-deep hover:bg-kinpaku/10 hover:border-kinpaku/30 border border-white/[0.05] text-xs text-warm transition-colors text-left cursor-pointer active:scale-98"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold border ${
                          s.type === 'XML' ? 'bg-patina/20 text-patina border-patina/30' : 'bg-kinpaku/20 text-kinpaku border-kinpaku/30'
                        }`}>
                          {s.type}
                        </span>
                        <span className="truncate text-[11px]">{s.name}</span>
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-faint shrink-0 ml-2" />
                    </button>
                  ))}
                </div>
              </div>

              {loading && (
                <div className="mt-3 text-center text-xs text-kinpaku animate-pulse font-mono">
                  Đang bóc tách dữ liệu chứng từ...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-vermilion/15 border border-vermilion/30 text-xs text-champagne flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-vermilion" />
          <span>{error}</span>
        </div>
      )}

      {recordSuccess && (
        <div className="p-4 rounded-xl bg-patina/15 border border-patina/30 text-xs text-champagne flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-patina" />
          <span>{recordSuccess}</span>
        </div>
      )}

      {/* Parsed Result Display */}
      {invoice && (
        <div className="space-y-5 animate-fadeIn">
          
          {/* Subtabs: Details vs Items vs Raw JSON */}
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveSubTab('details')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  activeSubTab === 'details'
                    ? 'bg-kinpaku/15 text-champagne border border-kinpaku/35 font-bold'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                Thông Tin Chung
              </button>
              <button
                onClick={() => setActiveSubTab('items')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  activeSubTab === 'items'
                    ? 'bg-kinpaku/15 text-champagne border border-kinpaku/35 font-bold'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                Chi Tiết Hàng Hóa ({invoice.chi_tiet_hang_hoa?.length || 0})
              </button>
              <button
                onClick={() => setActiveSubTab('json')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  activeSubTab === 'json'
                    ? 'bg-kinpaku/15 text-champagne border border-kinpaku/35 font-bold'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                Mã Dữ Liệu JSON
              </button>
            </div>

            {/* Direct Journal Recording Button */}
            <button
              onClick={handleRecordToJournal}
              disabled={recording}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-xl bg-kinpaku hover:bg-kinpaku-vivid text-on-gold font-bold text-xs transition-all shadow-[0_0_15px_-3px_rgba(245,196,81,0.4)] active:scale-95 cursor-pointer disabled:opacity-50"
            >
              <Database className="w-3.5 h-3.5" />
              <span>{recording ? 'Đang Ghi Sổ...' : 'Ghi Bút Toán Hóa Đơn Vào Sổ Kép'}</span>
            </button>
          </div>

          {activeSubTab === 'details' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              
              {/* Box 1: Seller Info */}
              <div className="double-bezel">
                <div className="double-bezel-inner p-5 space-y-3 h-full">
                  <div className="flex items-center gap-2 text-kinpaku text-xs font-semibold">
                    <Building className="w-4 h-4" />
                    <span>BÊN BÁN (SELLER)</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-champagne">{invoice.nguoi_ban?.ten || 'N/A'}</p>
                    <p className="text-xs text-kinpaku font-mono mt-1 font-bold">
                      MST: {invoice.nguoi_ban?.mst || 'Chưa nhận diện'}
                    </p>
                    <p className="text-[11px] text-muted mt-2 leading-relaxed">
                      {invoice.nguoi_ban?.dia_chi || 'Địa chỉ: N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Box 2: Buyer Info */}
              <div className="double-bezel">
                <div className="double-bezel-inner p-5 space-y-3 h-full">
                  <div className="flex items-center gap-2 text-patina text-xs font-semibold">
                    <User className="w-4 h-4" />
                    <span>BÊN MUA (BUYER)</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-champagne">{invoice.nguoi_mua?.ten || 'N/A'}</p>
                    <p className="text-xs text-patina font-mono mt-1 font-bold">
                      MST: {invoice.nguoi_mua?.mst || 'Chưa nhận diện'}
                    </p>
                    <p className="text-[11px] text-muted mt-2 leading-relaxed">
                      {invoice.nguoi_mua?.dia_chi || 'Địa chỉ: N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Box 3: Invoice Meta & Financial Totals */}
              <div className="double-bezel">
                <div className="double-bezel-inner p-5 space-y-3 h-full flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="text-muted">Số hóa đơn:</span>
                      <span className="font-mono font-bold text-champagne px-2 py-0.5 rounded bg-white/10">
                        {invoice.so_hoa_don || 'N/A'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="text-muted">Ký hiệu:</span>
                      <span className="font-mono text-patina font-bold">{invoice.ky_hieu || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs mb-3">
                      <span className="text-muted">Ngày lập:</span>
                      <span className="font-mono text-warm">{invoice.ngay_lap || 'N/A'}</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-white/[0.08] space-y-1.5">
                    <div className="flex justify-between text-xs text-muted">
                      <span>Cộng tiền hàng:</span>
                      <span className="font-mono text-champagne tabular-nums">
                        {formatVND(invoice.tong_tien_chua_thue || invoice.tien_hang)}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-muted">
                      <span>Tiền thuế GTGT:</span>
                      <span className="font-mono text-kinpaku tabular-nums font-semibold">
                        {formatVND(invoice.tien_thue_gtgt || invoice.tien_thue)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm font-bold pt-1 border-t border-white/[0.08]">
                      <span className="text-champagne">Tổng thanh toán:</span>
                      <span className="font-mono text-kinpaku text-base tabular-nums font-extrabold">
                        {formatVND(invoice.tong_tien_thanh_toan || invoice.tong_thanh_toan)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          )}

          {activeSubTab === 'items' && (
            <div className="double-bezel">
              <div className="double-bezel-inner overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-warm">
                    <thead className="bg-lacquer-deep text-[11px] uppercase tracking-wider text-faint border-b border-white/[0.08]">
                      <tr>
                        <th className="py-3 px-4 text-center">STT</th>
                        <th className="py-3 px-4">Tên Hàng Hóa, Dịch Vụ</th>
                        <th className="py-3 px-4 text-center">ĐVT</th>
                        <th className="py-3 px-4 text-right">Số Lượng</th>
                        <th className="py-3 px-4 text-right">Đơn Giá</th>
                        <th className="py-3 px-4 text-right">Thành Tiền</th>
                        <th className="py-3 px-4 text-center">Thuế Suất</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.06]">
                      {invoice.chi_tiet_hang_hoa && invoice.chi_tiet_hang_hoa.length > 0 ? (
                        invoice.chi_tiet_hang_hoa.map((item, idx) => (
                          <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                            <td className="py-3 px-4 text-center font-mono text-faint">{item.stt || idx + 1}</td>
                            <td className="py-3 px-4 font-medium text-champagne">{item.ten_hang || item.ten || 'N/A'}</td>
                            <td className="py-3 px-4 text-center text-muted">{item.dvt || '-'}</td>
                            <td className="py-3 px-4 text-right font-mono text-warm tabular-nums">{item.so_luong || 0}</td>
                            <td className="py-3 px-4 text-right font-mono text-warm tabular-nums">{formatVND(item.don_gia)}</td>
                            <td className="py-3 px-4 text-right font-mono font-semibold text-champagne tabular-nums">
                              {formatVND(item.thanh_tien)}
                            </td>
                            <td className="py-3 px-4 text-center font-mono text-patina font-bold">
                              {item.thue_suat ? `${item.thue_suat}%` : '0%'}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={7} className="py-8 text-center text-muted text-xs">
                            Hóa đơn dạng tóm tắt hoặc không có danh mục chi tiết
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeSubTab === 'json' && (
            <div className="double-bezel">
              <div className="double-bezel-inner p-4 bg-lacquer-deep font-mono text-[11px] text-patina overflow-x-auto max-h-96">
                <pre>{JSON.stringify(invoice, null, 2)}</pre>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
};
