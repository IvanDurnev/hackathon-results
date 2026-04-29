import Input from '../ui/Input';

const BellIcon = () => <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>;

export default function Header({ title, breadcrumbs }) {
  return (
    <header className="h-20 bg-white rounded-[2rem] px-10 flex items-center justify-between shadow-sm border border-[#E4EBF8] shrink-0">
      <div>
        <h2 className="text-lg font-black text-[#0F172A]">{title}</h2>
        <div className="flex items-center space-x-2 text-[11px] text-[#989FAC] font-bold uppercase tracking-wider">
          {breadcrumbs.map((crumb, idx) => (
            <div key={idx} className="flex items-center space-x-2">
              <span>{crumb}</span>
              {idx < breadcrumbs.length - 1 && (
                <span className="w-1 h-1 bg-[#3772FE] rounded-full"></span>
              )}
            </div>
          ))}
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <Input placeholder="Поиск по КБК..." className="w-64" />
        <button className="w-11 h-11 bg-[#F4F5F7] rounded-2xl flex items-center justify-center text-[#989FAC] hover:text-[#3772FE] transition-colors">
          <BellIcon />
        </button>
      </div>
    </header>
  );
}
