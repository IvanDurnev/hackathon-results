import Select from '../components/ui/Select';

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-[#0F172A] mb-2">Аналитика</h2>
        <p className="text-[#989FAC] text-sm">Детальный анализ бюджетных данных и трендов</p>
      </div>

      {/* Фильтры */}
      <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Select 
            label="Период" 
            options={['2026 год', '2025 год', '2024 год']} 
          />
          <Select 
            label="Квартал" 
            options={['Q2 2026', 'Q1 2026', 'Q4 2025']} 
          />
          <Select 
            label="Ведомство" 
            options={['Все ведомства', 'Минобразования', 'Минздрав АО']} 
          />
          <div className="flex items-end">
            <button className="w-full px-6 py-3 bg-[#3772FE] text-white rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all">
              Применить
            </button>
          </div>
        </div>
      </div>

      {/* Основные показатели */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Средний темп роста', value: '+4.2%', trend: 'За последний год' },
          { label: 'Эффективность расходов', value: '87.5%', trend: 'Выше плана на 2.5%' },
          { label: 'Отклонение от плана', value: '-1.2%', trend: 'В пределах нормы' }
        ].map((metric, idx) => (
          <div key={idx} className="bg-gradient-to-b from-white to-[#F9FBFF] p-6 rounded-[2rem] border border-[#E4EBF8] shadow-sm">
            <p className="text-[#989FAC] text-xs font-bold uppercase tracking-widest mb-3">{metric.label}</p>
            <h3 className="text-3xl font-black text-[#0F172A] mb-2">{metric.value}</h3>
            <p className="text-xs text-[#3772FE] font-bold">{metric.trend}</p>
          </div>
        ))}
      </div>

      {/* Графики */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Динамика доходов и расходов */}
        <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
          <h3 className="font-black text-[#0F172A] mb-6">Динамика доходов и расходов</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-bold text-[#0F172A]">Доходы</span>
                <span className="text-sm font-black text-[#31B96A]">84.2 млрд ₽</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-3 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-[#31B96A] to-[#5DD39E] rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-bold text-[#0F172A]">Расходы</span>
                <span className="text-sm font-black text-[#3772FE]">72.1 млрд ₽</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-3 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-[#3772FE] to-[#A3C0FF] rounded-full" style={{ width: '73%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-bold text-[#0F172A]">Профицит</span>
                <span className="text-sm font-black text-[#3772FE]">12.1 млрд ₽</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-3 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-[#3772FE] to-[#A3C0FF] rounded-full" style={{ width: '12%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Топ-5 статей расходов */}
        <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
          <h3 className="font-black text-[#0F172A] mb-6">Топ-5 статей расходов</h3>
          <div className="space-y-4">
            {[
              { name: 'Образование', amount: '28.5 млрд ₽', percent: 39 },
              { name: 'Здравоохранение', amount: '21.2 млрд ₽', percent: 29 },
              { name: 'Социальная политика', amount: '12.8 млрд ₽', percent: 18 },
              { name: 'ЖКХ', amount: '6.4 млрд ₽', percent: 9 },
              { name: 'Культура', amount: '3.2 млрд ₽', percent: 5 }
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="w-8 h-8 bg-[#EEF3FF] rounded-xl flex items-center justify-center">
                    <span className="text-xs font-black text-[#3772FE]">{idx + 1}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-bold text-[#0F172A]">{item.name}</p>
                    <div className="w-full bg-[#F4F5F7] h-1.5 rounded-full overflow-hidden mt-1">
                      <div 
                        className="h-full bg-[#3772FE] rounded-full"
                        style={{ width: `${item.percent}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                <span className="text-sm font-black text-[#0F172A] ml-4">{item.amount}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Таблица детализации */}
      <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
        <h3 className="font-black text-[#0F172A] mb-4">Детализация по КБК</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#F4F5F7]">
                <th className="text-left py-3 px-4 text-xs font-black text-[#989FAC] uppercase tracking-widest">КБК</th>
                <th className="text-left py-3 px-4 text-xs font-black text-[#989FAC] uppercase tracking-widest">Наименование</th>
                <th className="text-right py-3 px-4 text-xs font-black text-[#989FAC] uppercase tracking-widest">План</th>
                <th className="text-right py-3 px-4 text-xs font-black text-[#989FAC] uppercase tracking-widest">Факт</th>
                <th className="text-right py-3 px-4 text-xs font-black text-[#989FAC] uppercase tracking-widest">%</th>
              </tr>
            </thead>
            <tbody>
              {[
                { kbk: '01.03.450.99', name: 'Нацпроект: Жилье и среда', plan: '5.2 млн', fact: '4.8 млн', percent: 92 },
                { kbk: '02.04.320.15', name: 'Образовательные программы', plan: '12.5 млн', fact: '11.2 млн', percent: 90 },
                { kbk: '03.02.110.88', name: 'Медицинское оборудование', plan: '8.1 млн', fact: '7.9 млн', percent: 98 },
                { kbk: '04.01.250.42', name: 'Социальные выплаты', plan: '15.3 млн', fact: '15.1 млн', percent: 99 }
              ].map((row, idx) => (
                <tr key={idx} className="border-b border-[#F4F5F7] hover:bg-[#F4F5F7]/50 transition-colors">
                  <td className="py-3 px-4 font-mono text-xs text-[#3772FE] font-bold">{row.kbk}</td>
                  <td className="py-3 px-4 text-sm font-semibold text-[#0F172A]">{row.name}</td>
                  <td className="py-3 px-4 text-sm font-bold text-[#0F172A] text-right">{row.plan}</td>
                  <td className="py-3 px-4 text-sm font-bold text-[#0F172A] text-right">{row.fact}</td>
                  <td className="py-3 px-4 text-right">
                    <span className={`text-xs font-bold px-2 py-1 rounded-lg ${
                      row.percent >= 95 ? 'bg-[#EEF3FF] text-[#3772FE]' : 'bg-yellow-50 text-yellow-600'
                    }`}>
                      {row.percent}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
