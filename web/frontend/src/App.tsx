import React from 'react';
import { BankInvoicesView } from './components/BankInvoicesView';
import { Building2, Sparkles, ExternalLink } from 'lucide-react';

export function App() {
  return (
    <div className="min-h-[100dvh] bg-bg text-ink flex flex-col antialiased">
      
      {/* Top Header */}
      <header className="h-16 px-4 sm:px-8 bg-surface shadow-2xs flex items-center justify-between sticky top-0 z-30">
        <div className="max-w-6xl w-full mx-auto flex items-center justify-between">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-3 select-none">
            <div className="w-9 h-9 rounded-xl bg-surface-hover flex items-center justify-center text-accent">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-sm sm:text-base tracking-tight text-ink">
                KETOAN<span className="text-accent">·VN</span>
              </span>
              <span className="hidden sm:inline-block text-xs text-muted ml-2 pl-2 border-l border-border">
                Tự động hóa Hóa đơn Ngân hàng Vietcombank
              </span>
            </div>
          </div>

          {/* Quick API Docs Link */}
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-bg hover:bg-surface-hover text-xs text-muted hover:text-ink transition-colors"
          >
            <span>Swagger API</span>
            <ExternalLink className="w-3.5 h-3.5 text-faint" />
          </a>

        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-6xl w-full mx-auto">
        <BankInvoicesView />
      </main>

      {/* Minimal Footer */}
      <footer className="mt-auto py-5 px-6 text-xs text-muted bg-surface/50 border-t border-border/40">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Building2 className="w-3.5 h-3.5 text-accent" />
            <span>Thư mục lưu trữ: <code>data/chung_tu/hoa_don_bank/</code></span>
          </div>
          <span className="text-faint text-[11px]">
            Tự động giải mã AES-128-CBC &amp; tải tệp XML, PDF từ Vietcombank
          </span>
        </div>
      </footer>

    </div>
  );
}

export default App;
