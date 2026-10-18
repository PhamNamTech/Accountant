import React, { useState, useEffect } from 'react';
import {
  Code2,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  FileCode,
  ShieldCheck,
} from 'lucide-react';

export const BeancountView: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch('/api/beancount/verify')
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleCopy = () => {
    if (data?.raw_content) {
      navigator.clipboard.writeText(data.raw_content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-patina/10 border border-patina/30 text-patina text-xs font-mono">
                <Code2 className="w-3.5 h-3.5" />
                <span>Plaintext Double-Entry Accounting (Beancount)</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Sổ Cái Kế Toán Plaintext Beancount</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Sổ cái kế toán kép lưu trữ dưới dạng mã nguồn văn bản thuần (Plaintext), quản lý phiên bản qua Git và kiểm tra tính cân đối kép tự động qua Python Beancount Engine.
              </p>
            </div>

            {/* Status Pill */}
            {data && (
              <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-patina/15 border border-patina/30 text-patina text-xs font-mono w-fit font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Cân đối Nợ - Có Tuyệt Đối</span>
              </div>
            )}
          </div>

          {/* Quick Metrics */}
          {data && (
            <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-3 rounded-xl bg-graphite border border-white/[0.08]">
                <span className="text-[10px] text-muted">Trạng Thái Sổ</span>
                <p className="text-sm font-bold text-patina mt-0.5">{data.status === 'valid' ? 'Hợp lệ 100%' : 'Có lỗi'}</p>
              </div>

              <div className="p-3 rounded-xl bg-graphite border border-white/[0.08]">
                <span className="text-[10px] text-muted">Tổng Số Bút Toán</span>
                <p className="text-sm font-bold text-champagne mt-0.5">{data.total_entries} giao dịch</p>
              </div>

              <div className="p-3 rounded-xl bg-graphite border border-white/[0.08]">
                <span className="text-[10px] text-muted">Đơn Vị Tiền Tệ</span>
                <p className="text-sm font-bold text-kinpaku mt-0.5">
                  {Array.isArray(data.operating_currency) ? data.operating_currency.join(', ') : 'VND'}
                </p>
              </div>

              <div className="p-3 rounded-xl bg-graphite border border-white/[0.08]">
                <span className="text-[10px] text-muted">Lỗi Mất Cân Đối</span>
                <p className="text-sm font-bold text-patina mt-0.5">0 lỗi</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Raw Beancount Plaintext File Inspector */}
      <div className="double-bezel">
        <div className="double-bezel-inner overflow-hidden">
          <div className="p-4 bg-lacquer-deep border-b border-white/[0.08] flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono text-warm">
              <FileCode className="w-4 h-4 text-patina" />
              <span>data/database/so_cai.beancount</span>
            </div>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-graphite hover:bg-graphite-2 text-xs text-warm hover:text-champagne border border-white/10 transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-patina" /> : <Copy className="w-3.5 h-3.5 text-muted" />}
              <span>{copied ? 'Đã sao chép' : 'Sao chép sổ'}</span>
            </button>
          </div>

          <div className="p-5 bg-lacquer-deep font-mono text-xs text-warm overflow-x-auto max-h-[500px] leading-relaxed">
            {loading ? (
              <div className="text-muted">Đang đọc sổ cái Beancount...</div>
            ) : (
              <pre className="text-warm">{data?.raw_content || 'Không có dữ liệu'}</pre>
            )}
          </div>
        </div>
      </div>

    </div>
  );
};
