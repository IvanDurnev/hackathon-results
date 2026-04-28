import { useState } from 'react';

export default function RadioGroup({ label, options, defaultValue, onChange, className = "" }) {
  const [selectedValue, setSelectedValue] = useState(defaultValue || options[0]);

  const handleSelect = (option) => {
    setSelectedValue(option);
    if (onChange) {
      onChange(option);
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {label && (
        <label className="text-[11px] font-black text-[#989FAC] uppercase tracking-widest ml-2">
          {label}
        </label>
      )}
      <div className="grid grid-cols-1 gap-2">
        {options.map((option, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSelect(option)}
            className={`p-4 rounded-2xl border transition-all cursor-pointer flex justify-between items-center ${
              selectedValue === option
                ? 'bg-[#EEF3FF] border-[#3772FE]/30'
                : 'bg-white border-[#E2E8F0] hover:border-[#3772FE]/30'
            }`}
          >
            <span className={`text-sm font-bold ${
              selectedValue === option ? 'text-[#3772FE]' : 'text-[#56607A]'
            }`}>
              {option}
            </span>
            {selectedValue === option && (
              <div className="w-2 h-2 bg-[#3772FE] rounded-full shadow-glow"></div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
