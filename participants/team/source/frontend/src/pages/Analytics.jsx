import { useEffect } from 'react';
import { formatCurrency } from '../services/api';
import { useFilters } from '../context/FiltersContext';

export default function Analytics() {
  const { data, filters } = useFilters();

  // Вычисление метрик
  const totalLimits = data.reduce((sum, item) => sum + parseFloat(item.limit_pbs || 0), 0);
  const totalContracts = data.reduce((sum, item) => sum + parseFloat(item.gz_contracts_amount || 0), 0);
  const totalPaid = data.reduce((sum, item) => sum + parseFloat(item.gz_paid || 0), 0);
  const totalObligations = data.reduce((sum, item) => sum + parseFloat(item.budget_obligations || 0), 0);

  // Группировка по источникам финансирования
  const byFundSource = data.reduce((acc, item) => {
    const source = item.fund_source || 'Не указано';
    if (!acc[source]) acc[source] = 0;
    acc[source] += parseFloat(item.limit_pbs || 0);
    return acc;
  }, {});

  // Вычисляем точные проценты с одним знаком после запятой
  const fundSourceData = Object.entries(byFundSource)
    .map(([name, amount]) => ({
      name,
      amount,
      percent: totalLimits > 0 ? (amount / totalLimits) * 100 : 0
    }))
    .sort((a, b) => b.amount - a.amount);

  // Корректируем проценты чтобы сумма была ровно 100%
  if (fundSourceData.length > 0) {
    const totalPercent = fundSourceData.reduce((sum, item) => sum + Math.round(item.percent * 10) / 10, 0);
    if (totalPercent !== 100 && totalPercent > 0) {
      // Добавляем разницу к самому большому элементу
      const diff = 100 - totalPercent;
      fundSourceData[0].percent += diff;
    }
  }

  // Группировка по бюджетам
  const byBudget = data.reduce((acc, item) => {
    const budget = item.budget_name || 'Не указано';
    if (!acc[budget]) acc[budget] = 0;
    acc[budget] += parseFloat(item.limit_pbs || 0);
    return acc;
  }, {});

  const budgetData = Object.entries(byBudget)
    .map(([name, amount]) => ({
      name,
      amount,
      percent: totalLimits > 0 ? Math.round((amount / totalLimits) * 100) : 0
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 4);

  // Группировка по периодам для графика
  const byPeriod = data.reduce((acc, item) => {
    const period = item.budget_period;
    if (!acc[period]) acc[period] = 0;
    acc[period] += parseFloat(item.gz_paid || 0);
    return acc;
  }, {});

  const periodData = Object.entries(byPeriod)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(0, 12);

  const maxPeriodValue = Math.max(...periodData.map(([, value]) => value), 1);

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 sm:h-64 bg-white rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] mx-2 sm:mx-0">
        <div className="text-[#989FAC] text-base sm:text-lg mb-2">Нет данных для отображения</div>
        <div className="text-[#989FAC] text-xs sm:text-sm text-center px-4">Перейдите на страницу "Конструктор" и примените фильтры</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Метрики */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
          <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Лимиты ПБС</p>
          <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">{formatCurrency(totalLimits)}</h3>
          <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Общая сумма</p>
        </div>
        <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
          <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Контракты ГЗ</p>
          <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">{formatCurrency(totalContracts)}</h3>
          <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Сумма контрактов</p>
        </div>
        <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
          <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Оплачено ГЗ</p>
          <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">{formatCurrency(totalPaid)}</h3>
          <p className="text-[10px] sm:text-xs text-[#31B96A] font-bold">Фактические платежи</p>
        </div>
        <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border border-[#E4EBF8] shadow-sm">
          <p className="text-[#989FAC] text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-2 sm:mb-3">Бюджетные обязательства</p>
          <h3 className="text-2xl sm:text-3xl font-black text-[#0F172A] mb-1 sm:mb-2 break-all">{formatCurrency(totalObligations)}</h3>
          <p className="text-[10px] sm:text-xs text-[#3772FE] font-bold">Всего обязательств</p>
        </div>
      </div>

      {/* Графики и диаграммы */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
        {/* График оплат по периодам */}
        <div className="bg-white rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8] shadow-sm">
          <h3 className="font-black text-[#0F172A] mb-3 sm:mb-4 text-sm sm:text-base">Оплаты по периодам</h3>
          <div className="h-48 sm:h-64 relative flex gap-2 sm:gap-3">
            {/* Ось Y с делениями */}
            <div className="flex flex-col justify-between py-4 sm:py-6 pr-1 sm:pr-2 border-r border-[#E4EBF8]">
              {[100, 75, 50, 25, 0].map((percent) => {
                const value = (maxPeriodValue * percent) / 100;
                return (
                  <div key={percent} className="flex items-center gap-1 sm:gap-2">
                    <span className="text-[8px] sm:text-[10px] text-[#989FAC] font-bold whitespace-nowrap">
                      {formatCurrency(value)}
                    </span>
                    <div className="w-1 h-px bg-[#E4EBF8]"></div>
                  </div>
                );
              })}
            </div>
            
            {/* График */}
            <div className="flex-1 relative">
              <div className="absolute inset-0 flex items-end justify-between gap-1 sm:gap-2 pb-4 sm:pb-6">
                {periodData.length > 0 ? (
                  periodData.map(([period, value], idx) => {
                    const height = value > 0 ? Math.max((value / maxPeriodValue) * 100, 3) : 0;
                    const month = period.split('-')[1];
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center gap-1 sm:gap-2 group">
                        {value > 0 ? (
                          <>
                            <div className="relative w-full">
                              <div className="absolute bottom-4 sm:bottom-6 left-1/2 transform -translate-x-1/2 bg-[#0F172A] text-white text-[8px] sm:text-[10px] px-1.5 sm:px-2 py-0.5 sm:py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                                {formatCurrency(value)}
                              </div>
                              <div 
                                className="w-full bg-gradient-to-t from-[#3772FE] to-[#A3C0FF] rounded-lg transition-all hover:opacity-80 cursor-pointer"
                                style={{ height: `${height * 1.5}px` }}
                              ></div>
                            </div>
                            <span className="text-[8px] sm:text-[10px] text-[#989FAC] font-bold">{month}</span>
                          </>
                        ) : (
                          <span className="text-[8px] sm:text-[10px] text-[#989FAC] font-bold">{month}</span>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="w-full flex items-center justify-center text-[#989FAC] text-xs sm:text-sm">Нет данных по периодам</div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Распределение по источникам финансирования */}
        <div className="bg-white rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8] shadow-sm">
          <h3 className="font-black text-[#0F172A] mb-3 sm:mb-4 text-sm sm:text-base">Источники финансирования</h3>
          {fundSourceData.length > 0 ? (
            <div className="h-48 sm:h-64 flex flex-col sm:flex-row gap-4 sm:gap-6 items-center justify-center">
              {/* Круговая диаграмма */}
              <div className="flex-shrink-0">
                <svg width="140" height="140" viewBox="0 0 180 180" className="transform -rotate-90 sm:w-[180px] sm:h-[180px]">
                  {(() => {
                    let currentAngle = 0;
                    const colors = ['#3772FE', '#31B96A', '#FFA726', '#E91E63'];
                    return fundSourceData.map((item, idx) => {
                      const percentage = item.percent;
                      const angle = (percentage / 100) * 360;
                      const radius = 70;
                      const centerX = 90;
                      const centerY = 90;
                      
                      // Вычисляем координаты дуги
                      const startAngle = (currentAngle * Math.PI) / 180;
                      const endAngle = ((currentAngle + angle) * Math.PI) / 180;
                      
                      const x1 = centerX + radius * Math.cos(startAngle);
                      const y1 = centerY + radius * Math.sin(startAngle);
                      const x2 = centerX + radius * Math.cos(endAngle);
                      const y2 = centerY + radius * Math.sin(endAngle);
                      
                      const largeArcFlag = angle > 180 ? 1 : 0;
                      
                      const pathData = [
                        `M ${centerX} ${centerY}`,
                        `L ${x1} ${y1}`,
                        `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                        'Z'
                      ].join(' ');
                      
                      currentAngle += angle;
                      
                      return (
                        <path
                          key={idx}
                          d={pathData}
                          fill={colors[idx % colors.length]}
                          className="hover:opacity-80 transition-opacity cursor-pointer"
                        />
                      );
                    });
                  })()}
                  {/* Белый круг в центре для эффекта "пончика" */}
                  <circle cx="90" cy="90" r="45" fill="white" />
                </svg>
              </div>
              
              {/* Легенда и данные */}
              <div className="flex-1 space-y-2 sm:space-y-3 w-full">
                {fundSourceData.map((item, idx) => {
                  const colors = ['#3772FE', '#31B96A', '#FFA726', '#E91E63'];
                  return (
                    <div key={idx} className="flex items-center gap-2 sm:gap-3">
                      <div 
                        className="w-3 h-3 sm:w-4 sm:h-4 rounded-full flex-shrink-0"
                        style={{ backgroundColor: colors[idx % colors.length] }}
                      ></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs sm:text-sm font-bold text-[#0F172A] truncate pr-2">{item.name}</span>
                          <span className="text-xs sm:text-sm font-black text-[#3772FE] flex-shrink-0">
                            {item.percent.toFixed(1)}%
                          </span>
                        </div>
                        <span className="text-[10px] sm:text-xs text-[#989FAC] break-all">{formatCurrency(item.amount)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 sm:h-48 text-[#989FAC] text-xs sm:text-sm">Нет данных по источникам</div>
          )}
        </div>
      </div>

      {/* Топ бюджетов */}
      <div className="bg-white rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8] shadow-sm">
        <h3 className="font-black text-[#0F172A] mb-3 sm:mb-4 text-sm sm:text-base">Топ бюджетов по лимитам</h3>
        <div className="space-y-2 sm:space-y-3">
          {budgetData.length > 0 ? (
            budgetData.map((budget, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 sm:p-4 rounded-xl border border-[#E4EBF8] hover:border-[#3772FE]/30 transition-all hover:shadow-sm">
                <div className="flex items-center space-x-3 sm:space-x-4 flex-1 min-w-0">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-[#3772FE] to-[#A3C0FF] rounded-xl flex items-center justify-center flex-shrink-0">
                    <span className="text-xs sm:text-sm font-black text-white">{idx + 1}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs sm:text-sm font-black text-[#0F172A] truncate mb-1 sm:mb-2" title={budget.name}>
                      {budget.name}
                    </p>
                    <div className="flex items-center gap-2 sm:gap-3">
                      <div className="flex-1 bg-[#F4F5F7] h-1.5 sm:h-2 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-[#3772FE] to-[#A3C0FF] rounded-full transition-all"
                          style={{ width: `${Math.max(budget.percent, 2)}%` }}
                        ></div>
                      </div>
                      <span className="text-[10px] sm:text-xs font-bold text-[#989FAC] flex-shrink-0">{budget.percent}%</span>
                    </div>
                  </div>
                </div>
                <span className="text-xs sm:text-sm font-black text-[#0F172A] ml-3 sm:ml-4 flex-shrink-0 break-all">{formatCurrency(budget.amount)}</span>
              </div>
            ))
          ) : (
            <div className="text-center text-[#989FAC] text-xs sm:text-sm py-6 sm:py-8">Нет данных по бюджетам</div>
          )}
        </div>
      </div>
    </div>
  );
}
