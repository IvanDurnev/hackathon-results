import { useState } from 'react';
import Sidebar from './components/dashboard/Sidebar';
import Header from './components/dashboard/Header';
import { HomeIcon, MagicIcon, ChartIcon, DocIcon } from './components/icons';

// Импорт страниц
import Overview from './pages/Overview';
import Constructor from './pages/Constructor';
import Analytics from './pages/Analytics';
import Documents from './pages/Documents';

const PAGES = {
  overview: { component: Overview, title: 'Обзор', breadcrumbs: ['Система', 'Обзор'] },
  constructor: { component: Constructor, title: 'Конструктор выборок', breadcrumbs: ['Система', 'АЦК-Финансы'] },
  analytics: { component: Analytics, title: 'Аналитика', breadcrumbs: ['Система', 'Аналитика'] },
  documents: { component: Documents, title: 'Документы', breadcrumbs: ['Система', 'Документы'] }
};

export default function App() {
  const [currentPage, setCurrentPage] = useState('constructor');

  const sidebarLinks = [
    { label: "Обзор", icon: <HomeIcon />, page: 'overview' },
    { label: "Конструктор", icon: <MagicIcon />, page: 'constructor' },
    { label: "Аналитика", icon: <ChartIcon />, page: 'analytics' },
    { label: "Документы", icon: <DocIcon />, page: 'documents' }
  ].map(link => ({
    ...link,
    active: currentPage === link.page,
    onClick: () => setCurrentPage(link.page)
  }));

  const CurrentPageComponent = PAGES[currentPage].component;
  const pageConfig = PAGES[currentPage];

  return (
    <div className="flex h-screen bg-[#F4F5F7] p-4 gap-4 font-sans text-[#0F172A]">
      <Sidebar links={sidebarLinks} />

      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        <Header 
          title={pageConfig.title} 
          breadcrumbs={pageConfig.breadcrumbs} 
        />

        <main className="flex-1 overflow-y-auto pr-2">
          <CurrentPageComponent />
        </main>
      </div>
    </div>
  );
}
