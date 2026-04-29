const MetricCard = ({ label, value, trend, isPositive }) => (
  <div className="bg-gradient-to-b from-white to-[#F9FBFF] p-6 rounded-[2rem] border border-[#E4EBF8] shadow-sm hover:shadow-md transition-all">
    <p className="text-[#989FAC] text-xs font-bold uppercase tracking-widest mb-3">{label}</p>
    <div className="flex items-end justify-between">
      <h3 className="text-2xl font-black text-[#0F172A]">{value}</h3>
      <div className={`text-xs font-bold px-2 py-1 rounded-lg ${
        isPositive ? 'bg-[#EEF3FF] text-[#3772FE]' : 'bg-red-50 text-[#EF5C4F]'
      }`}>
        {trend}
      </div>
    </div>
  </div>
);

export default function MetricsGrid({ metrics }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {metrics.map((metric, idx) => (
        <MetricCard key={idx} {...metric} />
      ))}
    </div>
  );
}
