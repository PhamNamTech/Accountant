import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  Download,
  Calendar,
  FileSpreadsheet,
  FileText,
  FileCode,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Search,
  Building2,
  FolderOpen,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Archive
} from 'lucide-react';

interface BankInvoice {
  stt: number;
  so_hd: string;
  ngay_hd: string;
  ngay_ky: string;
  ky_hieu: string;
  nha_cung_cap: string;
  mst: string;
  ghi_chu: string;
  thanh_tien: number;
  thue_suat: string;
  tien_thue: number;
  tong_tien: number;
  tk_no: string;
  tk_co: string;
  tk_thue: string;
  pdf_file: string;
  xml_file: string;
  has_pdf: boolean;
  has_xml: boolean;
}

const formatVND = (num: number = 0) =>
  new Intl.NumberFormat('vi-VN').format(Math.round(num)) + ' ₫';

const getCurrentMonthString = () => {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
};

const formatMonthDisplay = (monthStr: string) => {
  if (!monthStr || !monthStr.includes('-')) return monthStr || 'Chọn kỳ';
  const [y, m] = monthStr.split('-');
  return `Tháng ${m}/${y}`;
};

export const BankInvoicesView: React.FC = () => {
  const [months, setMonths] = useState<string[]>([]);
  const [selectedMonth, setSelectedMonth] = useState<string>(() => getCurrentMonthString());
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [calendarYear, setCalendarYear] = useState<number>(() => {
    const [y] = getCurrentMonthString().split('-').map(Number);
    return y || 2026;
  });

  const calendarRef = useRef<HTMLDivElement>(null);

  // Close calendar popup on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target as Node)) {
        setIsCalendarOpen(false);
      }
    };
    if (isCalendarOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isCalendarOpen]);

  // Stepper handlers
  const handlePrevMonth = () => {
    if (!selectedMonth) return;
    const [y, m] = selectedMonth.split('-').map(Number);
    const prevDate = new Date(y, m - 2, 1);
    const nextMonthStr = `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, '0')}`;
    setSelectedMonth(nextMonthStr);
    setCalendarYear(prevDate.getFullYear());
  };

  const handleNextMonth = () => {
    if (!selectedMonth) return;
    const [y, m] = selectedMonth.split('-').map(Number);
    const nextDate = new Date(y, m, 1);
    const nextMonthStr = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, '0')}`;
    setSelectedMonth(nextMonthStr);
    setCalendarYear(nextDate.getFullYear());
  };

  const handleSelectMonth = (monthNumber: number) => {
    const monthStr = `${calendarYear}-${String(monthNumber).padStart(2, '0')}`;
    setSelectedMonth(monthStr);
    setIsCalendarOpen(false);
  };

  const handleJumpToCurrentMonth = () => {
    const currentStr = getCurrentMonthString();
    setSelectedMonth(currentStr);
    setCalendarYear(Number(currentStr.split('-')[0]));
    setIsCalendarOpen(false);
  };

  const [invoices, setInvoices] = useState<BankInvoice[]>([]);
  const [hasExcel, setHasExcel] = useState(false);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<number>(0);
  const [downloadStep, setDownloadStep] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Stop polling helper
  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  }, []);

  // Load available months from server
  const loadMonths = useCallback((targetMonth?: string) => {
    fetch('/api/bank-invoices/months')
      .then((res) => res.json())
      .then((data) => {
        if (data.months && data.months.length > 0) {
          setMonths(data.months);
          if (targetMonth) {
            setSelectedMonth(targetMonth);
            setCalendarYear(Number(targetMonth.split('-')[0]));
          } else {
            // Default to latest downloaded month if current selection hasn't been set by user
            setSelectedMonth((prev) => {
              const active = prev || data.months[0];
              if (active) {
                setCalendarYear(Number(active.split('-')[0]));
              }
              return active;
            });
          }
        }
      })
      .catch((err) => console.error('Error loading months:', err));
  }, []);

  // Load invoices for a given month
  const loadInvoices = useCallback((month: string) => {
    if (!month) return;
    setLoading(true);
    fetch(`/api/bank-invoices/list?month=${encodeURIComponent(month)}`)
      .then((res) => res.json())
      .then((data) => {
        setInvoices(data.invoices || []);
        setHasExcel(Boolean(data.has_excel));
      })
      .catch((err) => {
        console.error('Error fetching invoices:', err);
        setInvoices([]);
        setHasExcel(false);
      })
      .finally(() => setLoading(false));
  }, []);

  // Poll download status
  const pollStatus = useCallback(() => {
    stopPolling();
    pollTimerRef.current = setInterval(async () => {
      try {
        const res = await fetch('/api/bank-invoices/download-status');
        const data = await res.json();
        
        if (data.is_running) {
          setDownloading(true);
          setDownloadStep(data.message || 'Đang xử lý...');
          setDownloadProgress(data.progress || 0);
        } else {
          stopPolling();
          setDownloading(false);
          if (data.status === 'completed') {
            setStatusMessage(data.message || 'Đã tải thành công toàn bộ hóa đơn từ Vietcombank!');
            const completedMonth = data.month || selectedMonth;
            if (completedMonth) {
              loadMonths(completedMonth);
              loadInvoices(completedMonth);
            }
          } else if (data.status === 'error') {
            setErrorMessage(data.error || data.message || 'Lỗi khi tải hóa đơn từ Vietcombank');
          }
        }
      } catch (err) {
        stopPolling();
        setDownloading(false);
      }
    }, 1000);
  }, [selectedMonth, loadMonths, loadInvoices, stopPolling]);

  // Initial load & check if a download is already running
  useEffect(() => {
    loadMonths();

    fetch('/api/bank-invoices/download-status')
      .then((res) => res.json())
      .then((data) => {
        if (data.is_running) {
          setDownloading(true);
          setDownloadStep(data.message || 'Đang tải hóa đơn...');
          setDownloadProgress(data.progress || 0);
          pollStatus();
        }
      })
      .catch(() => {});

    return () => {
      stopPolling();
    };
  }, [loadMonths, pollStatus, stopPolling]);

  // Load invoices when selectedMonth changes
  useEffect(() => {
    if (selectedMonth) {
      loadInvoices(selectedMonth);
    }
  }, [selectedMonth, loadInvoices]);

  // Handle Download from Vietcombank Direct API
  const handleDownloadFromVCB = async () => {
    if (!selectedMonth) {
      setErrorMessage('Vui lòng chọn kỳ hóa đơn cần tải');
      return;
    }

    setDownloading(true);
    setDownloadProgress(0);
    setDownloadStep(`Đang khởi tạo kết nối Vietcombank cho kỳ ${formatMonthDisplay(selectedMonth)}...`);
    setStatusMessage(null);
    setErrorMessage(null);

    try {
      const res = await fetch('/api/bank-invoices/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          month: selectedMonth,
          force: true,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setDownloadStep(data.message || 'Đã bắt đầu tải trong nền...');
        pollStatus();
      } else {
        setDownloading(false);
        setErrorMessage(data.message || 'Không thể bắt đầu tiến trình tải');
      }
    } catch (err: any) {
      setDownloading(false);
      setErrorMessage(err.message || 'Không thể kết nối đến máy chủ backend');
    }
  };

  // Memoized filtered invoices for high performance
  const filteredInvoices = useMemo(() => {
    if (!searchTerm.trim()) return invoices;
    const term = searchTerm.toLowerCase();
    return invoices.filter(
      (inv) =>
        inv.so_hd.toLowerCase().includes(term) ||
        inv.ghi_chu.toLowerCase().includes(term)
    );
  }, [invoices, searchTerm]);

  // Memoized total amounts
  const totalAmount = useMemo(
    () => invoices.reduce((sum, i) => sum + (i.tong_tien || 0), 0),
    [invoices]
  );

  return (
    <div className="space-y-6">
      
      {/* Action Card: Core Purpose of the Project */}
      <div className="p-6 sm:p-8 rounded-2xl bg-surface shadow-xs space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-hover text-accent text-xs font-medium">
              <Building2 className="w-3.5 h-3.5" />
              <span>Vietcombank Direct API</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-ink mt-2">
              Tải Hóa Đơn Điện Tử Vietcombank
            </h1>
            <p className="text-xs sm:text-sm text-muted mt-1 max-w-2xl leading-relaxed">
              Tự động kết nối cổng Vietcombank, giải mã AES-128 và tải trọn bộ file <b>XML</b> và <b>PDF</b> gốc theo tháng về máy.
            </p>
          </div>

          {/* Month Selector & Primary Download Button */}
          <div className="flex items-center flex-wrap gap-3">
            
            {/* Month Picker / Calendar Component */}
            <div className="relative" ref={calendarRef}>
              <div className="flex items-center gap-1 p-1 rounded-xl bg-bg border border-border/60 text-xs shadow-xs">
                
                {/* Stepper: Previous Month */}
                <button
                  type="button"
                  onClick={handlePrevMonth}
                  disabled={downloading}
                  className="p-1.5 rounded-lg text-muted hover:text-ink hover:bg-surface transition-colors cursor-pointer disabled:opacity-40"
                  title="Tháng trước"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                {/* Interactive Calendar Trigger */}
                <button
                  type="button"
                  onClick={() => setIsCalendarOpen(!isCalendarOpen)}
                  disabled={downloading}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all cursor-pointer font-bold select-none ${
                    isCalendarOpen
                      ? 'bg-accent text-accent-ink shadow-xs'
                      : 'hover:bg-surface text-ink'
                  }`}
                  title="Bấm để mở lịch chọn tháng"
                >
                  <Calendar className={`w-4 h-4 shrink-0 ${isCalendarOpen ? 'text-accent-ink' : 'text-accent'}`} />
                  <span className="tabular-nums text-xs sm:text-sm">
                    {formatMonthDisplay(selectedMonth)}
                  </span>
                  <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${isCalendarOpen ? 'rotate-180 text-accent-ink' : 'text-muted'}`} />
                </button>

                {/* Stepper: Next Month */}
                <button
                  type="button"
                  onClick={handleNextMonth}
                  disabled={downloading}
                  className="p-1.5 rounded-lg text-muted hover:text-ink hover:bg-surface transition-colors cursor-pointer disabled:opacity-40"
                  title="Tháng sau"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              {/* Calendar 12-Month Popover Grid */}
              {isCalendarOpen && (
                <div className="absolute top-full mt-2 left-0 sm:left-auto sm:right-0 z-50 w-72 p-4 rounded-2xl bg-surface border border-border/80 shadow-xl space-y-3.5 animate-in fade-in zoom-in-95 duration-150">
                  
                  {/* Year Navigation Header */}
                  <div className="flex items-center justify-between px-1">
                    <button
                      type="button"
                      onClick={() => setCalendarYear((prev) => prev - 1)}
                      className="p-1 rounded-lg text-muted hover:text-ink hover:bg-surface-hover transition-colors cursor-pointer"
                      title="Năm trước"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>

                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-sm text-ink tabular-nums">
                        Năm {calendarYear}
                      </span>
                      {calendarYear === new Date().getFullYear() && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-accent/15 text-accent font-semibold">
                          Hiện tại
                        </span>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={() => setCalendarYear((prev) => prev + 1)}
                      className="p-1 rounded-lg text-muted hover:text-ink hover:bg-surface-hover transition-colors cursor-pointer"
                      title="Năm sau"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>

                  {/* 12 Months Grid */}
                  <div className="grid grid-cols-4 gap-1.5">
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => {
                      const monthKey = `${calendarYear}-${String(m).padStart(2, '0')}`;
                      const isSelected = selectedMonth === monthKey;
                      const isDownloaded = months.includes(monthKey);
                      const isCurrent = getCurrentMonthString() === monthKey;

                      return (
                        <button
                          key={m}
                          type="button"
                          onClick={() => handleSelectMonth(m)}
                          className={`relative py-2 px-1 rounded-xl text-xs font-semibold transition-all cursor-pointer flex flex-col items-center justify-center gap-0.5 ${
                            isSelected
                              ? 'bg-accent text-accent-ink shadow-sm font-bold scale-102'
                              : isDownloaded
                              ? 'bg-surface-hover text-ink border border-accent/40 hover:border-accent hover:bg-vanilla/40'
                              : 'text-ink/80 hover:bg-surface-hover hover:text-ink'
                          } ${isCurrent && !isSelected ? 'ring-1 ring-accent/60' : ''}`}
                          title={isDownloaded ? `Tháng ${m}/${calendarYear} (Đã có dữ liệu)` : `Tháng ${m}/${calendarYear}`}
                        >
                          <span>Thg {m}</span>
                          {isDownloaded && !isSelected && (
                            <span className="w-1.5 h-1.5 rounded-full bg-accent" />
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Calendar Footer: Legend & Jump to Current Month */}
                  <div className="pt-2 border-t border-border/40 flex items-center justify-between text-[11px]">
                    <div className="flex items-center gap-1.5 text-muted">
                      <span className="w-2 h-2 rounded-full bg-accent inline-block shrink-0" />
                      <span>Đã tải</span>
                    </div>

                    <button
                      type="button"
                      onClick={handleJumpToCurrentMonth}
                      className="text-accent hover:underline font-semibold cursor-pointer"
                    >
                      Về tháng này
                    </button>
                  </div>

                </div>
              )}
            </div>

            {/* THE ONE AND ONLY CORE ACTION BUTTON */}
            <button
              onClick={handleDownloadFromVCB}
              disabled={downloading}
              className="px-5 py-2.5 rounded-xl bg-accent hover:bg-accent-hover text-accent-ink font-semibold text-xs sm:text-sm transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50 shadow-sm"
              title="Kéo toàn bộ XML và PDF từ tài khoản Vietcombank"
            >
              {downloading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang tải XML & PDF...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Tải Hóa Đơn (XML & PDF)</span>
                </>
              )}
            </button>

            {/* 1-Click Download All Available Invoices (ZIP) */}
            {invoices.length > 0 && (
              <a
                href={`/api/bank-invoices/download-zip?month=${encodeURIComponent(selectedMonth)}`}
                download
                className="px-4 py-2.5 rounded-xl bg-vanilla/60 hover:bg-vanilla text-ink font-semibold text-xs sm:text-sm transition-all flex items-center gap-2 cursor-pointer shadow-xs border border-accent/20 hover:border-accent"
                title={`Tải về máy trọn bộ file PDF & XML của ${formatMonthDisplay(selectedMonth).toLowerCase()} (.ZIP)`}
              >
                <Archive className="w-4 h-4 text-accent" />
                <span>Tải Toàn Bộ Chứng Từ (ZIP)</span>
              </a>
            )}

            {/* Optional Excel summary export */}
            {hasExcel && (
              <a
                href={`/api/bank-invoices/export-misa-excel?month=${encodeURIComponent(selectedMonth)}`}
                download
                className="px-4 py-2.5 rounded-xl bg-bg hover:bg-surface-hover text-ink text-xs font-medium transition-colors flex items-center gap-2"
                title="Tải bảng kê tổng hợp các hóa đơn đã tải"
              >
                <FileSpreadsheet className="w-4 h-4 text-accent" />
                <span>Bảng Kê Excel</span>
              </a>
            )}
          </div>
        </div>

        {/* Real-time Download Progress Bar */}
        {downloading && (
          <div className="p-4 rounded-xl bg-surface-hover text-ink text-xs space-y-2 border-l-4 border-accent">
            <div className="flex items-center justify-between">
              <span className="font-semibold flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-accent shrink-0" />
                <span>{downloadStep || 'Đang kết nối Vietcombank và tải hóa đơn...'}</span>
              </span>
              {downloadProgress > 0 && (
                <span className="font-bold tabular-nums text-accent">{downloadProgress}%</span>
              )}
            </div>
            {downloadProgress > 0 && (
              <div className="w-full bg-border/50 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-accent h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${downloadProgress}%` }}
                />
              </div>
            )}
          </div>
        )}

        {/* Feedback Alert: Success */}
        {statusMessage && (
          <div className="p-4 rounded-xl bg-surface-hover text-ink text-xs flex items-center justify-between border-l-4 border-accent">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-accent shrink-0" />
              <span>{statusMessage}</span>
            </div>
            <button
              onClick={() => setStatusMessage(null)}
              className="text-muted hover:text-ink text-xs px-2 py-0.5 rounded cursor-pointer"
            >
              Đóng
            </button>
          </div>
        )}

        {/* Feedback Alert: Error */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-danger/10 text-danger text-xs flex items-center justify-between border-l-4 border-danger">
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 text-danger shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-danger hover:underline text-xs px-2 py-0.5 rounded cursor-pointer"
            >
              Đóng
            </button>
          </div>
        )}
      </div>

      {/* Invoices List Table */}
      <div className="p-6 rounded-2xl bg-surface shadow-xs space-y-4">
        
        {/* Header Bar with Search & Summary */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2">
          <div className="flex items-center gap-3">
            <h2 className="text-base font-bold text-ink">
              Danh Sách Hóa Đơn Đã Tải ({filteredInvoices.length})
            </h2>
            {invoices.length > 0 && (
              <span className="text-xs text-muted">
                Tổng thanh toán: <strong className="text-accent tabular-nums">{formatVND(totalAmount)}</strong>
              </span>
            )}
          </div>

          {/* Quick Search & Download All Vouchers */}
          <div className="flex items-center gap-2.5">
            {months.length > 1 && (
              <a
                href="/api/bank-invoices/download-zip?month=all"
                download
                className="px-3 py-1.5 rounded-xl bg-bg hover:bg-surface-hover text-muted hover:text-ink text-[11px] font-medium transition-colors hidden sm:flex items-center gap-1.5 border border-border/40"
                title="Tải toàn bộ chứng từ (PDF & XML) của tất cả các tháng đã lưu dạng file nén ZIP"
              >
                <Archive className="w-3.5 h-3.5 text-accent" />
                <span>Tải tất cả các kỳ ({months.length} tháng)</span>
              </a>
            )}

            {invoices.length > 0 && (
              <div className="relative max-w-xs w-full">
                <Search className="w-3.5 h-3.5 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Tìm số HĐ, nội dung..."
                  className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-bg text-ink text-xs focus:outline-none focus:ring-1 focus:ring-accent placeholder:text-muted"
                />
              </div>
            )}
          </div>
        </div>

        {/* Invoices Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-bg text-muted font-medium">
              <tr>
                <th className="py-3 px-3 text-center w-12">STT</th>
                <th className="py-3 px-3 w-28">Số Hóa Đơn</th>
                <th className="py-3 px-3 w-24">Ngày HĐ</th>
                <th className="py-3 px-4">Nội Dung / Nghiệp Vụ</th>
                <th className="py-3 px-3 text-right w-32">Tổng Tiền</th>
                <th className="py-3 px-3 text-center w-36">Tải Chứng Từ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bg">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-muted">
                    <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2 text-accent" />
                    Đang tải danh sách hóa đơn...
                  </td>
                </tr>
              ) : filteredInvoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-muted">
                    <FolderOpen className="w-8 h-8 mx-auto mb-2 text-faint" />
                    <p className="text-ink font-medium">Chưa có hóa đơn nào cho {formatMonthDisplay(selectedMonth).toLowerCase()}</p>
                    <p className="text-[11px] text-faint mt-1">
                      Hãy nhấn nút <b>"Tải Hóa Đơn (XML & PDF)"</b> ở trên để tự động kéo hóa đơn từ Vietcombank về máy.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredInvoices.map((inv) => (
                  <tr key={inv.stt} className="hover:bg-surface-hover/60 transition-colors">
                    <td className="py-3 px-3 text-center text-faint tabular-nums">
                      {inv.stt}
                    </td>
                    <td className="py-3 px-3 font-bold text-accent tabular-nums">
                      {inv.so_hd}
                    </td>
                    <td className="py-3 px-3 text-muted tabular-nums">
                      {inv.ngay_hd}
                    </td>
                    <td className="py-3 px-4 text-ink font-medium">
                      {inv.ghi_chu}
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-ink tabular-nums">
                      {formatVND(inv.tong_tien)}
                    </td>
                    <td className="py-3 px-3 text-center">
                      <div className="flex items-center justify-center gap-2">
                        {/* PDF Download Button */}
                        {inv.has_pdf ? (
                          <a
                            href={`/api/bank-invoices/file?month=${encodeURIComponent(selectedMonth)}&filename=${encodeURIComponent(inv.pdf_file)}`}
                            target="_blank"
                            rel="noreferrer"
                            title={`Xem / Tải file PDF: ${inv.pdf_file}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-hover hover:bg-vanilla text-accent font-semibold transition-colors"
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>PDF</span>
                          </a>
                        ) : (
                          <span className="text-[11px] text-faint">-</span>
                        )}

                        {/* XML Download Button */}
                        {inv.has_xml ? (
                          <a
                            href={`/api/bank-invoices/file?month=${encodeURIComponent(selectedMonth)}&filename=${encodeURIComponent(inv.xml_file)}`}
                            target="_blank"
                            rel="noreferrer"
                            title={`Tải file XML gốc: ${inv.xml_file}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-bg hover:bg-surface-hover text-muted hover:text-ink font-medium transition-colors"
                          >
                            <FileCode className="w-3.5 h-3.5" />
                            <span>XML</span>
                          </a>
                        ) : (
                          <span className="text-[11px] text-faint">-</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
};
