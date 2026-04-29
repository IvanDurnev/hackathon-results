const stats = [
  { value: "84.2 млрд ₽", label: "Объем бюджета АО" },
  { value: "12", label: "Ведомств в системе" },
  { value: "99.2%", label: "Точность данных" }
];

export default function Stats() {
  return (
    <section className="py-16 bg-slate-50">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">{stat.value}</div>
              <div className="text-slate-600">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
