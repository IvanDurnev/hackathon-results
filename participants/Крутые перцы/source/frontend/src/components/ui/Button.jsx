export default function Button({ 
  children, 
  variant = "primary", 
  onClick, 
  className = "",
  ...props 
}) {
  const variants = {
    primary: "px-6 py-2.5 bg-[#3772FE] text-white rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all",
    secondary: "px-6 py-2.5 bg-white text-[#3772FE] border border-[#3772FE]/30 rounded-2xl font-bold text-sm hover:bg-[#EEF3FF] transition-all"
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
