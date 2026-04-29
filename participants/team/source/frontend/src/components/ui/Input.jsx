export default function Input({ 
  label,
  placeholder, 
  value, 
  onChange, 
  type = "text",
  className = "",
  ...props 
}) {
  return (
    <div className="flex flex-col gap-1.5 sm:gap-2">
      {label && (
        <label className="text-[10px] sm:text-xs font-bold text-[#989FAC] uppercase tracking-widest">
          {label}
        </label>
      )}
      <input 
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`bg-[#F4F5F7] border-none rounded-xl sm:rounded-2xl px-4 py-2 sm:px-6 sm:py-2.5 text-xs sm:text-sm focus:ring-2 focus:ring-[#3772FE]/20 transition-all outline-none ${className}`}
        {...props}
      />
    </div>
  );
}
