import React, { useState, useEffect } from 'react';
import {
  Database,
  Plus,
  Search,
  Download,
  Filter,
  CheckCircle2,
  AlertCircle,
  Calendar,
  X,
} from 'lucide-react';

interface JournalEntry {
  id: number;
  ngay_ghi_so: string;
  so_chung_tu: string;
  ngay_chung_tu: string;
  dien_giai: string;
  tk_no: string;
  tk_co: string;
  so_tien: number;
}

export const GeneralJournalView: React.FC = () => {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalAmount, setTotalAmount] = useState(0);
  const [search, setSearch] = useState('');
  const [accountFilter, setAccountFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [newEntry, setNewEntry] = useState({
    ngay_ghi_so: new Date().toISOString().split('T')[0],
    so_chung_tu: `PKT-${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 900) + 100)}`,
    ngay_chung_tu: new Date().toISOString().split('T')[0],
    dien_giai: '',
    tk_no: '154',
    tk_co: '621',
    so_tien: 0,
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (accountFilter) params.append('tk', accountFilter);

      const res = await fetch(`/api/journal/entries?${params.toString()}`);
      const data = await res.json();
      setEntries(data.items || []);
      setTotalRecords(data.total_records || 0);
      setTotalAmount(data.total_amount || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [search, accountFilter]);

  const handleCreateEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    if (newEntry.so_tien <= 0) {
      setFormError('Số tiền ghi sổ phải lớn hơn 0');
      return;
    }
    if (newEntry.tk_no === newEntry.tk_co) {
      setFormError('Tài khoản Nợ và Tài khoản Có không được trùng nhau');
      return;
    }

    try {
      const res = await fetch('/api/journal/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEntry),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Lỗi ghi sổ');

      setFormSuccess('Đã ghi sổ thành công!');
      setTimeout(() => {
        setIsModalOpen(false);
        setFormSuccess(null);
        fetchEntries();
      }, 1000);
    } catch (err: any) {
      setFormError(err.message);
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
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-kinpaku/10 border border-kinpaku/30 text-kinpaku text-xs font-mono">
                <Database className="w-3.5 h-3.5" />
                <span>Sổ Sách Kế Toán Kép SQLite</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Sổ Nhật Ký Chung (Mẫu S03a-DN)</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Lưu trữ toàn bộ giao dịch kép (Double-entry), kiểm tra cân đối Tổng Nợ = Tổng Có tuyệt đối theo thời gian thực từ cơ sở dữ liệu `ketoan.db`.
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-kinpaku hover:bg-kinpaku-vivid text-on-gold text-xs font-bold transition-all shadow-[0_0_15px_-3px_rgba(245,196,81,0.4)] active:scale-95 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Thêm Bút Toán</span>
              </button>

              <a
                href="/api/journal/export-excel"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-graphite hover:bg-graphite-2 text-champagne border border-white/10 text-xs font-medium transition-colors"
                title="Xuất Sổ Nhật Ký Chung Excel"
              >
                <Download className="w-4 h-4 text-kinpaku" />
                <span>Xuất Excel S03a</span>
              </a>
            </div>
          </div>

          {/* Quick Metrics & Filters */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            {/* Search */}
            <div className="md:col-span-5 relative">
              <Search className="w-4 h-4 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Tìm theo số chứng từ hoặc diễn giải..."
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-graphite border border-white/10 text-champagne placeholder:text-muted text-xs focus:outline-none focus:border-kinpaku/50"
              />
            </div>

            {/* Account filter */}
            <div className="md:col-span-3">
              <input
                type="text"
                value={accountFilter}
                onChange={(e) => setAccountFilter(e.target.value)}
                placeholder="Lọc tài khoản (VD: 112, 154, 331)..."
                className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne placeholder:text-muted font-mono text-xs focus:outline-none focus:border-patina/50"
              />
            </div>

            {/* Stats Overview */}
            <div className="md:col-span-4 flex items-center justify-end gap-4 text-xs font-mono">
              <div>
                <span className="text-muted text-[10px] block">Tổng số bút toán</span>
                <span className="text-champagne font-bold">{totalRecords}</span>
              </div>
              <div className="border-l border-white/10 pl-4">
                <span className="text-muted text-[10px] block">Tổng phát sinh</span>
                <span className="text-kinpaku font-bold tabular-nums">{formatVND(totalAmount)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Journal Table */}
      <div className="double-bezel">
        <div className="double-bezel-inner overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-warm">
              <thead className="bg-lacquer-deep text-[11px] uppercase tracking-wider text-faint border-b border-white/[0.08]">
                <tr>
                  <th className="py-3 px-4 text-center font-mono">ID</th>
                  <th className="py-3 px-4 font-mono">Ngày Ghi Sổ</th>
                  <th className="py-3 px-4 font-mono">Số Hiệu CT</th>
                  <th className="py-3 px-4 font-mono">Ngày CT</th>
                  <th className="py-3 px-4">Diễn Giải Nghiệp Vụ</th>
                  <th className="py-3 px-4 text-center font-mono">TK Nợ</th>
                  <th className="py-3 px-4 text-center font-mono">TK Có</th>
                  <th className="py-3 px-4 text-right font-mono">Số Tiền (VND)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06]">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-muted text-xs">
                      Đang tải sổ nhật ký chung...
                    </td>
                  </tr>
                ) : entries.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-muted text-xs">
                      Không tìm thấy bút toán nào
                    </td>
                  </tr>
                ) : (
                  entries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 px-4 text-center font-mono text-faint">{entry.id}</td>
                      <td className="py-3 px-4 font-mono text-warm">{entry.ngay_ghi_so}</td>
                      <td className="py-3 px-4 font-mono font-bold text-patina">{entry.so_chung_tu}</td>
                      <td className="py-3 px-4 font-mono text-muted">{entry.ngay_chung_tu}</td>
                      <td className="py-3 px-4 text-champagne font-medium">{entry.dien_giai}</td>
                      <td className="py-3 px-4 text-center font-mono font-bold text-kinpaku bg-kinpaku/5">
                        {entry.tk_no}
                      </td>
                      <td className="py-3 px-4 text-center font-mono font-bold text-patina bg-patina/5">
                        {entry.tk_co}
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-champagne tabular-nums">
                        {formatVND(entry.so_tien)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modal: Add Entry */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-lacquer-deep/80 backdrop-blur-md animate-fadeIn">
          <div className="double-bezel max-w-lg w-full">
            <div className="double-bezel-inner p-6 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
                <h3 className="text-base font-bold text-champagne">Ghi Sổ Kế Toán Bút Toán Mới</h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="p-1 rounded-lg text-muted hover:text-champagne hover:bg-white/10"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {formError && (
                <div className="p-3 rounded-lg bg-vermilion/15 border border-vermilion/30 text-xs text-champagne flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-vermilion shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              {formSuccess && (
                <div className="p-3 rounded-lg bg-patina/15 border border-patina/30 text-xs text-champagne flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-patina shrink-0" />
                  <span>{formSuccess}</span>
                </div>
              )}

              <form onSubmit={handleCreateEntry} className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-muted mb-1">Số hiệu chứng từ</label>
                    <input
                      type="text"
                      value={newEntry.so_chung_tu}
                      onChange={(e) => setNewEntry({ ...newEntry, so_chung_tu: e.target.value })}
                      required
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>

                  <div>
                    <label className="block text-muted mb-1">Ngày ghi sổ</label>
                    <input
                      type="date"
                      value={newEntry.ngay_ghi_so}
                      onChange={(e) =>
                        setNewEntry({
                          ...newEntry,
                          ngay_ghi_so: e.target.value,
                          ngay_chung_tu: e.target.value,
                        })
                      }
                      required
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono focus:outline-none focus:border-kinpaku/50"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted mb-1">Diễn giải nghiệp vụ</label>
                  <input
                    type="text"
                    value={newEntry.dien_giai}
                    onChange={(e) => setNewEntry({ ...newEntry, dien_giai: e.target.value })}
                    placeholder="VD: Mua nguyên vật liệu nhập kho, trả tiền điện..."
                    required
                    className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne placeholder:text-muted focus:outline-none focus:border-kinpaku/50"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-kinpaku mb-1 font-semibold">Tài khoản Nợ</label>
                    <input
                      type="text"
                      value={newEntry.tk_no}
                      onChange={(e) => setNewEntry({ ...newEntry, tk_no: e.target.value })}
                      placeholder="154, 155, 621..."
                      required
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-kinpaku/30 text-kinpaku font-mono font-bold focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-patina mb-1 font-semibold">Tài khoản Có</label>
                    <input
                      type="text"
                      value={newEntry.tk_co}
                      onChange={(e) => setNewEntry({ ...newEntry, tk_co: e.target.value })}
                      placeholder="111, 112, 331..."
                      required
                      className="w-full px-3 py-2 rounded-xl bg-graphite border border-patina/30 text-patina font-mono font-bold focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-muted mb-1">Số tiền phát sinh (VND)</label>
                  <input
                    type="number"
                    value={newEntry.so_tien}
                    onChange={(e) => setNewEntry({ ...newEntry, so_tien: Number(e.target.value) })}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-graphite border border-white/10 text-champagne font-mono text-sm font-bold focus:outline-none focus:border-kinpaku/50"
                  />
                </div>

                <div className="pt-3 flex items-center justify-end gap-2 border-t border-white/[0.08]">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-white/[0.05] text-muted hover:text-champagne cursor-pointer"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 rounded-xl bg-kinpaku hover:bg-kinpaku-vivid text-on-gold font-bold shadow-[0_0_15px_-3px_rgba(245,196,81,0.4)] cursor-pointer"
                  >
                    Ghi Sổ
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
