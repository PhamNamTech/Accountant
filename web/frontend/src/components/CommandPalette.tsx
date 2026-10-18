import React, { useState, useEffect } from 'react';
import {
  Search,
  BookOpen,
  FileText,
  Calculator,
  Database,
  ArrowLeftRight,
  ShieldCheck,
  Code2,
  X,
  ArrowRight,
} from 'lucide-react';
import { TabId } from './Navbar';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  setActiveTab: (tab: TabId) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  setActiveTab,
}) => {
  const [query, setQuery] = useState('');

  const commands = [
    { id: 'overview', title: 'Tổng quan hệ thống', desc: 'Bento Grid, HUD số liệu và khối tương tác 3D', icon: Database, tab: 'overview' },
    { id: 'accounts-112', title: 'TK 112 - Tiền gửi không kỳ hạn', desc: 'Đổi tên theo TT 99/2025/TT-BTC', icon: BookOpen, tab: 'accounts' },
    { id: 'accounts-155', title: 'TK 155 - Sản phẩm', desc: 'Bãi bỏ tiểu khoản 1551/1557 bắt buộc theo TT 99', icon: BookOpen, tab: 'accounts' },
    { id: 'accounts-621', title: 'TK 621 - Chi phí NVL trực tiếp', desc: 'Khoản mục chi phí sản xuất trực tiếp', icon: BookOpen, tab: 'accounts' },
    { id: 'accounts-627', title: 'TK 627 - Chi phí sản xuất chung', desc: 'Phân bổ theo công suất bình thường VAS 02', icon: BookOpen, tab: 'accounts' },
    { id: 'invoices', title: 'Bóc tách hóa đơn điện tử', desc: 'Đọc file XML chuẩn TT 78 và file PDF scan', icon: FileText, tab: 'invoices' },
    { id: 'cost', title: 'Kế toán Giá thành & VAS 02', desc: 'Tính tổng giá thành Z, đơn giá z và loại trừ lãng phí vào TK 632', icon: Calculator, tab: 'cost' },
    { id: 'journal', title: 'Sổ Nhật Ký Chung (SQLite)', desc: 'Xem sổ kép, thêm bút toán mới và xuất file Excel Mẫu S03a-DN', icon: Database, tab: 'journal' },
    { id: 'reconcile', title: 'Đối soát sao kê ngân hàng', desc: 'So khớp sao kê Vietcombank với Sổ TK 112', icon: ArrowLeftRight, tab: 'reconcile' },
    { id: 'beancount', title: 'Sổ cái Plaintext Beancount', desc: 'Kiểm tra tính cân đối kép của file ledger plaintext', icon: Code2, tab: 'beancount' },
    { id: 'legal', title: 'Cơ sở Pháp lý & Ma trận quy phạm', desc: '4 nhóm mốc xét theo quy chuẩn và cảnh báo 90 ngày', icon: ShieldCheck, tab: 'legal' },
  ];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          setQuery('');
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filtered = commands.filter(
    (c) =>
      c.title.toLowerCase().includes(query.toLowerCase()) ||
      c.desc.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (tab: TabId) => {
    setActiveTab(tab);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 bg-lacquer-deep/80 backdrop-blur-md animate-fadeIn">
      <div className="double-bezel max-w-xl w-full">
        <div className="double-bezel-inner overflow-hidden shadow-2xl">
          
          {/* Input Header */}
          <div className="p-4 border-b border-hairline flex items-center gap-3 bg-raised">
            <Search className="w-4 h-4 text-kinpaku shrink-0" />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Nhập tên tính năng, mã tài khoản hoặc từ khóa tra cứu..."
              className="w-full bg-transparent text-sm text-champagne placeholder:text-muted focus:outline-none"
            />
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-muted hover:text-champagne hover:bg-graphite transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Results List */}
          <div className="max-h-80 overflow-y-auto p-2 space-y-1 bg-raised">
            {filtered.length === 0 ? (
              <div className="p-8 text-center text-muted text-xs font-mono">
                Không tìm thấy lệnh hoặc tài khoản phù hợp
              </div>
            ) : (
              filtered.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleSelect(item.tab as TabId)}
                    className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-graphite transition-colors text-left group cursor-pointer border border-transparent hover:border-hairline"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-graphite/60 border border-hairline flex items-center justify-center text-kinpaku group-hover:bg-kinpaku/15 group-hover:border-kinpaku/30 group-hover:text-kinpaku-vivid transition-colors">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-champagne group-hover:text-kinpaku transition-colors">
                          {item.title}
                        </p>
                        <p className="text-[11px] text-muted mt-0.5">{item.desc}</p>
                      </div>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-faint group-hover:translate-x-0.5 group-hover:text-kinpaku transition-all shrink-0 ml-2" />
                  </button>
                );
              })
            )}
          </div>

          {/* Footer hints */}
          <div className="p-2.5 bg-lacquer-deep border-t border-hairline flex items-center justify-between text-[10px] text-muted font-mono">
            <span>Dùng phím ↑ ↓ để duyệt</span>
            <span>ESC để đóng</span>
          </div>

        </div>
      </div>
    </div>
  );
};
