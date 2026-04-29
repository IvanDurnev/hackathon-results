const SidebarLink = ({ label, active = false, icon, onClick }) => (
  <div 
    onClick={onClick}
    className={`flex items-center space-x-3 px-5 py-3.5 rounded-2xl cursor-pointer transition-all duration-300 ${
      active 
      ? 'bg-[#3772FE] text-white shadow-lg shadow-blue-500/25 scale-[1.02]' 
      : 'text-[#989FAC] hover:bg-[#F4F5F7] hover:text-[#3772FE]'
    }`}
  >
    <div className="w-5 h-5">{icon}</div>
    <span className="text-sm font-semibold">{label}</span>
  </div>
);

export default function Sidebar({ links }) {
  return (
    <aside className="w-72 bg-white rounded-[2.5rem] flex flex-col p-6 shadow-sm border border-[#E4EBF8]">
      <div className="flex items-center space-x-3 mb-12 px-2 pt-2">
        <img src="/logo.svg" alt="АМУР.БЮДЖЕТ" className="w-10 h-10" />
        <span className="font-black tracking-tighter text-xl text-[#0F172A]">АМУР.БЮДЖЕТ</span>
      </div>

      <nav className="flex-1 space-y-2">
        {links.map((link, idx) => (
          <SidebarLink key={idx} {...link} />
        ))}
      </nav>

      {/* Статус систем */}
      <div className="mt-8 mb-6 space-y-3">
        <p className="text-[10px] font-black text-[#989FAC] uppercase tracking-widest px-2">Статус систем</p>
        <div className="space-y-2">
          {[
            { name: 'АЦК-Финансы', status: 'online' },
            { name: 'Хранилище данных', status: 'online' },
            { name: 'API Сервис', status: 'online' }
          ].map((system, idx) => (
            <div key={idx} className="flex items-center justify-between px-3 py-2 rounded-xl bg-[#F4F5F7] hover:bg-[#EEF3FF] transition-colors">
              <span className="text-xs font-semibold text-[#0F172A]">{system.name}</span>
              <div className="flex items-center space-x-1.5">
                <div className={`w-2 h-2 rounded-full ${system.status === 'online' ? 'bg-[#31B96A]' : 'bg-[#EF5C4F]'}`}></div>
                <span className="text-[10px] font-bold text-[#989FAC]">{system.status === 'online' ? 'OK' : 'Ошибка'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Нижний блок */}
      <div className="mt-auto pt-6 border-t border-[#E4EBF8] space-y-4">
        {/* Информация о системе */}
        <div className="bg-[#F4F5F7] rounded-2xl p-4">
          <p className="text-[10px] font-black text-[#989FAC] uppercase tracking-widest mb-2">Система</p>
          <p className="text-sm font-bold text-[#0F172A] mb-1">АМУР.БЮДЖЕТ</p>
          <p className="text-[10px] text-[#989FAC] font-medium">v1.0.0</p>
        </div>

        {/* Кнопки действий */}
        <div className="grid grid-cols-2 gap-2">
          <button className="flex items-center justify-center space-x-2 px-3 py-2.5 bg-white rounded-xl border border-[#E4EBF8] text-[#989FAC] hover:text-[#3772FE] hover:border-[#3772FE]/30 transition-all text-xs font-bold">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-4 h-4">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Справка</span>
          </button>
          <button className="flex items-center justify-center space-x-2 px-3 py-2.5 bg-white rounded-xl border border-[#E4EBF8] text-[#989FAC] hover:text-[#3772FE] hover:border-[#3772FE]/30 transition-all text-xs font-bold">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-4 h-4">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>Настройки</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
