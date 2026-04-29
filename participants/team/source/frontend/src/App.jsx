import { useState } from 'react';
import Sidebar from './components/dashboard/Sidebar';
import Header from './components/dashboard/Header';
import { HomeIcon, ChartIcon } from './components/icons';
import { FiltersProvider } from './context/FiltersContext';

// Импорт страниц
import Overview from './pages/Overview';
import Analytics from './pages/Analytics';
import ChatBot from './pages/ChatBot';

const PAGES = {
  overview: { 
    component: Overview, 
    title: 'Конструктор выборок', 
    description: 'Детальный анализ бюджетных данных и трендов',
    breadcrumbs: ['Конструктор'] 
  },
  analytics: { 
    component: Analytics, 
    title: 'Аналитика', 
    description: 'Общая информация о состоянии бюджета Амурской области',
    breadcrumbs: ['Аналитика'] 
  },
  chatbot: { 
    component: ChatBot, 
    title: 'AI Ассистент', 
    description: 'Интеллектуальный помощник для анализа бюджетных данных',
    breadcrumbs: ['AI Ассистент'] 
  }
};

export default function App() {
  const [currentPage, setCurrentPage] = useState('overview');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const sidebarLinks = [
    { label: "Конструктор", icon: <HomeIcon />, page: 'overview' },
    { label: "Аналитика", icon: <ChartIcon />, page: 'analytics' },
    { 
      label: "AI Ассистент", 
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ), 
      page: 'chatbot' 
    }
  ].map(link => ({
    ...link,
    active: currentPage === link.page,
    onClick: () => {
      setCurrentPage(link.page);
      setIsMobileMenuOpen(false);
    }
  }));

  const CurrentPageComponent = PAGES[currentPage].component;
  const pageConfig = PAGES[currentPage];

  return (
    <FiltersProvider>
      <div className="flex h-screen bg-[#F4F5F7] p-2 sm:p-4 gap-2 sm:gap-4 font-sans text-[#0F172A]">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block">
          <Sidebar links={sidebarLinks} />
        </div>

        {/* Mobile Sidebar Overlay */}
        {isMobileMenuOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <div 
              className="absolute left-0 top-0 bottom-0 w-72 bg-white"
              onClick={(e) => e.stopPropagation()}
            >
              <Sidebar links={sidebarLinks} onClose={() => setIsMobileMenuOpen(false)} />
            </div>
          </div>
        )}

        <div className="flex-1 flex flex-col gap-2 sm:gap-4 overflow-hidden min-w-0">
          <Header 
            title={pageConfig.title} 
            description={pageConfig.description}
            breadcrumbs={pageConfig.breadcrumbs}
            onMenuClick={() => setIsMobileMenuOpen(true)}
          />

          <main className="flex-1 overflow-y-auto pr-1 sm:pr-2">
            <CurrentPageComponent />
          </main>
        </div>
      </div>
    </FiltersProvider>
  );
}
