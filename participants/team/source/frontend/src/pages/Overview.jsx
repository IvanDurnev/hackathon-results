import { useState, useEffect } from 'react';
import Input from '../components/ui/Input';
import { getAnalyticsReport, formatCurrency, formatPeriod, exportToExcel } from '../services/api';
import { useFilters } from '../context/FiltersContext';

export default function Overview() {
  const { filters, setFilters, data, setData } = useFilters();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedRow, setSelectedRow] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getAnalyticsReport(filters);
      setData(result);
    } catch (err) {
      setError('Ошибка загрузки данных: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleApplyFilters = () => {
    fetchData();
  };

  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus(null);
    
    try {
      const result = await exportToExcel(filters);
      setExportStatus({ 
        type: 'success', 
        message: `Файл ${result.filename} успешно скачан` 
      });
      setTimeout(() => setExportStatus(null), 5000);
    } catch (err) {
      setExportStatus({ 
        type: 'error', 
        message: 'Ошибка экспорта: ' + err.message 
      });
      setTimeout(() => setExportStatus(null), 5000);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Фильтры */}
      <div className="bg-white rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8] shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <Input
            label="Период от"
            type="month"
            value={filters.period_from}
            onChange={(e) => handleFilterChange('period_from', e.target.value)}
          />
          <Input
            label="Период до"
            type="month"
            value={filters.period_to}
            onChange={(e) => handleFilterChange('period_to', e.target.value)}
          />
          <Input
            label="КЦСР маска"
            placeholder="1 для всех или код КЦСР"
            value={filters.kcsr_mask}
            onChange={(e) => handleFilterChange('kcsr_mask', e.target.value)}
          />
          <Input
            label="Название бюджета"
            placeholder="Например: Областной бюджет"
            value={filters.budget_name}
            onChange={(e) => handleFilterChange('budget_name', e.target.value)}
          />
          <Input
            label="Источник финансирования"
            placeholder="Региональные/Федеральные"
            value={filters.fund_source}
            onChange={(e) => handleFilterChange('fund_source', e.target.value)}
          />
          <Input
            label="Минимальная сумма"
            type="number"
            placeholder="0"
            value={filters.min_amount}
            onChange={(e) => handleFilterChange('min_amount', e.target.value)}
          />
        </div>
        <div className="mt-4 flex flex-col sm:flex-row gap-2 sm:gap-3">
          <button 
            onClick={handleApplyFilters}
            disabled={loading}
            className="px-4 sm:px-6 py-2.5 sm:py-3 bg-[#3772FE] text-white rounded-xl sm:rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Загрузка...' : 'Применить'}
          </button>
          <button 
            onClick={handleExport}
            disabled={isExporting || data.length === 0}
            className="px-4 sm:px-6 py-2.5 sm:py-3 bg-[#3772FE] text-white rounded-xl sm:rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isExporting ? 'Экспорт...' : 'Экспортировать'}
          </button>
          <button 
            onClick={() => {
              setFilters({
                period_from: '2025-01',
                period_to: '2025-08',
                kcsr_mask: '1',
                budget_name: '',
                fund_source: '',
                min_amount: ''
              });
            }}
            className="px-4 sm:px-6 py-2.5 sm:py-3 bg-[#F4F5F7] text-[#0F172A] rounded-xl sm:rounded-2xl font-bold text-sm hover:bg-[#E4EBF8] transition-all"
          >
            Сбросить
          </button>
        </div>
      </div>

      {exportStatus && (
        <div className={`p-3 sm:p-4 rounded-xl sm:rounded-2xl border ${
          exportStatus.type === 'success' 
            ? 'bg-green-50 border-green-200 text-green-700' 
            : 'bg-red-50 border-red-200 text-red-700'
        } animate-fade-in`}>
          <div className="flex items-center gap-2">
            {exportStatus.type === 'success' ? (
              <svg className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            <span className="font-bold text-xs sm:text-sm">{exportStatus.message}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl sm:rounded-2xl p-3 sm:p-4 text-red-600 text-xs sm:text-sm">
          {error}
        </div>
      )}

      {/* Основные показатели */}
      {data.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
            <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Всего записей</p>
            <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2">{data.length}</h3>
            <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Найдено в системе</p>
          </div>
          <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
            <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Лимиты ПБС</p>
            <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">
              {formatCurrency(data.reduce((sum, item) => sum + parseFloat(item.limit_pbs || 0), 0))}
            </h3>
            <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Общая сумма</p>
          </div>
          <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
            <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Контракты ГЗ</p>
            <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">
              {formatCurrency(data.reduce((sum, item) => sum + parseFloat(item.gz_contracts_amount || 0), 0))}
            </h3>
            <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Сумма контрактов</p>
          </div>
          <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
            <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Оплачено ГЗ</p>
            <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">
              {formatCurrency(data.reduce((sum, item) => sum + parseFloat(item.gz_paid || 0), 0))}
            </h3>
            <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Фактические платежи</p>
          </div>
        </div>
      )}

      {/* Таблица детализации */}
      <div className="bg-white rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8] shadow-sm">
        <h3 className="font-black text-[#0F172A] mb-3 sm:mb-4 text-sm sm:text-base">Детализация по КЦСР</h3>
        {loading ? (
          <div className="text-center py-8 text-[#989FAC] text-sm">Загрузка данных...</div>
        ) : data.length === 0 ? (
          <div className="text-center py-8 text-[#989FAC] text-sm">Нет данных для отображения</div>
        ) : (
          <div className="overflow-x-auto -mx-4 sm:mx-0">
            <table className="w-full min-w-[800px]">
              <thead>
                <tr className="border-b border-[#F4F5F7]">
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest">КЦСР</th>
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest">Наименование</th>
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest hidden lg:table-cell">Бюджет</th>
                  <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest hidden md:table-cell">Период</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest">Лимит ПБС</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest hidden sm:table-cell">Контракты ГЗ</th>
                  <th className="text-right py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs font-black text-[#989FAC] uppercase tracking-widest">Оплачено</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, idx) => (
                  <>
                    <tr 
                      key={idx} 
                      className="border-b border-[#F4F5F7] hover:bg-[#F4F5F7]/50 transition-colors cursor-pointer"
                      onClick={() => setSelectedRow(selectedRow === idx ? null : idx)}
                    >
                      <td className="py-2 sm:py-3 px-2 sm:px-4 font-mono text-[10px] sm:text-xs text-[#3772FE] font-bold">
                        <div className="flex items-center gap-1 sm:gap-2">
                          {(row.gz_contract_details?.length > 0 || row.gz_payment_details?.length > 0) && (
                            <svg 
                              className={`w-3 h-3 sm:w-4 sm:h-4 transition-transform flex-shrink-0 ${selectedRow === idx ? 'rotate-90' : ''}`} 
                              fill="none" 
                              stroke="currentColor" 
                              viewBox="0 0 24 24"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          )}
                          <span className="break-all">{row.kcsr_code}</span>
                        </div>
                      </td>
                      <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-semibold text-[#0F172A] max-w-[150px] sm:max-w-md truncate" title={row.kcsr_name}>
                        {row.kcsr_name}
                      </td>
                      <td className="py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs text-[#0F172A] hidden lg:table-cell">{row.budget_name}</td>
                      <td className="py-2 sm:py-3 px-2 sm:px-4 text-[10px] sm:text-xs text-[#989FAC] hidden md:table-cell">{formatPeriod(row.budget_period)}</td>
                      <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-bold text-[#0F172A] text-right">
                        {formatCurrency(row.limit_pbs)}
                      </td>
                      <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-bold text-[#0F172A] text-right hidden sm:table-cell">
                        {formatCurrency(row.gz_contracts_amount)}
                      </td>
                      <td className="py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-bold text-[#31B96A] text-right">
                        {formatCurrency(row.gz_paid)}
                      </td>
                    </tr>
                    
                    {/* Детали контрактов и платежей */}
                    {selectedRow === idx && (row.gz_contract_details?.length > 0 || row.gz_payment_details?.length > 0) && (
                      <tr>
                        <td colSpan="7" className="bg-[#F9FBFF] p-3 sm:p-6">
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                            {/* Контракты */}
                            {row.gz_contract_details?.length > 0 && (
                              <div>
                                <h4 className="font-black text-[#0F172A] mb-2 sm:mb-3 text-xs sm:text-sm">
                                  Контракты ГЗ ({row.gz_contract_details.length})
                                </h4>
                                <div className="space-y-2 sm:space-y-3">
                                  {row.gz_contract_details.map((contract, cIdx) => (
                                    <div key={cIdx} className="bg-white rounded-lg sm:rounded-xl p-3 sm:p-4 border border-[#E4EBF8]">
                                      <div className="grid grid-cols-2 gap-2 sm:gap-3 text-[10px] sm:text-xs">
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Номер:</span>
                                          <p className="text-[#0F172A] font-bold mt-1 break-all">{contract.number}</p>
                                        </div>
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Дата:</span>
                                          <p className="text-[#0F172A] font-bold mt-1">{contract.date}</p>
                                        </div>
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Сумма:</span>
                                          <p className="text-[#3772FE] font-black mt-1 break-all">{formatCurrency(contract.amount)}</p>
                                        </div>
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Контрагент:</span>
                                          <p className="text-[#0F172A] font-mono text-[9px] sm:text-[10px] mt-1 break-all">{contract.counterparty}</p>
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Платежи */}
                            {row.gz_payment_details?.length > 0 && (
                              <div>
                                <h4 className="font-black text-[#0F172A] mb-2 sm:mb-3 text-xs sm:text-sm">
                                  Платежи ГЗ ({row.gz_payment_details.length})
                                </h4>
                                <div className="space-y-2 sm:space-y-3">
                                  {row.gz_payment_details.map((payment, pIdx) => (
                                    <div key={pIdx} className="bg-white rounded-lg sm:rounded-xl p-3 sm:p-4 border border-[#E4EBF8]">
                                      <div className="grid grid-cols-2 gap-2 sm:gap-3 text-[10px] sm:text-xs">
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Номер:</span>
                                          <p className="text-[#0F172A] font-bold mt-1 break-all">{payment.number}</p>
                                        </div>
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Дата:</span>
                                          <p className="text-[#0F172A] font-bold mt-1">{payment.date}</p>
                                        </div>
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Сумма:</span>
                                          <p className="text-[#31B96A] font-black mt-1 break-all">{formatCurrency(payment.amount)}</p>
                                        </div>
                                        <div>
                                          <span className="text-[#989FAC] font-bold uppercase tracking-wider">Ключ платежа:</span>
                                          <p className="text-[#0F172A] font-mono text-[9px] sm:text-[10px] mt-1 break-all">{payment.payment_key}</p>
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
