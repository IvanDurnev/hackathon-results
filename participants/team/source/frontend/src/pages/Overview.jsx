import MetricsGrid from '../components/dashboard/MetricsGrid';
import { METRICS_DATA } from '../constants/dashboard';

export default function Overview() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-[#0F172A] mb-2">Обзор бюджета</h2>
        <p className="text-[#989FAC] text-sm">Общая информация о состоянии бюджета Амурской области</p>
      </div>

      <MetricsGrid metrics={METRICS_DATA} />

      {/* Графики и диаграммы */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* График исполнения бюджета */}
        <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
          <h3 className="font-black text-[#0F172A] mb-4">Исполнение бюджета по месяцам</h3>
          <div className="h-64 flex items-end justify-between gap-2">
            {[65, 72, 68, 85, 78, 82, 88, 75, 90, 85, 92, 88].map((height, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className="w-full bg-gradient-to-t from-[#3772FE] to-[#A3C0FF] rounded-lg transition-all hover:opacity-80"
                  style={{ height: `${height}%` }}
                ></div>
                <span className="text-[10px] text-[#989FAC] font-bold">{idx + 1}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Распределение по ведомствам */}
        <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
          <h3 className="font-black text-[#0F172A] mb-4">Распределение по ведомствам</h3>
          <div className="space-y-4">
            {[
              { name: 'Министерство образования', percent: 35, color: '#3772FE' },
              { name: 'Минздрав АО', percent: 28, color: '#A3C0FF' },
              { name: 'Минстрой АО', percent: 22, color: '#EEF3FF' },
              { name: 'Прочие', percent: 15, color: '#F4F5F7' }
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-bold text-[#0F172A]">{item.name}</span>
                  <span className="text-sm font-black text-[#3772FE]">{item.percent}%</span>
                </div>
                <div className="w-full bg-[#F4F5F7] h-2 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all"
                    style={{ width: `${item.percent}%`, backgroundColor: item.color }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Последние операции */}
      <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
        <h3 className="font-black text-[#0F172A] mb-4">Последние операции</h3>
        <div className="space-y-3">
          {[
            { title: 'Утверждение лимитов', dept: 'Минобразования', date: '28.04.2026', status: 'Завершено' },
            { title: 'Корректировка КБК', dept: 'Минздрав АО', date: '27.04.2026', status: 'В работе' },
            { title: 'Формирование отчета', dept: 'Минстрой АО', date: '27.04.2026', status: 'Завершено' },
            { title: 'Проверка данных', dept: 'Минфин АО', date: '26.04.2026', status: 'Завершено' }
          ].map((op, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 rounded-xl border border-[#E4EBF8] hover:border-[#3772FE]/30 transition-all">
              <div className="flex items-center space-x-4">
                <div className="w-2 h-12 bg-[#3772FE] rounded-full opacity-20"></div>
                <div>
                  <p className="text-sm font-black text-[#0F172A]">{op.title}</p>
                  <p className="text-xs text-[#989FAC] font-bold">{op.dept} • {op.date}</p>
                </div>
              </div>
              <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                op.status === 'Завершено' 
                  ? 'bg-[#EEF3FF] text-[#3772FE]' 
                  : 'bg-yellow-50 text-yellow-600'
              }`}>
                {op.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
