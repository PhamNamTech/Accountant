import React, { useState, useEffect } from 'react';
import {
  Search,
  BookOpen,
  Copy,
  Check,
  AlertTriangle,
  Info,
  Filter,
  Layers,
} from 'lucide-react';

interface AccountInfo {
  code: string;
  name: string;
  type: string;
  regime: string;
  status?: string;
  note?: string;
}

export const AccountLookup: React.FC = () => {
  const [query, setQuery] = useState('');
  const [regime, setRegime] = useState<'TT99' | 'TT200' | 'TT133'>('TT99');
  const [accounts, setAccounts] = useState<AccountInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const fetchAccounts = async (q: string, reg: string) => {
    setLoading(true);
    try {
      if (q.trim()) {
        const res = await fetch(`/api/accounts?query=${encodeURIComponent(q)}&regime=${reg}`);
        const data = await res.json();
        const list: AccountInfo[] = Object.entries(data.results || {}).map(([code, info]: [string, any]) => ({
          code,
          ...info,
        }));
        setAccounts(list);
      } else {
        const res = await fetch(`/api/accounts/all?regime=${reg}`);
        const data = await res.json();
        setAccounts(data.accounts || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts(query, regime);
  }, [query, regime]);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 1500);
  };

  const filteredAccounts = accounts.filter((acc) => {
    if (categoryFilter === 'all') return true;
    if (categoryFilter === 'money') return acc.code.startsWith('111') || acc.code.startsWith('112');
    if (categoryFilter === 'inventory') return acc.code.startsWith('151') || acc.code.startsWith('152') || acc.code.startsWith('153') || acc.code.startsWith('154') || acc.code.startsWith('155') || acc.code.startsWith('156');
    if (categoryFilter === 'cost') return acc.code.startsWith('621') || acc.code.startsWith('622') || acc.code.startsWith('623') || acc.code.startsWith('627') || acc.code.startsWith('632') || acc.code.startsWith('154');
    if (categoryFilter === 'liabilities') return acc.code.startsWith('331') || acc.code.startsWith('333') || acc.code.startsWith('334') || acc.code.startsWith('338');
    if (categoryFilter === 'deprecated') return acc.status === 'Bãi bỏ';
    return true;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Top Banner & Title */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-kinpaku/10 border border-kinpaku/30 text-kinpaku text-xs font-mono">
                <BookOpen className="w-3.5 h-3.5" />
                <span>Hệ Thống Tài Khoản Kế Toán Doanh Nghiệp</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Tra Cứu Tài Khoản Chuẩn Hóa</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Cập nhật chính xác quy định danh mục tài khoản theo Thông tư 99/2025/TT-BTC, Thông tư 200/2014/TT-BTC và Thông tư 133/2016/TT-BTC.
              </p>
            </div>

            {/* Regime Toggle (Pill Switcher) */}
            <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-graphite border border-white/[0.08] w-fit">
              <button
                onClick={() => setRegime('TT99')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  regime === 'TT99'
                    ? 'bg-kinpaku text-on-gold font-bold shadow-[0_0_12px_-2px_rgba(245,196,81,0.4)]'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                TT 99/2025 (Từ 2026)
              </button>
              <button
                onClick={() => setRegime('TT200')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  regime === 'TT200'
                    ? 'bg-patina text-on-gold font-bold shadow-[0_0_12px_-2px_rgba(112,192,208,0.4)]'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                TT 200/2014 (Kỳ cũ)
              </button>
              <button
                onClick={() => setRegime('TT133')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  regime === 'TT133'
                    ? 'bg-graphite-2 text-champagne font-bold border border-white/20'
                    : 'text-muted hover:text-champagne'
                }`}
              >
                TT 133/2016 (DNNVV)
              </button>
            </div>
          </div>

          {/* Search Bar & Quick Category Filters */}
          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Nhập số hiệu tài khoản (VD: 112, 155, 621, 642) hoặc tên tài khoản..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-graphite border border-white/10 text-champagne text-xs placeholder:text-muted focus:outline-none focus:border-kinpaku/60 transition-colors"
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted hover:text-champagne"
                >
                  Xóa
                </button>
              )}
            </div>

            {/* Category Pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
              {[
                { id: 'all', label: 'Tất cả' },
                { id: 'money', label: 'Tiền & Ngân hàng (111, 112)' },
                { id: 'inventory', label: 'Hàng tồn kho (15x)' },
                { id: 'cost', label: 'Chi phí & Giá thành (62x, 154)' },
                { id: 'liabilities', label: 'Nợ phải trả (33x)' },
                { id: 'deprecated', label: 'Tài khoản bãi bỏ' },
              ].map((c) => (
                <button
                  key={c.id}
                  onClick={() => setCategoryFilter(c.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap transition-colors cursor-pointer ${
                    categoryFilter === c.id
                      ? 'bg-kinpaku/20 text-champagne font-medium border border-kinpaku/40'
                      : 'bg-white/[0.03] text-muted hover:text-champagne border border-white/[0.06]'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Highlights for TT99 Changes */}
      {regime === 'TT99' && (
        <div className="p-4 rounded-xl bg-kinpaku/10 border border-kinpaku/25 text-xs text-champagne flex items-start gap-3">
          <Info className="w-4 h-4 text-kinpaku shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-kinpaku">Điểm thay đổi trọng yếu theo Thông tư 99/2025/TT-BTC:</p>
            <p className="text-[11px] leading-relaxed text-warm">
              • <strong>TK 112</strong> đổi tên thành "Tiền gửi không kỳ hạn". • <strong>TK 155</strong> đổi tên thành "Sản phẩm" (bãi bỏ tiểu khoản 1551/1557 bắt buộc). • <strong>TK 244</strong> đổi tên thành "Ký quỹ, ký cược". • <strong>TK 215</strong> bổ sung mới "Tài sản sinh học". • <strong className="text-vermilion">BÃI BỎ HOÀN TOÀN</strong> các tài khoản: TK 611, TK 631, TK 161, TK 441.
            </p>
          </div>
        </div>
      )}

      {/* Account Cards Grid */}
      <div>
        <div className="flex items-center justify-between mb-3 text-xs text-muted">
          <span>Tìm thấy <strong className="text-champagne font-mono">{filteredAccounts.length}</strong> tài khoản phù hợp</span>
          <span className="font-mono text-[11px] text-faint">Chế độ: {regime}</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-muted text-xs">Đang tải danh mục tài khoản...</div>
        ) : filteredAccounts.length === 0 ? (
          <div className="p-12 text-center text-muted text-xs">Không tìm thấy tài khoản nào phù hợp với từ khóa "{query}"</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAccounts.map((acc) => {
              const isDeprecated = acc.status === 'Bãi bỏ';
              const isModified = Boolean(acc.note);

              return (
                <div
                  key={acc.code}
                  className={`double-bezel transition-all duration-200 group ${
                    isDeprecated ? 'opacity-65' : ''
                  }`}
                >
                  <div className="double-bezel-inner p-4 h-full flex flex-col justify-between">
                    <div>
                      {/* Top Header of Card */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-mono font-bold text-sm px-2.5 py-0.5 rounded-lg border ${
                              isDeprecated
                                ? 'bg-vermilion/15 text-vermilion border-vermilion/30 line-through'
                                : 'bg-kinpaku/15 text-kinpaku border-kinpaku/30'
                            }`}
                          >
                            TK {acc.code}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-white/[0.05] text-muted border border-white/[0.06]">
                            {acc.type}
                          </span>
                        </div>

                        <button
                          onClick={() => handleCopy(acc.code)}
                          className="p-1.5 rounded-lg text-muted hover:text-champagne hover:bg-white/10 transition-colors cursor-pointer"
                          title="Sao chép số hiệu tài khoản"
                        >
                          {copiedCode === acc.code ? (
                            <Check className="w-3.5 h-3.5 text-patina" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>

                      {/* Account Name */}
                      <h4 className="text-sm font-semibold text-champagne group-hover:text-kinpaku transition-colors">
                        {acc.name}
                      </h4>

                      {/* Status / Note */}
                      {isDeprecated && (
                        <div className="mt-2.5 p-2 rounded-lg bg-vermilion/15 border border-vermilion/30 text-[11px] text-vermilion flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-vermilion" />
                          <span>{acc.note || 'Bãi bỏ hoàn toàn theo quy định mới'}</span>
                        </div>
                      )}

                      {!isDeprecated && isModified && (
                        <div className="mt-2.5 p-2 rounded-lg bg-patina/15 border border-patina/30 text-[11px] text-patina flex items-center gap-1.5">
                          <Info className="w-3.5 h-3.5 shrink-0 text-patina" />
                          <span>{acc.note}</span>
                        </div>
                      )}
                    </div>

                    <div className="mt-3 pt-2 border-t border-white/[0.06] text-[10px] text-faint font-mono flex items-center justify-between">
                      <span>{acc.regime}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
};
