import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  BookOpen,
  Calendar,
  FileCheck,
  Scale,
} from 'lucide-react';

interface PillarRule {
  code: string;
  target: string;
  status: string;
}

interface Pillar {
  category: string;
  criterion: string;
  rules: PillarRule[];
}

export const LegalBasisView: React.FC = () => {
  const [data, setData] = useState<{
    title: string;
    last_updated: string;
    pillars: Pillar[];
  } | null>(null);

  useEffect(() => {
    fetch('/api/legal-basis')
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch(() => {});
  }, []);

  const sources = [
    { name: 'Cơ sở dữ liệu Quốc gia về VBQPPL', domain: 'vbpl.vn', url: 'https://vbpl.vn' },
    { name: 'Cổng thông tin điện tử Chính phủ', domain: 'chinhphu.vn', url: 'https://chinhphu.vn' },
    { name: 'Cổng thông tin điện tử Bộ Tài chính', domain: 'mof.gov.vn', url: 'https://mof.gov.vn' },
    { name: 'Cổng thông tin điện tử Tổng cục Thuế', domain: 'gdt.gov.vn', url: 'https://gdt.gov.vn' },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-kinpaku/10 border border-kinpaku/30 text-kinpaku text-xs font-mono">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Hệ Thống Căn Cứ Pháp Lý & Ma Trận Hiệu Lực</span>
              </div>
              <h2 className="text-2xl font-bold text-champagne mt-2">Ma Trận Quy Phạm Pháp Luật Kế Toán & Thuế</h2>
              <p className="text-xs text-muted mt-1 max-w-2xl">
                Phân định 4 mốc xét áp dụng theo loại văn bản quy phạm, loại bỏ suy diễn chủ quan và đối soát chặt chẽ với nguồn văn bản gốc Cấp 1 của Nhà nước.
              </p>
            </div>

            <div className="text-right text-xs font-mono text-muted">
              <span className="block text-[11px] text-faint">Cập nhật lần cuối</span>
              <span className="text-kinpaku font-bold">{data?.last_updated || '17/10/2026'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 90-Day Staleness Warning Card */}
      <div className="p-4 rounded-xl bg-vermilion/15 border border-vermilion/30 text-xs text-champagne flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-vermilion shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold text-vermilion">Quy Tắc Cảnh Báo Văn Bản Quá Hạn (Staleness Warning):</p>
          <p className="text-[11px] leading-relaxed text-warm">
            Khi viện dẫn bất kỳ văn bản pháp luật nào, nếu ngày rà soát gần nhất đã quá <strong>90 ngày</strong> so với thời điểm phát sinh giao dịch, hệ thống yêu cầu rà soát lại nguồn Cấp 1 để cập nhật tình trạng hiệu lực mới nhất trước khi ra quyết định thực thi.
          </p>
        </div>
      </div>

      {/* 4 Pillars Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {data?.pillars.map((p, idx) => (
          <div key={idx} className="double-bezel">
            <div className="double-bezel-inner p-5 space-y-3 h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-kinpaku/15 text-kinpaku border border-kinpaku/30 font-bold">
                    Nhóm {idx + 1}
                  </span>
                  <span className="text-[11px] font-mono text-muted">
                    Tiêu chí: <strong className="text-champagne">{p.criterion}</strong>
                  </span>
                </div>

                <h3 className="text-base font-bold text-champagne mb-3">{p.category}</h3>

                <div className="space-y-2">
                  {p.rules.map((r, rIdx) => (
                    <div
                      key={rIdx}
                      className="p-3 rounded-lg bg-graphite border border-white/[0.08] flex items-center justify-between text-xs"
                    >
                      <div>
                        <p className="font-mono font-bold text-patina">{r.code}</p>
                        <p className="text-[11px] text-muted mt-0.5">{r.target}</p>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-lacquer-deep text-warm border border-white/[0.08]">
                        {r.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Official Level-1 Source Links */}
      <div className="double-bezel">
        <div className="double-bezel-inner p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-kinpaku" />
            <h3 className="text-sm font-bold text-champagne">Nguồn Tra Cứu Cấp 1 (Chính Thức - Giá Trị Pháp Lý Cao Nhất)</h3>
          </div>
          <p className="text-xs text-muted">
            Mọi kết luận pháp lý và chính sách thuế bắt buộc đối chiếu với văn bản gốc tại các cổng thông tin quốc gia:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
            {sources.map((s, idx) => (
              <a
                key={idx}
                href={s.url}
                target="_blank"
                rel="noreferrer"
                className="p-3.5 rounded-xl bg-graphite hover:bg-graphite-2 border border-white/[0.08] text-xs transition-colors flex items-center justify-between group"
              >
                <div>
                  <p className="font-semibold text-champagne group-hover:text-kinpaku transition-colors">{s.name}</p>
                  <p className="text-[11px] font-mono text-muted mt-0.5">{s.domain}</p>
                </div>
                <ExternalLink className="w-3.5 h-3.5 text-muted group-hover:text-kinpaku transition-colors shrink-0 ml-2" />
              </a>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
};
