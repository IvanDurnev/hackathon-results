const features = [
  {
    title: "Сквозная кодировка",
    desc: "Автоматическое объединение данных по иерархическим кодам без участия пользователя."
  },
  {
    title: "Экспорт отчетности",
    desc: "Формирование готовых Excel-таблиц, соответствующих стандартам отчетности Минфина."
  },
  {
    title: "Интеллектуальный поиск",
    desc: "Система подсказок при вводе КЦСР и автоматическое определение типа бюджета."
  }
];

export default function Features() {
  return (
    <section className="py-12 sm:py-16 lg:py-24 bg-white">
      <div className="container mx-auto px-4 sm:px-6">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8 sm:mb-12 lg:mb-16 text-slate-900">Инструменты для профессионалов</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          {features.map((f, i) => (
            <div key={i} className="p-6 sm:p-8 rounded-2xl border border-slate-100 bg-slate-50 hover:shadow-xl transition-shadow group">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-600 rounded-lg mb-4 sm:mb-6 flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform text-sm sm:text-base">
                {i + 1}
              </div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 sm:mb-4">{f.title}</h3>
              <p className="text-sm sm:text-base text-slate-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}