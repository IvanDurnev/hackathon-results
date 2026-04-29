import { useState, useRef, useEffect } from 'react';
import { ChevronDownIcon } from '../icons';

export default function Select({ label, options, value, onChange, className = "" }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || options[0]);
  const dropdownRef = useRef(null);

  // Закрытие при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (option) => {
    setSelectedValue(option);
    setIsOpen(false);
    if (onChange) {
      onChange(option);
    }
  };

  return (
    <div className="space-y-1.5 sm:space-y-2" ref={dropdownRef}>
      {label && (
        <label className="text-[10px] sm:text-[11px] font-black text-[#989FAC] uppercase tracking-widest ml-2">
          {label}
        </label>
      )}
      
      <div className="relative">
        {/* Кнопка выбора */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className={`w-full bg-[#F4F5F7] border-none rounded-xl sm:rounded-2xl px-4 py-2.5 sm:px-5 sm:py-3.5 text-xs sm:text-sm font-semibold outline-none ring-1 ring-transparent focus:ring-[#3772FE]/30 transition-all text-left flex items-center justify-between ${className}`}
        >
          <span className="text-[#0F172A] truncate">{selectedValue}</span>
          <div className={`transition-transform duration-200 text-[#989FAC] flex-shrink-0 ml-2 ${isOpen ? 'rotate-180' : ''}`}>
            <ChevronDownIcon />
          </div>
        </button>

        {/* Выпадающий список */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-2 bg-white rounded-xl sm:rounded-2xl shadow-xl border border-[#E2E8F0] overflow-hidden animate-fadeIn">
            <div className="max-h-48 sm:max-h-60 overflow-y-auto py-2 px-2">
              {options.map((option, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelect(option)}
                  className={`w-full px-3 py-2.5 sm:px-4 sm:py-3 text-xs sm:text-sm font-semibold text-left transition-all rounded-lg sm:rounded-xl mb-1 last:mb-0 ${
                    selectedValue === option
                      ? 'bg-[#EEF3FF] text-[#3772FE]'
                      : 'text-[#0F172A] hover:bg-[#F4F5F7]'
                  }`}
                >
                  <span className="truncate block">{option}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
