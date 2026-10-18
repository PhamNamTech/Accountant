import React, { useState } from 'react';
import {
  ArrowLeftRight,
  Upload,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  ArrowDownLeft,
  ArrowUpRight,
  Sparkles,
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface ReconcileTransaction {
  stt: number;
  ngay: string;
  ghi_no_tien_ra: number;
  ghi_co_tien_vao: number;
  so_du: number;
  noi_dung: string;
  status: 'MATCHED' | 'BANK_ONLY';
  matched_info?: any;
}

export const BankReconciliationView: React.FC = () => {
  const [data, setData] = useState<{
    file_analyzed: string;
    total_bank_transactions: number;
    matched_count: number;
    bank_only_count: number;
    ledger_only_count: number;
    total_bank_in: number;
    total_bank_out: number;
    transactions: ReconcileTransaction[];
    unmatched_ledger_transactions: any[];
  } | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUseSample = async () => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('use_sample', 'true');

      const res = await fetch('/api/reconcile', {
        method: 'POST',
        body: formData,
      });
      const resData = await res.json();
      if (!res.ok) throw new Error(resData.detail || 'Lỗi đối soát sao kê');

      setData(resData);
      // Trigger subtle celebration confetti
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('use_sample', 'false');

      const res = await fetch('/api/reconcile', {
        method: 'POST',
        body: formData,
      });
      const resData = await res.json();
      if (!res.ok) throw new Error(resData.detail || 'Lỗi đối soát sao kê');

      setData(resData);
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.6 },
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatVND = (num: number) => {
    return new Intl.NumberFormat('vi-VN').format(Math.round(num || 0)) + ' ₫';
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header Banner */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-patina/10 border border-patina/30 text-patina text-xs font-mono">
                <ArrowLeftRight className="w-3.5 h-3.5" />
                <span>Đối Soát Ngân Hàng (Bank Reconciliation)</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Đối Soát Sao Kê VCB Với Sổ TK 112</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Tự động đối chiếu từng giao dịch từ file Excel sao kê Vietcombank với các phát sinh Nợ/Có của TK 112 trong Sổ Nhật Ký Chung.
              </p>
            </div>

            {/* Quick 1-Click Sample Test */}
            <button
              onClick={handleUseSample}
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-patina hover:bg-patina-pale text-on-gold font-bold text-xs transition-all shadow-[0_0_15px_-3px_rgba(112,192,208,0.4)] active:scale-95 cursor-pointer w-fit"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Đang Xử Lý...' : 'Nạp Sao Kê VCB Mẫu (1-Click)'}</span>
            </button>
          </div>

          {/* Upload Box */}
          <div className="mt-6">
            <label className="flex items-center justify-between p-4 rounded-xl border border-dashed border-white/10 hover:border-patina/50 bg-graphite/40 hover:bg-graphite/70 transition-colors cursor-pointer">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-patina/15 border border-patina/30 flex items-center justify-center text-patina shadow-[0_0_12px_-2px_rgba(112,192,208,0.25)]">
                  <Upload className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-champagne">Hoặc tải lên file sao kê Excel (.xls / .xlsx) của doanh nghiệp</p>
                  <p className="text-[11px] text-faint">Chuẩn sao kê Vietcombank hoặc ngân hàng thương mại</p>
                </div>
              </div>
              <span className="text-xs text-patina font-medium">Chọn file...</span>
              <input type="file" accept=".xls,.xlsx" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-vermilion/15 border border-vermilion/30 text-xs text-champagne flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-vermilion shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Reconciliation Results */}
      {data && (
        <div className="space-y-6 animate-fadeIn">
          
          {/* KPI Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="double-bezel">
              <div className="double-bezel-inner p-4">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-muted">Tổng Tiền Vào (Có)</span>
                  <ArrowDownLeft className="w-4 h-4 text-patina" />
                </div>
                <p className="text-lg font-bold text-patina font-mono mt-1 tabular-nums">
                  {formatVND(data.total_bank_in)}
                </p>
              </div>
            </div>

            <div className="double-bezel">
              <div className="double-bezel-inner p-4">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-muted">Tổng Tiền Ra (Nợ)</span>
                  <ArrowUpRight className="w-4 h-4 text-kinpaku" />
                </div>
                <p className="text-lg font-bold text-kinpaku font-mono mt-1 tabular-nums">
                  {formatVND(data.total_bank_out)}
                </p>
              </div>
            </div>

            <div className="double-bezel">
              <div className="double-bezel-inner p-4">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-muted">Khớp Tuyệt Đối</span>
                  <CheckCircle2 className="w-4 h-4 text-patina" />
                </div>
                <p className="text-lg font-bold text-champagne font-mono mt-1">
                  {data.matched_count}{' '}
                  <span className="text-xs text-faint font-normal">/ {data.total_bank_transactions} GD</span>
                </p>
              </div>
            </div>

            <div className="double-bezel">
              <div className="double-bezel-inner p-4">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-muted">Chưa Ghi Sổ</span>
                  <AlertTriangle className="w-4 h-4 text-vermilion" />
                </div>
                <p className="text-lg font-bold text-vermilion font-mono mt-1">
                  {data.bank_only_count}{' '}
                  <span className="text-xs text-faint font-normal">giao dịch</span>
                </p>
              </div>
            </div>
          </div>

          {/* Transactions List */}
          <div className="double-bezel">
            <div className="double-bezel-inner overflow-hidden">
              <div className="p-4 border-b border-white/[0.08] flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-champagne">Danh Sách Giao Dịch Đối Soát</h3>
                  <p className="text-[11px] text-muted">Tệp: {data.file_analyzed}</p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-warm">
                  <thead className="bg-lacquer-deep text-[11px] uppercase tracking-wider text-faint border-b border-white/[0.08]">
                    <tr>
                      <th className="py-3 px-4 text-center font-mono">STT</th>
                      <th className="py-3 px-4 font-mono">Ngày GD</th>
                      <th className="py-3 px-4 text-right font-mono">Tiền Ra (Debit)</th>
                      <th className="py-3 px-4 text-right font-mono">Tiền Vào (Credit)</th>
                      <th className="py-3 px-4 text-right font-mono">Số Dư Sau GD</th>
                      <th className="py-3 px-4">Nội Dung Giao Dịch</th>
                      <th className="py-3 px-4 text-center">Trạng Thái</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.06]">
                    {data.transactions.map((t) => {
                      const isMatched = t.status === 'MATCHED';
                      return (
                        <tr key={t.stt} className="hover:bg-white/[0.02]">
                          <td className="py-3 px-4 text-center font-mono text-faint">{t.stt}</td>
                          <td className="py-3 px-4 font-mono text-warm">{t.ngay}</td>
                          <td className="py-3 px-4 text-right font-mono text-kinpaku tabular-nums font-semibold">
                            {t.ghi_no_tien_ra > 0 ? formatVND(t.ghi_no_tien_ra) : '-'}
                          </td>
                          <td className="py-3 px-4 text-right font-mono text-patina tabular-nums font-semibold">
                            {t.ghi_co_tien_vao > 0 ? formatVND(t.ghi_co_tien_vao) : '-'}
                          </td>
                          <td className="py-3 px-4 text-right font-mono text-muted tabular-nums">
                            {formatVND(t.so_du)}
                          </td>
                          <td className="py-3 px-4 text-champagne max-w-xs truncate" title={t.noi_dung}>
                            {t.noi_dung}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {isMatched ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-patina/15 text-patina border border-patina/30 text-[10px] font-semibold">
                                <CheckCircle2 className="w-3 h-3" />
                                Khớp 100%
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-vermilion/15 text-vermilion border border-vermilion/30 text-[10px] font-semibold">
                                <AlertTriangle className="w-3 h-3" />
                                Chưa ghi sổ
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
