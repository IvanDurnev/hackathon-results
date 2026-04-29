import Select from '../components/ui/Select';
import Input from '../components/ui/Input';
import { PdfIcon, ExcelIcon, WordIcon } from '../components/icons';

export default function Documents() {
  const documents = [
    { 
      title: 'Отчет об исполнении бюджета Q1 2026', 
      type: 'PDF', 
      size: '2.4 МБ', 
      date: '15.04.2026',
      status: 'Утвержден'
    },
    { 
      title: 'Сводная таблица КБК за март 2026', 
      type: 'XLSX', 
      size: '1.8 МБ', 
      date: '01.04.2026',
      status: 'Утвержден'
    },
    { 
      title: 'Аналитическая записка по доходам', 
      type: 'DOCX', 
      size: '856 КБ', 
      date: '28.03.2026',
      status: 'На проверке'
    },
    { 
      title: 'План-график финансирования 2026', 
      type: 'PDF', 
      size: '3.1 МБ', 
      date: '15.03.2026',
      status: 'Утвержден'
    },
    { 
      title: 'Реестр получателей бюджетных средств', 
      type: 'XLSX', 
      size: '4.2 МБ', 
      date: '10.03.2026',
      status: 'Утвержден'
    },
    { 
      title: 'Методические рекомендации по КБК', 
      type: 'PDF', 
      size: '1.2 МБ', 
      date: '01.03.2026',
      status: 'Утвержден'
    }
  ];

  const getFileIcon = (type) => {
    const icons = {
      PDF: <PdfIcon />,
      XLSX: <ExcelIcon />,
      DOCX: <WordIcon />
    };
    return icons[type] || <PdfIcon />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-[#0F172A] mb-2">Документы</h2>
          <p className="text-[#989FAC] text-sm">Отчеты, таблицы и нормативные документы</p>
        </div>
        <button className="px-6 py-3 bg-[#3772FE] text-white rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all">
          Загрузить документ
        </button>
      </div>

      {/* Фильтры */}
      <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Select 
            label="Тип документа" 
            options={['Все типы', 'PDF', 'XLSX', 'DOCX']} 
          />
          <Select 
            label="Статус" 
            options={['Все статусы', 'Утвержден', 'На проверке', 'Черновик']} 
          />
          <Select 
            label="Период" 
            options={['2026 год', '2025 год', '2024 год']} 
          />
          <div>
            <label className="text-[11px] font-black text-[#989FAC] uppercase tracking-widest ml-2 mb-2 block">Поиск</label>
            <Input placeholder="Название документа..." />
          </div>
        </div>
      </div>

      {/* Список документов */}
      <div className="bg-white rounded-[2rem] p-6 border border-[#E4EBF8] shadow-sm">
        <div className="space-y-3">
          {documents.map((doc, idx) => (
            <div 
              key={idx}
              className="flex items-center justify-between p-5 rounded-2xl border border-[#E4EBF8] hover:border-[#3772FE]/30 hover:shadow-md transition-all group cursor-pointer"
            >
              <div className="flex items-center space-x-4 flex-1">
                <div className="w-12 h-12 bg-[#EEF3FF] rounded-2xl flex items-center justify-center text-[#3772FE] group-hover:scale-110 transition-transform">
                  {getFileIcon(doc.type)}
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-black text-[#0F172A] mb-1">{doc.title}</h4>
                  <div className="flex items-center space-x-3 text-xs text-[#989FAC] font-bold">
                    <span>{doc.type}</span>
                    <span className="w-1 h-1 bg-[#989FAC] rounded-full"></span>
                    <span>{doc.size}</span>
                    <span className="w-1 h-1 bg-[#989FAC] rounded-full"></span>
                    <span>{doc.date}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`text-xs font-bold px-3 py-1.5 rounded-full ${
                  doc.status === 'Утвержден' 
                    ? 'bg-[#EEF3FF] text-[#3772FE]' 
                    : 'bg-yellow-50 text-yellow-600'
                }`}>
                  {doc.status}
                </span>
                <button className="w-10 h-10 bg-[#F4F5F7] rounded-xl flex items-center justify-center text-[#989FAC] hover:text-[#3772FE] hover:bg-[#EEF3FF] transition-all">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Всего документов', value: '248' },
          { label: 'Загружено в этом месяце', value: '32' },
          { label: 'На проверке', value: '8' },
          { label: 'Общий размер', value: '1.2 ГБ' }
        ].map((stat, idx) => (
          <div key={idx} className="bg-gradient-to-b from-white to-[#F9FBFF] p-5 rounded-[2rem] border border-[#E4EBF8] shadow-sm">
            <p className="text-[#989FAC] text-xs font-bold uppercase tracking-widest mb-2">{stat.label}</p>
            <h3 className="text-2xl font-black text-[#0F172A]">{stat.value}</h3>
          </div>
        ))}
      </div>
    </div>
  );
}
