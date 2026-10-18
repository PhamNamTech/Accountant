import React from 'react';
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  Calculator,
  Database,
  ArrowLeftRight,
  ShieldCheck,
  Code2,
  FileSpreadsheet,
  ChevronRight,
  ExternalLink,
  Sparkles,
  Layers,
  X,
} from 'lucide-react';
import { TabId } from './Navbar';

interface SidebarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  isOpen,
  onClose,
}) => {
  const navSections = [
    {
      title: 'TỔNG QUAN',
      items: [
        { id: 'overview', label: 'Bảng Điều Khiển', icon: LayoutDashboard, badge: 'HUD' },
      ],
    },
    {
      title: 'SỔ SÁCH & HỆ THỐNG',
      items: [
        { id: 'accounts', label: 'Hệ Thống Tài Khoản', icon: BookOpen, badge: 'TT 99' },
        { id: 'journal', label: 'Sổ Nhật Ký Chung', icon: Database, badge: 'S03a-DN' },
        { id: 'beancount', label: 'Sổ Cái Beancount', icon: Code2, badge: 'Plaintext' },
      ],
    },
    {
      title: 'GIÁ THÀNH & CHI PHÍ',
      items: [
        { id: 'cost', label: 'Kế Toán Giá Thành', icon: Calculator, badge: 'VAS 02' },
      ],
    },
    {
      title: 'CHỨNG TỪ & ĐỐI SOÁT',
      items: [
        { id: 'invoices', label: 'Bóc Tách Hóa Đơn', icon: FileText, badge: 'XML/PDF' },
        { id: 'reconcile', label: 'Đối Soát Sao Kê', icon: ArrowLeftRight, badge: 'VCB' },
      ],
    },
    {
      title: 'QUY CHUẨN PHÁP LÝ',
      items: [
        { id: 'legal', label: 'Căn Cứ Pháp Lý', icon: ShieldCheck, badge: 'Cấp 1' },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm lg:hidden animate-fadeIn"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-raised border-r border-white/[0.08] flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Sidebar Header */}
        <div>
          <div className="h-16 px-5 border-b border-white/[0.08] flex items-center justify-between">
            <div className="flex items-center gap-3 select-none">
              <div className="w-8 h-8 rounded-lg bg-kinpaku/15 border border-kinpaku/35 flex items-center justify-center text-kinpaku shadow-[0_0_15px_-3px_rgba(245,196,81,0.3)]">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <span className="font-extrabold text-sm tracking-tight text-champagne font-mono">
                  KETOAN<span className="text-kinpaku">·VN</span>
                </span>
                <span className="block text-[10px] text-muted font-mono">
                  Enterprise Suite v2.0
                </span>
              </div>
            </div>

            {/* Close button on mobile */}
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-muted hover:text-champagne lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Sections */}
          <div className="p-3 space-y-6 overflow-y-auto max-h-[calc(100vh-140px)] scrollbar-none">
            {navSections.map((section, sIdx) => (
              <div key={sIdx} className="space-y-1">
                <p className="px-3 text-[10px] font-mono font-bold tracking-wider text-faint uppercase">
                  {section.title}
                </p>

                <div className="space-y-0.5 pt-1">
                  {section.items.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    return (
                      <button
                        key={item.id}
                        onClick={() => {
                          setActiveTab(item.id as TabId);
                          onClose();
                        }}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer group text-left ${
                          isActive
                            ? 'bg-kinpaku/10 text-champagne border border-kinpaku/35 font-semibold shadow-[inset_0_1px_0_rgba(245,196,81,0.25)]'
                            : 'text-warm hover:text-champagne hover:bg-white/[0.04] border border-transparent'
                        }`}
                      >
                        <div className="flex items-center gap-2.5">
                          <Icon
                            className={`w-4 h-4 shrink-0 transition-colors ${
                              isActive ? 'text-kinpaku' : 'text-muted group-hover:text-champagne'
                            }`}
                          />
                          <span>{item.label}</span>
                        </div>

                        <span
                          className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${
                            isActive
                              ? 'bg-kinpaku/20 text-kinpaku border-kinpaku/40 font-bold'
                              : 'bg-white/[0.05] text-muted border-white/[0.06]'
                          }`}
                        >
                          {item.badge}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Footer: System Status */}
        <div className="p-4 border-t border-white/[0.08] bg-lacquer-deep">
          <div className="flex items-center justify-between text-[11px] font-mono text-muted mb-2">
            <span className="flex items-center gap-1.5 text-patina font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-patina animate-pulse shadow-[0_0_8px_rgba(112,192,208,0.8)]" />
              SQLite WAL Active
            </span>
            <span className="text-faint">TT 99/2025</span>
          </div>

          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-graphite hover:bg-graphite-2 text-xs text-warm hover:text-champagne border border-white/[0.08] transition-colors"
          >
            <span>Swagger API Docs</span>
            <ExternalLink className="w-3.5 h-3.5 text-muted" />
          </a>
        </div>
      </aside>
    </>
  );
};
