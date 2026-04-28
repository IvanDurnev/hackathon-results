import { BarChart3 } from "lucide-react";
import { Link } from "react-router-dom";

import { UserMenu } from "../UserMenu/UserMenu";

export function TopNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/95 sm:bg-background/80 sm:backdrop-blur-xl sm:supports-[backdrop-filter]:bg-background/65">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link className="group flex min-w-0 items-center gap-3 font-semibold" to="/">
          <span className="inverse-panel relative flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-2xl shadow-soft">
            <span className="inverse-gradient absolute inset-0 opacity-80 transition-transform duration-500 group-hover:scale-125" />
            <BarChart3 className="relative" size={18} />
          </span>
          <span className="grid min-w-0 leading-tight">
            <span className="truncate font-display text-sm tracking-[0.12em] uppercase">Бюджет</span>
            <span className="truncate text-xs font-medium text-muted-foreground">конструктор выборок</span>
          </span>
        </Link>
        <UserMenu />
      </div>
    </header>
  );
}
