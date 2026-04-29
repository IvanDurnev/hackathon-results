import type { PropsWithChildren } from "react";
import { createContext, useContext, useEffect, useState } from "react";

const THEME_STORAGE_KEY = "theme";

export type Theme = "light" | "dark";

type ThemeContextValue = {
  theme: Theme;
  isDark: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

function normalizeTheme(value: string | null): Theme | null {
  return value === "light" || value === "dark" ? value : null;
}

function getPreferredTheme(): Theme {
  if (typeof window === "undefined") return "light";

  try {
    const storedTheme = normalizeTheme(window.localStorage.getItem(THEME_STORAGE_KEY));
    if (storedTheme) return storedTheme;
  } catch {
    // Ignore storage failures and fall back to system preference.
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.classList.toggle("dark", theme === "dark");
  root.style.colorScheme = theme;
}

export function getInitialTheme() {
  return getPreferredTheme();
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setThemeState] = useState<Theme>(getPreferredTheme);

  useEffect(() => {
    applyTheme(theme);
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      // Ignore storage failures.
    }
  }, [theme]);

  const value: ThemeContextValue = {
    theme,
    isDark: theme === "dark",
    setTheme: setThemeState,
    toggleTheme: () => setThemeState((current) => (current === "dark" ? "light" : "dark"))
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }

  return context;
}
