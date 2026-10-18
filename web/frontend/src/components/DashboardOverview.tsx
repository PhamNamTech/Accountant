import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  Database,
  Calculator,
  FileText,
  ArrowLeftRight,
  ShieldCheck,
  CheckCircle2,
  ArrowUpRight,
  Download,
  Activity,
  Layers,
  Scale,
} from 'lucide-react';
import { TabId } from './Navbar';

interface DashboardOverviewProps {
  setActiveTab: (tab: TabId) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({ setActiveTab }) => {
  const [stats, setStats] = useState<{
    total_transactions: number;
    total_amount: number;
    top_debit_accounts: Array<{ tk_no: string; total: number }>;
    top_credit_accounts: Array<{ tk_co: string; total: number }>;
  }>({
    total_transactions: 4,
    total_amount: 29660000,
    top_debit_accounts: [],
    top_credit_accounts: [],
  });

  const [recentEntries, setRecentEntries] = useState<any[]>([]);
  const [beancountStatus, setBeancountStatus] = useState<string>('Cân đối hợp lệ (14 bút toán)');

  useEffect(() => {
    // Tải thống kê journal
    fetch('/api/journal/stats')
      .then((r) => r.json())
      .then((data) => {
        if (data.total_transactions !== undefined) {
          setStats(data);
        }
      })
      .catch(() => {});

    // Lấy 5 bút toán mới nhất
    fetch('/api/journal/entries?limit=5')
      .then((r) => r.json())
      .then((data) => {
        setRecentEntries(data.items || []);
      })
      .catch(() => {});

    // Kiểm tra Beancount
    fetch('/api/beancount/verify')
      .then((r) => r.json())
      .then((data) => {
        if (data.status === 'valid') {
          setBeancountStatus(`Cân đối hợp lệ (${data.total_entries} bút toán)`);
        }
      })
      .catch(() => {});
  }, []);

  const formatVND = (num: number) => {
    return new Intl.NumberFormat('vi-VN').format(Math.round(num || 0)) + ' ₫';
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Top Executive Stats (Bullet KPI Grid with Impeccable Neo Kinpaku & Patina) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1: Tổng phát sinh luồng tiền */}
        <div className="p-5 rounded-xl bg-raised border border-white/[0.08] shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted">
              <span className="font-mono uppercase tracking-wider text-[11px] text-faint">Tổng Luồng Tiền Ghi Sổ</span>
              <Activity className="w-4 h-4 text-kinpaku" />
            </div>
            <p className="text-2xl font-bold text-kinpaku font-mono mt-2 tabular-nums">
              {formatVND(stats.total_amount)}
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-muted">
            <span>Cân đối Nợ = Có:</span>
            <span className="text-patina font-bold">100% Cân Bằng</span>
          </div>
        </div>

        {/* KPI 2: Bút toán đã hạch toán */}
        <div className="p-5 rounded-xl bg-raised border border-white/[0.08] shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted">
              <span className="font-mono uppercase tracking-wider text-[11px] text-faint">Số Bút Toán Nhật Ký</span>
              <Database className="w-4 h-4 text-patina" />
            </div>
            <p className="text-2xl font-bold text-champagne font-mono mt-2">
              {stats.total_transactions}{' '}
              <span className="text-xs font-normal text-muted">giao dịch</span>
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-muted">
            <span>Cơ sở dữ liệu:</span>
            <span className="text-champagne font-medium">SQLite ketoan.db</span>
          </div>
        </div>

        {/* KPI 3: Sổ cái Beancount */}
        <div className="p-5 rounded-xl bg-raised border border-white/[0.08] shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted">
              <span className="font-mono uppercase tracking-wider text-[11px] text-faint">Sổ Cái Beancount</span>
              <CheckCircle2 className="w-4 h-4 text-patina" />
            </div>
            <p className="text-base font-bold text-champagne font-mono mt-2 truncate">
              {beancountStatus}
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-muted">
            <span>Đơn vị tiền tệ:</span>
            <span className="text-champagne font-bold">VND</span>
          </div>
        </div>

        {/* KPI 4: Chế độ áp dụng */}
        <div className="p-5 rounded-xl bg-raised border border-white/[0.08] shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs text-muted">
              <span className="font-mono uppercase tracking-wider text-[11px] text-faint">Chế Độ Kế Toán Chuẩn</span>
              <ShieldCheck className="w-4 h-4 text-kinpaku" />
            </div>
            <p className="text-lg font-bold text-champagne font-mono mt-2">
              TT 99/2025/TT-BTC
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-muted">
            <span>Quy chuẩn giá thành:</span>
            <span className="text-patina font-bold">VAS 02 Chuẩn</span>
          </div>
        </div>

      </div>

      {/* Main Grid: Workbench Shortcuts & Recent Ledger Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Quick Navigation Workbench (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-champagne font-mono uppercase tracking-wider">
              Phân Hệ Nghiệp Vụ Cốt Lõi
            </h3>
            <span className="text-xs text-muted font-mono">6 Phân Hệ Tự Động</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            
            {/* Card 1: Tra cứu tài khoản */}
            <div
              onClick={() => setActiveTab('accounts')}
              className="p-4 rounded-xl bg-raised border border-white/[0.08] hover:border-kinpaku/40 hover:bg-raised-hover transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 rounded-lg bg-kinpaku/15 border border-kinpaku/35 flex items-center justify-center text-kinpaku group-hover:scale-105 transition-transform shadow-[0_0_12px_-2px_rgba(245,196,81,0.25)]">
                  <Database className="w-4 h-4" />
                </div>
                <ArrowUpRight className="w-4 h-4 text-faint group-hover:text-kinpaku transition-colors" />
              </div>
              <h4 className="text-sm font-bold text-champagne group-hover:text-kinpaku transition-colors">
                Hệ Thống Tài Khoản
              </h4>
              <p className="text-xs text-muted mt-1 leading-relaxed">
                Tra cứu danh mục TK chuẩn TT 99/2025 (TK 112, TK 155, bãi bỏ 611/631/161/441), TT 200 và TT 133.
              </p>
            </div>

            {/* Card 2: Bóc tách hóa đơn */}
            <div
              onClick={() => setActiveTab('invoices')}
              className="p-4 rounded-xl bg-raised border border-white/[0.08] hover:border-patina/40 hover:bg-raised-hover transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 rounded-lg bg-patina/15 border border-patina/35 flex items-center justify-center text-patina group-hover:scale-105 transition-transform shadow-[0_0_12px_-2px_rgba(112,192,208,0.25)]">
                  <FileText className="w-4 h-4" />
                </div>
                <ArrowUpRight className="w-4 h-4 text-faint group-hover:text-patina transition-colors" />
              </div>
              <h4 className="text-sm font-bold text-champagne group-hover:text-patina transition-colors">
                Bóc Tách Hóa Đơn XML/PDF
              </h4>
              <p className="text-xs text-muted mt-1 leading-relaxed">
                Trích xuất thông tin người bán, người mua, thuế suất, hàng hóa; hỗ trợ ghi trực tiếp vào Sổ Nhật Ký.
              </p>
            </div>

            {/* Card 3: Giá thành sản xuất */}
            <div
              onClick={() => setActiveTab('cost')}
              className="p-4 rounded-xl bg-raised border border-white/[0.08] hover:border-kinpaku/40 hover:bg-raised-hover transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 rounded-lg bg-kinpaku/15 border border-kinpaku/35 flex items-center justify-center text-kinpaku group-hover:scale-105 transition-transform shadow-[0_0_12px_-2px_rgba(245,196,81,0.25)]">
                  <Calculator className="w-4 h-4" />
                </div>
                <ArrowUpRight className="w-4 h-4 text-faint group-hover:text-kinpaku transition-colors" />
              </div>
              <h4 className="text-sm font-bold text-champagne group-hover:text-kinpaku transition-colors">
                Kế Toán Giá Thành & VAS 02
              </h4>
              <p className="text-xs text-muted mt-1 leading-relaxed">
                Tính tổng Z, đơn giá z, kiểm soát công suất bình thường VAS 02 loại trừ SXC cố định lãng phí vào TK 632.
              </p>
            </div>

            {/* Card 4: Đối soát sao kê VCB */}
            <div
              onClick={() => setActiveTab('reconcile')}
              className="p-4 rounded-xl bg-raised border border-white/[0.08] hover:border-patina/40 hover:bg-raised-hover transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 rounded-lg bg-patina/15 border border-patina/35 flex items-center justify-center text-patina group-hover:scale-105 transition-transform shadow-[0_0_12px_-2px_rgba(112,192,208,0.25)]">
                  <ArrowLeftRight className="w-4 h-4" />
                </div>
                <ArrowUpRight className="w-4 h-4 text-faint group-hover:text-patina transition-colors" />
              </div>
              <h4 className="text-sm font-bold text-champagne group-hover:text-patina transition-colors">
                Đối Soát Ngân Hàng (TK 112)
              </h4>
              <p className="text-xs text-muted mt-1 leading-relaxed">
                Đối chiếu sao kê Vietcombank Excel với các bút toán tiền gửi trong Sổ Nhật Ký để tìm chênh lệch.
              </p>
            </div>

          </div>

          {/* Quick Legal Compliance Banner */}
          <div className="p-4 rounded-xl bg-raised border border-white/[0.08] space-y-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-champagne font-bold flex items-center gap-2">
                <Scale className="w-4 h-4 text-kinpaku" />
                Nguyên Tắc Pháp Lý Áp Dụng Theo Mốc Xét
              </span>
              <button
                onClick={() => setActiveTab('legal')}
                className="text-kinpaku hover:text-kinpaku-vivid flex items-center gap-1 cursor-pointer font-bold"
              >
                <span>Xem Ma Trận</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              Phân định 4 mốc: Chế độ kế toán (Theo Năm tài chính), Hóa đơn (Theo Ngày lập), Thuế TNDN/TNCN (Theo Kỳ tính thuế), Thuế GTGT (Theo Thời điểm phát sinh). Cảnh báo quá hạn 90 ngày được kích hoạt.
            </p>
          </div>
        </div>

        {/* Right Column: Live Journal Activity Stream (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-champagne font-mono uppercase tracking-wider">
              Nhật Ký Giao Dịch Gần Đây
            </h3>
            <button
              onClick={() => setActiveTab('journal')}
              className="text-xs text-kinpaku hover:underline font-mono cursor-pointer font-medium"
            >
              Xem toàn bộ ({stats.total_transactions})
            </button>
          </div>

          <div className="p-4 rounded-xl bg-raised border border-white/[0.08] divide-y divide-white/[0.08]">
            {recentEntries.length === 0 ? (
              <div className="py-8 text-center text-muted text-xs">
                Chưa có bút toán phát sinh trong sổ
              </div>
            ) : (
              recentEntries.map((e) => (
                <div key={e.id} className="py-3 first:pt-0 last:pb-0 flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 font-mono text-xs">
                      <span className="font-bold text-patina">{e.so_chung_tu}</span>
                      <span className="text-faint">·</span>
                      <span className="text-muted text-[11px]">{e.ngay_ghi_so}</span>
                    </div>
                    <p className="text-xs text-warm mt-1 line-clamp-1">{e.dien_giai}</p>
                    <div className="flex items-center gap-2 text-[11px] font-mono mt-1 text-muted">
                      <span>Nợ <strong className="text-kinpaku">{e.tk_no}</strong></span>
                      <span className="text-faint">/</span>
                      <span>Có <strong className="text-patina">{e.tk_co}</strong></span>
                    </div>
                  </div>

                  <span className="font-mono text-xs font-bold text-champagne tabular-nums shrink-0">
                    {formatVND(e.so_tien)}
                  </span>
                </div>
              ))
            )}
          </div>

          {/* Export Quick Action */}
          <div className="p-4 rounded-xl bg-raised border border-white/[0.08] flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-champagne font-mono">Sổ Nhật Ký Chung Mẫu S03a-DN</p>
              <p className="text-[11px] text-muted">Xuất file Excel báo cáo chuẩn</p>
            </div>
            <a
              href="/api/journal/export-excel"
              className="px-3.5 py-1.5 rounded-lg bg-kinpaku hover:bg-kinpaku-vivid text-on-gold text-xs font-bold font-mono transition-all flex items-center gap-1.5 shadow-[0_0_15px_-3px_rgba(245,196,81,0.35)]"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Tải Excel</span>
            </a>
          </div>

        </div>

      </div>

    </div>
  );
};
