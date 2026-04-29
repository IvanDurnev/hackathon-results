import { MoonStar, SunMedium } from "lucide-react";

import { useTheme } from "../../app/theme";
import { Button } from "../../shared/ui/button";
import { cn } from "@/shared/lib/utils";

type ThemeToggleProps = {
  className?: string;
  variant?: "icon" | "inline";
};

export function ThemeToggle({ className, variant = "icon" }: ThemeToggleProps) {
  const { isDark, toggleTheme } = useTheme();
  const Icon = isDark ? SunMedium : MoonStar;
  const label = isDark ? "Переключить на светлую тему" : "Переключить на тёмную тему";

  if (variant === "inline") {
    return (
      <Button
        type="button"
        variant="outline"
        className={cn("h-11 rounded-full px-4", className)}
        onClick={toggleTheme}
        aria-pressed={isDark}
      >
        <Icon size={16} />
        <span>{label}</span>
      </Button>
    );
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      className={cn("rounded-full", className)}
      onClick={toggleTheme}
      aria-label={label}
      title={label}
      aria-pressed={isDark}
    >
      <Icon size={16} />
    </Button>
  );
}
