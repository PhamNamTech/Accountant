import React from 'react';
import {
  Layers,
  BookOpen,
  FileText,
  Calculator,
  Database,
  ArrowLeftRight,
  ShieldCheck,
  Search,
  Code2,
  Sparkles,
  ChevronRight,
} from 'lucide-react';

export type TabId =
  | 'overview'
  | 'accounts'
  | 'invoices'
  | 'cost'
  | 'journal'
  | 'reconcile'
  | 'beancount'
  | 'legal';

interface NavbarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  onOpenSearch: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenSearch,
}) => {
  const tabs = [
    { id: 'overview', label: 'Tổng quan', icon: Layers, badge: 'HUD' },
    { id: 'accounts', label: 'Tra cứu TK', icon: BookOpen, badge: 'TT99' },
    { id: 'invoices', label: 'Bóc tách Hóa đơn', icon: FileText, badge: 'XML/PDF' },
    { id: 'cost', label: 'Giá thành & VAS 02', icon: Calculator, badge: 'Z, z' },
    { id: 'journal', label: 'Sổ Nhật ký', icon: Database, badge: 'S03a' },
    { id: 'reconcile', label: 'Đối soát VCB', icon: ArrowLeftRight, badge: 'TK 112' },
    { id: 'beancount', label: 'Sổ Beancount', icon: Code2, badge: 'Plaintext' },
    { id: 'legal', label: 'Cơ sở Pháp lý', icon: ShieldCheck, badge: 'Cấp 1' },
  ] as const;

  const currentTabObj = tabs.find((t) => t.id === activeTab);

  return (
    <header className="sticky top-2 z-50 px-3 sm:px-6 max-w-7xl mx-auto w-full transition-all duration-300">
      <div className="double-bezel shadow-2xl backdrop-blur-2xl">
        <div className="double-bezel-inner px-3 sm:px-5 py-2.5 flex items-center justify-between gap-3 flex-wrap">
          
          {/* Logo & Brand Identity */}
          <div
            onClick={() => setActiveTab('overview')}
            className="flex items-center gap-3 cursor-pointer group select-none transition-transform active:scale-95"
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter') setActiveTab('overview'); }}
            title="Quay về màn hình Tổng quan"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 via-cyan-500/20 to-indigo-500/10 border border-emerald-500/30 flex items-center justify-center shadow-inner group-hover:scale-105 transition-transform duration-200">
              <Sparkles className="w-4 h-4 text-emerald-400 group-hover:rotate-12 transition-transform duration-200" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-sm tracking-tight text-white font-display">
                  KETOAN<span className="text-emerald-400">·VN</span>
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 font-mono font-semibold">
                  TT 99/2025
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block tracking-wide">
                Vietnam Accounting AI Suite
              </p>
            </div>
          </div>

          {/* Navigation Items (Segmented Pill Selector) */}
          <nav className="flex items-center gap-1 overflow-x-auto py-1 scrollbar-none max-w-full">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabId)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all duration-150 whitespace-nowrap cursor-pointer active:scale-95 ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/35 shadow-[0_0_12px_-2px_rgba(16,185,129,0.3)] font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.05] border border-transparent'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Action: Search / Command Palette & Status Indicator */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenSearch}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 border border-white/[0.08] transition-colors cursor-pointer active:scale-95"
              title="Tìm kiếm nhanh toàn bộ hệ thống (Ctrl+K)"
            >
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <span className="hidden md:inline text-[11px] text-slate-400">Tìm kiếm</span>
              <kbd className="hidden sm:inline-block text-[10px] bg-white/10 text-slate-300 px-1.5 py-0.5 rounded border border-white/10 font-mono">
                ⌘K
              </kbd>
            </button>

            {/* Live Indicator */}
            <div className="hidden xl:flex items-center gap-2 pl-2 border-l border-white/[0.08]">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[11px] text-emerald-400/90 font-mono">LIVE API</span>
            </div>
          </div>

        </div>
      </div>

      {/* Mini Breadcrumb Bar */}
      <div className="mt-2 px-3 flex items-center justify-between text-[11px] text-slate-400 font-mono">
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400">Hệ Thống</span>
          <ChevronRight className="w-3 h-3 text-slate-400" />
          <span className="text-white font-medium">{currentTabObj?.label}</span>
          <span className="px-1.5 py-0.2 rounded bg-white/[0.05] text-[10px] text-emerald-400 border border-white/[0.08]">
            {currentTabObj?.badge}
          </span>
        </div>
        <div className="hidden md:flex items-center gap-2 text-[10px] text-slate-400">
          <span>Chuẩn mực: VAS 02 · TT 99/2025 · NĐ 123</span>
        </div>
      </div>
    </header>
  );
};
