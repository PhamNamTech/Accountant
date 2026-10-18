import React from 'react';
import {
  Menu,
  Search,
  Download,
  ChevronRight,
  ShieldCheck,
  FileSpreadsheet,
} from 'lucide-react';
import { TabId } from './Navbar';

interface TopHeaderProps {
  activeTab: TabId;
  onOpenSidebar: () => void;
  onOpenSearch: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  activeTab,
  onOpenSidebar,
  onOpenSearch,
}) => {
  const titles: Record<TabId, { title: string; category: string }> = {
    overview: { title: 'Bảng Điều Khiển Tổng Quan', category: 'Tổng Quan' },
    accounts: { title: 'Tra Cứu Danh Mục Tài Khoản', category: 'Sổ Sách & Hệ Thống' },
    journal: { title: 'Sổ Nhật Ký Chung (Mẫu S03a-DN)', category: 'Sổ Sách & Hệ Thống' },
    beancount: { title: 'Sổ Cái Kế Toán Plaintext Beancount', category: 'Sổ Sách & Hệ Thống' },
    cost: { title: 'Kế Toán Giá Thành & Chuẩn Mực VAS 02', category: 'Giá Thành & Chi Phí' },
    invoices: { title: 'Bóc Tách Hóa Đơn Điện Tử XML/PDF', category: 'Chứng Từ & Đối Soát' },
    reconcile: { title: 'Đối Soát Sao Kê Ngân Hàng (TK 112)', category: 'Chứng Từ & Đối Soát' },
    legal: { title: 'Căn Cứ Pháp Lý & Ma Trận Quy Phạm', category: 'Quy Chuẩn Pháp Lý' },
  };

  const current = titles[activeTab] || titles.overview;

  return (
    <header className="h-16 px-4 sm:px-8 border-b border-white/[0.08] bg-raised/90 backdrop-blur-md flex items-center justify-between sticky top-0 z-30">
      
      {/* Left: Mobile Menu Trigger & Breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSidebar}
          className="p-2 rounded-lg text-muted hover:text-champagne hover:bg-white/[0.05] lg:hidden"
          title="Mở menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-faint hidden sm:inline">{current.category}</span>
          <ChevronRight className="w-3.5 h-3.5 text-faint hidden sm:inline" />
          <span className="text-champagne font-bold tracking-tight text-sm sm:text-base">
            {current.title}
          </span>
        </div>
      </div>

      {/* Right: Quick Search & Export Actions */}
      <div className="flex items-center gap-2 sm:gap-3">
        
        {/* Global Search Button */}
        <button
          onClick={onOpenSearch}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-graphite hover:bg-graphite-2 text-warm border border-white/[0.08] text-xs transition-colors cursor-pointer"
        >
          <Search className="w-3.5 h-3.5 text-muted" />
          <span className="hidden md:inline text-[11px] text-muted">Tìm kiếm nhanh</span>
          <kbd className="text-[10px] bg-lacquer-deep text-champagne px-1.5 py-0.5 rounded border border-white/[0.1] font-mono">
            ⌘K
          </kbd>
        </button>

        {/* Quick Excel Export */}
        <a
          href="/api/journal/export-excel"
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-graphite hover:bg-graphite-2 text-warm border border-white/[0.08] text-xs font-mono transition-colors"
          title="Xuất file Sổ Nhật Ký Chung Excel (S03a-DN)"
        >
          <FileSpreadsheet className="w-3.5 h-3.5 text-kinpaku" />
          <span>Sổ S03a-DN</span>
        </a>

        {/* Legal Regime Badge */}
        <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-kinpaku/10 border border-kinpaku/30 text-kinpaku text-xs font-mono font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>TT 99/2025</span>
        </div>

      </div>

    </header>
  );
};
