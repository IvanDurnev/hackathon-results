export default function Preview() {
  return (
    <section className="py-12">
      <div className="container mx-auto px-6">
        <div className="bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden">
          <div className="bg-slate-900 px-6 py-3 flex items-center justify-between">
            <div className="flex space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <div className="text-xs text-slate-400 font-mono tracking-widest uppercase">Рабочая область конструктора</div>
          </div>
          <div className="p-8 lg:p-12">
            <div className="grid grid-cols-12 gap-6">
              {/* Sidebar Mockup */}
              <div className="col-span-3 space-y-6">
                <div className="space-y-2">
                  <div className="h-2 w-20 bg-slate-100 rounded"></div>
                  <div className="h-10 w-full border border-slate-200 rounded-md"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-2 w-24 bg-slate-100 rounded"></div>
                  <div className="h-32 w-full border border-slate-200 rounded-md border-dashed flex items-center justify-center">
                    <div className="text-[10px] text-slate-400">Фильтры КЦСР / КВР</div>
                  </div>
                </div>
              </div>
              {/* Data Table Mockup */}
              <div className="col-span-9">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="pb-4 font-semibold text-slate-400">КБК</th>
                        <th className="pb-4 font-semibold text-slate-400">Лимит (РЧB)</th>
                        <th className="pb-4 font-semibold text-slate-400">Выбытия</th>
                        <th className="pb-4 font-semibold text-slate-400">Исполнение</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {[1, 2, 3, 4].map((i) => (
                        <tr key={i}>
                          <td className="py-4 font-mono text-xs text-blue-600">000 0000 0000000 {i}00</td>
                          <td className="py-4 font-medium">124 500 000 ₽</td>
                          <td className="py-4">112 000 000 ₽</td>
                          <td className="py-4">
                            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                              <div className="bg-blue-500 h-full w-[85%]"></div>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}