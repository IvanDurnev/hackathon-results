import Button from '../ui/Button';
import Select from '../ui/Select';
import RadioGroup from '../ui/RadioGroup';
import PreviewTable from './PreviewTable';
import { DEPARTMENTS, MERGE_METHODS } from '../../constants/dashboard';
import { previewData } from '../../data/mockData';

export default function WorkspacePanel() {
  return (
    <div className="bg-white rounded-[1.5rem] sm:rounded-[2.5rem] shadow-sm border border-[#E4EBF8] overflow-hidden">
      <div className="p-4 sm:p-8 border-b border-[#F4F5F7] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        <h3 className="font-black text-[#0F172A] text-base sm:text-lg">Параметры формирования данных</h3>
        <Button>Сгенерировать отчет</Button>
      </div>

      <div className="p-4 sm:p-8 grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-8">
        {/* Левая часть - Фильтры */}
        <div className="col-span-1 lg:col-span-4 space-y-4 sm:space-y-6">
          <Select label="Ведомство" options={DEPARTMENTS} />
          <RadioGroup label="Метод склейки" options={MERGE_METHODS} defaultValue={MERGE_METHODS[0]} />
        </div>

        {/* Правая часть - Таблица (Preview) */}
        <PreviewTable data={previewData} />
      </div>
    </div>
  );
}
