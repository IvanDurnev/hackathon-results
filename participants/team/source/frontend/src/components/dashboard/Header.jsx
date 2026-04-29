import Input from '../ui/Input';

export default function Header({ title, description, breadcrumbs, onMenuClick }) {
  return (
    <header className="min-h-[4rem] sm:h-20 bg-white rounded-[1.5rem] sm:rounded-[2rem] px-4 sm:px-10 py-3 sm:py-0 flex items-center justify-between shadow-sm border border-[#E4EBF8] shrink-0">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        {/* Mobile Menu Button */}
        <button 
          onClick={onMenuClick}
          className="lg:hidden p-2 hover:bg-[#F4F5F7] rounded-xl transition-colors flex-shrink-0"
        >
          <svg className="w-6 h-6 text-[#0F172A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        
        <div className="min-w-0 flex-1">
          <h2 className="text-base sm:text-lg font-black text-[#0F172A] truncate">{title}</h2>
          <p className="text-xs text-[#989FAC] font-medium hidden sm:block truncate">{description}</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
      </div>
    </header>
  );
}
