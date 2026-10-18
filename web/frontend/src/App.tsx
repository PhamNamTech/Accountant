import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopHeader } from './components/TopHeader';
import { DashboardOverview } from './components/DashboardOverview';
import { AccountLookup } from './components/AccountLookup';
import { InvoiceParserView } from './components/InvoiceParserView';
import { CostAccountingView } from './components/CostAccountingView';
import { GeneralJournalView } from './components/GeneralJournalView';
import { BankReconciliationView } from './components/BankReconciliationView';
import { BeancountView } from './components/BeancountView';
import { LegalBasisView } from './components/LegalBasisView';
import { CommandPalette } from './components/CommandPalette';
import { TabId } from './components/Navbar';
import { ExternalLink, ShieldCheck } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <div className="min-h-screen bg-lacquer text-champagne flex font-sans antialiased selection:bg-kinpaku/20 selection:text-kinpaku">
      
      {/* 1. Left Enterprise Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* 2. Main Workspace Layout (Padded left by 64 on desktop) */}
      <div className="lg:pl-64 flex-1 flex flex-col min-w-0 min-h-screen bg-lacquer">
        
        {/* Top Header App Bar */}
        <TopHeader
          activeTab={activeTab}
          onOpenSidebar={() => setIsSidebarOpen(true)}
          onOpenSearch={() => setIsSearchOpen(true)}
        />

        {/* Workspace Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
          {activeTab === 'overview' && <DashboardOverview setActiveTab={setActiveTab} />}
          {activeTab === 'accounts' && <AccountLookup />}
          {activeTab === 'invoices' && <InvoiceParserView />}
          {activeTab === 'cost' && <CostAccountingView />}
          {activeTab === 'journal' && <GeneralJournalView />}
          {activeTab === 'reconcile' && <BankReconciliationView />}
          {activeTab === 'beancount' && <BeancountView />}
          {activeTab === 'legal' && <LegalBasisView />}
        </main>

        {/* Enterprise Footer */}
        <footer className="mt-auto border-t border-hairline bg-lacquer-deep py-4 px-6 text-xs text-muted font-mono">
          <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="font-bold text-champagne tracking-wide">KETOAN·VN</span>
              <span className="text-faint">·</span>
              <span className="text-muted">Vietnam Accounting AI Suite</span>
              <span className="text-faint">·</span>
              <span className="text-kinpaku font-semibold">TT 99/2025/TT-BTC</span>
            </div>

            <div className="flex items-center gap-4 text-[11px]">
              <a
                href="/docs"
                target="_blank"
                rel="noreferrer"
                className="text-muted hover:text-kinpaku transition-colors flex items-center gap-1"
              >
                <span>Swagger API (/docs)</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <span className="text-faint">·</span>
              <span className="text-patina font-semibold">Chuẩn VAS 02</span>
            </div>
          </div>
        </footer>

      </div>

      {/* 3. Global Command Palette (⌘K) */}
      <CommandPalette
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        setActiveTab={setActiveTab}
      />

    </div>
  );
}

export default App;
