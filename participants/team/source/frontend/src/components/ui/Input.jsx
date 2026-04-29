export default function Input({ 
  placeholder, 
  value, 
  onChange, 
  className = "",
  ...props 
}) {
  return (
    <input 
      type="text"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={`bg-[#F4F5F7] border-none rounded-2xl px-6 py-2.5 text-sm focus:ring-2 focus:ring-[#3772FE]/20 transition-all outline-none ${className}`}
      {...props}
    />
  );
}
