import Button from '../ui/Button';
import Select from '../ui/Select';
import RadioGroup from '../ui/RadioGroup';
import PreviewTable from './PreviewTable';
import { DEPARTMENTS, MERGE_METHODS } from '../../constants/dashboard';
import { previewData } from '../../data/mockData';

export default function WorkspacePanel() {
  return (
    <div className="bg-white rounded-[2.5rem] shadow-sm border border-[#E4EBF8] overflow-hidden">
      <div className="p-8 border-b border-[#F4F5F7] flex items-center justify-between">
        <h3 className="font-black text-[#0F172A] text-lg">Параметры формирования данных</h3>
        <Button>Сгенерировать отчет</Button>
      </div>

      <div className="p-8 grid grid-cols-12 gap-8">
        {/* Левая часть - Фильтры */}
        <div className="col-span-4 space-y-6">
          <Select label="Ведомство" options={DEPARTMENTS} />
          <RadioGroup label="Метод склейки" options={MERGE_METHODS} defaultValue={MERGE_METHODS[0]} />
        </div>

        {/* Правая часть - Таблица (Preview) */}
        <PreviewTable data={previewData} />
      </div>
    </div>
  );
}
