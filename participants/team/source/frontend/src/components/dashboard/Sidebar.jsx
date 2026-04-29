const SidebarLink = ({ label, active = false, icon, onClick }) => (
  <div 
    onClick={onClick}
    className={`flex items-center space-x-3 px-5 py-3.5 rounded-2xl cursor-pointer transition-all duration-300 ${
      active 
      ? 'bg-[#3772FE] text-white shadow-lg shadow-blue-500/25 scale-[1.02]' 
      : 'text-[#989FAC] hover:bg-[#F4F5F7] hover:text-[#3772FE]'
    }`}
  >
    <div className="w-5 h-5 flex-shrink-0">{icon}</div>
    <span className="text-sm font-semibold">{label}</span>
  </div>
);

export default function Sidebar({ links, onClose }) {
  return (
    <aside className="w-72 h-full bg-white rounded-[2.5rem] lg:rounded-[2.5rem] rounded-none flex flex-col p-6 shadow-sm border border-[#E4EBF8]">
      <div className="flex items-center justify-between mb-12 px-2 pt-2">
        <div className="flex items-center space-x-3">
          <img src="/logo.svg" alt="АМУР.БЮДЖЕТ" className="w-10 h-10" />
          <span className="font-black tracking-tighter text-xl text-[#0F172A]">АМУР.БЮДЖЕТ</span>
        </div>
        {onClose && (
          <button 
            onClick={onClose}
            className="lg:hidden p-2 hover:bg-[#F4F5F7] rounded-xl transition-colors"
          >
            <svg className="w-6 h-6 text-[#989FAC]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      <nav className="flex-1 space-y-2">
        {links.map((link, idx) => (
          <SidebarLink key={idx} {...link} />
        ))}
      </nav>
    </aside>
  );
}
