export default function PreviewTable({ data, recordCount = 124 }) {
  return (
    <div className="col-span-1 lg:col-span-8 bg-[#F4F5F7]/50 rounded-[1.5rem] sm:rounded-[2rem] p-4 sm:p-6 border border-[#E4EBF8]">
      <div className="flex items-center justify-between mb-4 sm:mb-6 px-1 sm:px-2">
        <span className="text-[10px] sm:text-[11px] font-black text-[#989FAC] uppercase tracking-widest">
          Предварительный просмотр
        </span>
        <span className="text-[10px] sm:text-xs font-bold text-[#3772FE] bg-white px-2 py-1 sm:px-3 sm:py-1 rounded-full shadow-sm">
          {recordCount} записи
        </span>
      </div>
      
      <div className="space-y-2 sm:space-y-3">
        {data.map((item) => (
          <div 
            key={item.id} 
            className="bg-white p-3 sm:p-4 rounded-xl sm:rounded-2xl shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between border border-[#E2E8F0]/50 transition-transform hover:scale-[1.01] gap-2 sm:gap-0"
          >
            <div className="flex items-center space-x-3 sm:space-x-4 w-full sm:w-auto">
              <div className="w-2 h-8 sm:h-10 bg-[#3772FE] rounded-full opacity-20 flex-shrink-0"></div>
              <div className="min-w-0 flex-1">
                <p className="text-xs sm:text-xs font-black text-[#0F172A] break-all">{item.kbk}</p>
                <p className="text-[10px] sm:text-[11px] text-[#989FAC] font-bold uppercase tracking-tighter truncate">
                  {item.project}
                </p>
              </div>
            </div>
            <div className="text-left sm:text-right w-full sm:w-auto pl-5 sm:pl-0">
              <p className="font-black text-[#0F172A] text-sm sm:text-base">{item.amount}</p>
              <p className="text-[10px] sm:text-[10px] text-[#31B96A] font-bold">{item.status}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
