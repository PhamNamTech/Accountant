import React, { useEffect, useState } from 'react';
import {
  FileText,
  Calculator,
  Database,
  ArrowLeftRight,
  ShieldCheck,
  Code2,
  TrendingUp,
  CheckCircle2,
  ExternalLink,
  Sparkles,
  ArrowUpRight,
  Download,
} from 'lucide-react';
import { ThreeCanvas } from './ThreeCanvas';
import { TabId } from './Navbar';

interface BentoDashboardProps {
  setActiveTab: (tab: TabId) => void;
}

export const BentoDashboard: React.FC<BentoDashboardProps> = ({ setActiveTab }) => {
  const [stats, setStats] = useState<{
    total_transactions: number;
    total_amount: number;
  }>({
    total_transactions: 4,
    total_amount: 29660000,
  });

  const [beancountStatus, setBeancountStatus] = useState<string>('Đã kiểm tra cân đối');

  useEffect(() => {
    // Tải thống kê thực từ SQLite API
    fetch('/api/journal/stats')
      .then((r) => r.json())
      .then((data) => {
        if (data.total_transactions !== undefined) {
          setStats({
            total_transactions: data.total_transactions,
            total_amount: data.total_amount,
          });
        }
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
    return new Intl.NumberFormat('vi-VN').format(num) + ' ₫';
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Hero Section with Antigravity 3D Canvas */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6 sm:p-10 relative overflow-hidden">
          {/* Subtle Ambient Radial Glow */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
            {/* Left Column: Brand & Copy */}
            <div className="lg:col-span-7 space-y-5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-[11px] font-mono tracking-wider uppercase">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Hệ Thống Chuẩn Kế Toán Việt Nam · TT 99/2025/TT-BTC
              </div>

              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-[1.15]">
                Trợ Lý Kế Toán AI &{' '}
                <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                  Quản Trị Giá Thành
                </span>
              </h1>

              <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl font-light">
                Tự động hóa toàn diện quy trình hạch toán: Bóc tách hóa đơn điện tử XML/PDF, tính giá thành theo chuẩn VAS 02 kiểm soát công suất bình thường, ghi sổ kế toán kép SQLite và đối soát tự động sao kê ngân hàng TK 112.
              </p>

              {/* Action Buttons (Button-in-Button Architecture) */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  onClick={() => setActiveTab('cost')}
                  className="group relative inline-flex items-center gap-3 px-5 py-3 rounded-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs sm:text-sm transition-all duration-300 shadow-[0_0_25px_-5px_rgba(16,185,129,0.5)] active:scale-95 cursor-pointer"
                >
                  <span>Tính Giá Thành VAS 02</span>
                  <div className="w-6 h-6 rounded-full bg-slate-950/20 flex items-center justify-center group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-300">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </div>
                </button>

                <button
                  onClick={() => setActiveTab('invoices')}
                  className="group inline-flex items-center gap-3 px-5 py-3 rounded-full bg-white/[0.05] hover:bg-white/[0.1] text-white border border-white/10 font-medium text-xs sm:text-sm transition-all duration-300 active:scale-95 cursor-pointer"
                >
                  <span>Bóc Tách Hóa Đơn XML/PDF</span>
                  <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-300">
                    <ArrowUpRight className="w-3.5 h-3.5 text-slate-300" />
                  </div>
                </button>

                <a
                  href="/api/journal/export-excel"
                  className="inline-flex items-center gap-2 px-4 py-3 rounded-full bg-white/[0.03] hover:bg-white/[0.06] text-slate-300 border border-white/[0.08] text-xs font-mono transition-colors"
                  title="Xuất file Sổ Nhật Ký Chung Mẫu S03a-DN"
                >
                  <Download className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Sổ S03a-DN Excel</span>
                </a>
              </div>

              {/* Quick Metrics Bar */}
              <div className="pt-4 grid grid-cols-3 gap-3 border-t border-white/[0.08]">
                <div>
                  <p className="text-[11px] text-slate-400 font-medium">Bút toán ghi sổ</p>
                  <p className="text-lg font-bold text-white font-mono">{stats.total_transactions} bút toán</p>
                </div>
                <div>
                  <p className="text-[11px] text-slate-400 font-medium">Tổng phát sinh Nợ/Có</p>
                  <p className="text-lg font-bold text-emerald-400 font-mono tabular-nums">
                    {formatVND(stats.total_amount)}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] text-slate-400 font-medium">Sổ cái Beancount</p>
                  <div className="flex items-center gap-1.5 text-emerald-300 text-xs font-medium pt-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="truncate">{beancountStatus}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Three.js 3D Antigravity Floating Visualization */}
            <div className="lg:col-span-5 relative h-80 sm:h-96 w-full rounded-2xl overflow-hidden bg-gradient-to-b from-white/[0.02] to-transparent border border-white/[0.06]">
              <ThreeCanvas />

              {/* Floating Accounting Chips (Antigravity HUD overlays) */}
              <div className="absolute top-4 left-4 animate-antigravity pointer-events-none">
                <div className="px-2.5 py-1 rounded-lg bg-slate-900/80 backdrop-blur-md border border-emerald-500/30 text-[10px] font-mono text-emerald-300 shadow-lg">
                  TK 112 · Tiền gửi không kỳ hạn
                </div>
              </div>

              <div className="absolute bottom-6 left-6 animate-antigravity-slow pointer-events-none">
                <div className="px-2.5 py-1 rounded-lg bg-slate-900/80 backdrop-blur-md border border-cyan-500/30 text-[10px] font-mono text-cyan-300 shadow-lg">
                  TK 155 · Sản phẩm (TT 99)
                </div>
              </div>

              <div className="absolute top-10 right-4 animate-antigravity pointer-events-none">
                <div className="px-2.5 py-1 rounded-lg bg-slate-900/80 backdrop-blur-md border border-indigo-500/30 text-[10px] font-mono text-indigo-300 shadow-lg">
                  TK 621 · Chi phí NVL TT
                </div>
              </div>

              <div className="absolute bottom-16 right-4 animate-antigravity-slow pointer-events-none">
                <div className="px-2.5 py-1 rounded-lg bg-slate-900/80 backdrop-blur-md border border-teal-500/30 text-[10px] font-mono text-teal-300 shadow-lg">
                  TK 627 · Phân bổ SXC (VAS 02)
                </div>
              </div>

              <div className="absolute bottom-2 right-2 text-[9px] font-mono text-slate-500 pointer-events-none">
                3D WebGL ThreeUI Physics
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bento Grid: 6 Core Modules Architecture */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Tính Năng Cốt Lõi Dự Án</h2>
            <p className="text-xs text-slate-400">Các hành động kế toán tự động hóa hiện có trong hệ thống</p>
          </div>
          <span className="text-xs font-mono text-emerald-400/80 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
            6 Modules Sẵn Sàng
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          
          {/* Card 1: Tra cứu Danh mục Tài khoản (TT99 / TT200 / TT133) */}
          <div
            onClick={() => setActiveTab('accounts')}
            className="group double-bezel hover:scale-[1.01] transition-all duration-300 cursor-pointer"
          >
            <div className="double-bezel-inner p-5 h-full flex flex-col justify-between hover:border-emerald-500/30 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
                    <Database className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.05] text-slate-300 border border-white/[0.08]">
                    TT 99 / 200 / 133
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                  Tra Cứu Hệ Thống Tài Khoản
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Tra cứu theo mã số hoặc từ khóa; phân biệt rõ TK 112 "Tiền gửi không kỳ hạn", TK 155 "Sản phẩm", và danh mục tài khoản bãi bỏ (611, 631, 161, 441).
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-emerald-400 font-medium">
                <span>Khám phá danh mục</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </div>
          </div>

          {/* Card 2: Bóc Tách Hóa Đơn Điện Tử XML / PDF */}
          <div
            onClick={() => setActiveTab('invoices')}
            className="group double-bezel hover:scale-[1.01] transition-all duration-300 cursor-pointer"
          >
            <div className="double-bezel-inner p-5 h-full flex flex-col justify-between hover:border-cyan-500/30 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-500/20 transition-colors">
                    <FileText className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                    TT 78 / NĐ 123
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors">
                  Bóc Tách Hóa Đơn XML & PDF
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Tự động trích xuất MST người bán/mua, số HĐ, ký hiệu, chi tiết từng dòng hàng hóa và tiền thuế GTGT. Có sẵn hóa đơn mẫu để test ngay chỉ với 1 click.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-cyan-400 font-medium">
                <span>Tải lên hóa đơn</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </div>
          </div>

          {/* Card 3: Kế Toán Giá Thành & VAS 02 */}
          <div
            onClick={() => setActiveTab('cost')}
            className="group double-bezel hover:scale-[1.01] transition-all duration-300 cursor-pointer"
          >
            <div className="double-bezel-inner p-5 h-full flex flex-col justify-between hover:border-emerald-500/30 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
                    <Calculator className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    VAS 02 Chuẩn Mực
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                  Tính Giá Thành & VAS 02
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Tính tổng giá thành Z, đơn giá z, phân bổ chi phí SXC theo công suất định mức; tự động loại trừ chi phí lãng phí dưới công suất đưa vào TK 632 và xuất file Excel.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-emerald-400 font-medium">
                <span>Tính toán giá thành</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </div>
          </div>

          {/* Card 4: Sổ Nhật Ký Chung (SQLite) */}
          <div
            onClick={() => setActiveTab('journal')}
            className="group double-bezel hover:scale-[1.01] transition-all duration-300 cursor-pointer"
          >
            <div className="double-bezel-inner p-5 h-full flex flex-col justify-between hover:border-indigo-500/30 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/25 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500/20 transition-colors">
                    <TrendingUp className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    Mẫu S03a-DN
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-indigo-300 transition-colors">
                  Sổ Nhật Ký Chung & SQLite
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Cơ sở dữ liệu SQLite lưu trữ bút toán sổ kép, kiểm tra cân đối Nợ = Có tuyệt đối, bộ lọc tìm kiếm theo tài khoản và xuất Sổ Nhật Ký Chung Excel.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-indigo-400 font-medium">
                <span>Xem sổ Nhật ký</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </div>
          </div>

          {/* Card 5: Đối Soát Sao Kê Ngân Hàng (TK 112) */}
          <div
            onClick={() => setActiveTab('reconcile')}
            className="group double-bezel hover:scale-[1.01] transition-all duration-300 cursor-pointer"
          >
            <div className="double-bezel-inner p-5 h-full flex flex-col justify-between hover:border-amber-500/30 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/25 flex items-center justify-center text-amber-400 group-hover:bg-amber-500/20 transition-colors">
                    <ArrowLeftRight className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                    Vietcombank
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-amber-300 transition-colors">
                  Đối Soát Ngân Hàng (TK 112)
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Quét file sao kê Excel Vietcombank, tự động đối chiếu số tiền và ngày giao dịch với các bút toán TK 112 trong sổ kế toán để phát hiện sai lệch dòng tiền.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-amber-400 font-medium">
                <span>Thực hiện đối soát</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </div>
          </div>

          {/* Card 6: Sổ Cái Beancount Plaintext & Pháp Lý */}
          <div
            onClick={() => setActiveTab('legal')}
            className="group double-bezel hover:scale-[1.01] transition-all duration-300 cursor-pointer"
          >
            <div className="double-bezel-inner p-5 h-full flex flex-col justify-between hover:border-violet-500/30 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center text-violet-400 group-hover:bg-violet-500/20 transition-colors">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">
                    Pháp Lý Cấp 1
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-violet-300 transition-colors">
                  Cơ Sở Pháp Lý & Ma Trận Hiệu Lực
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Hệ thống 4 mốc xét quy phạm pháp luật (Chế độ kế toán, Hóa đơn chứng từ, Thuế TNDN/TNCN, Thuế GTGT) cùng quy tắc cảnh báo quá hạn 90 ngày.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs text-violet-400 font-medium">
                <span>Xem ma trận pháp lý</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};
