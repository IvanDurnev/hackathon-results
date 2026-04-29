import { createContext, useContext, useState } from 'react';

const FiltersContext = createContext();

export function FiltersProvider({ children }) {
  const [filters, setFilters] = useState({
    period_from: '2025-01',
    period_to: '2025-08',
    kcsr_mask: '1',
    budget_name: '',
    fund_source: '',
    min_amount: ''
  });

  const [data, setData] = useState([]);

  return (
    <FiltersContext.Provider value={{ filters, setFilters, data, setData }}>
      {children}
    </FiltersContext.Provider>
  );
}

export function useFilters() {
  const context = useContext(FiltersContext);
  if (!context) {
    throw new Error('useFilters must be used within FiltersProvider');
  }
  return context;
}
