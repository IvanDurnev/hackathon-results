export default function PreviewTable({ data, recordCount = 124 }) {
  return (
    <div className="col-span-8 bg-[#F4F5F7]/50 rounded-[2rem] p-6 border border-[#E4EBF8]">
      <div className="flex items-center justify-between mb-6 px-2">
        <span className="text-[11px] font-black text-[#989FAC] uppercase tracking-widest">
          Предварительный просмотр
        </span>
        <span className="text-xs font-bold text-[#3772FE] bg-white px-3 py-1 rounded-full shadow-sm">
          {recordCount} записи
        </span>
      </div>
      
      <div className="space-y-3">
        {data.map((item) => (
          <div 
            key={item.id} 
            className="bg-white p-4 rounded-2xl shadow-sm flex items-center justify-between border border-[#E2E8F0]/50 transition-transform hover:scale-[1.01]"
          >
            <div className="flex items-center space-x-4">
              <div className="w-2 h-10 bg-[#3772FE] rounded-full opacity-20"></div>
              <div>
                <p className="text-xs font-black text-[#0F172A]">{item.kbk}</p>
                <p className="text-[11px] text-[#989FAC] font-bold uppercase tracking-tighter">
                  {item.project}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-black text-[#0F172A]">{item.amount}</p>
              <p className="text-[10px] text-[#31B96A] font-bold">{item.status}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
