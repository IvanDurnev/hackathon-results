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
    <section className="py-24 bg-white">
      <div className="container mx-auto px-6">
        <h2 className="text-3xl font-bold text-center mb-16 text-slate-900">Инструменты для профессионалов</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <div key={i} className="p-8 rounded-2xl border border-slate-100 bg-slate-50 hover:shadow-xl transition-shadow group">
              <div className="w-12 h-12 bg-blue-600 rounded-lg mb-6 flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">
                {i + 1}
              </div>
              <h3 className="text-xl font-bold mb-4">{f.title}</h3>
              <p className="text-slate-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}