export default function Button({ 
  children, 
  variant = "primary", 
  onClick, 
  className = "",
  ...props 
}) {
  const variants = {
    primary: "px-4 py-2 sm:px-6 sm:py-2.5 bg-[#3772FE] text-white rounded-xl sm:rounded-2xl font-bold text-xs sm:text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all",
    secondary: "px-4 py-2 sm:px-6 sm:py-2.5 bg-white text-[#3772FE] border border-[#3772FE]/30 rounded-xl sm:rounded-2xl font-bold text-xs sm:text-sm hover:bg-[#EEF3FF] transition-all"
  };

  return (
    <button 
      onClick={onClick}
      className={`${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
