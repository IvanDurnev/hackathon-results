import { LayoutDashboard, LogOut, Shield, User } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { useLogout, useMe } from "../../entities/user/hooks";
import { Button } from "../../shared/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "../../shared/ui/dropdown-menu";
import { ThemeToggle } from "../ThemeToggle/ThemeToggle";

export function UserMenu() {
  const navigate = useNavigate();
  const me = useMe();
  const logout = useLogout();
  const user = logout.isPending ? undefined : me.data?.user;

  if (!user) {
    return (
      <nav className="flex items-center gap-2">
        <ThemeToggle />
        <Button asChild variant="ghost" size="sm">
          <Link to="/login">
            <User size={16} />
            Войти
          </Link>
        </Button>
        <Button asChild size="sm" className="hidden sm:inline-flex">
          <Link to="/register">Создать аккаунт</Link>
        </Button>
      </nav>
    );
  }

  const isAdmin = user.roles.includes("admin");
  const displayName = user.display_name?.trim() || user.username;
  const initials = user.username.slice(0, 2).toUpperCase();

  return (
    <div className="flex items-center gap-2">
      <ThemeToggle />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-10 gap-2 rounded-full px-2 hover:bg-card/80" aria-label="Открыть меню аккаунта">
            <span className="inverse-panel flex size-8 items-center justify-center overflow-hidden rounded-full text-xs font-bold shadow-sm">
              {user.avatar?.url ? (
                <img alt="" className="size-full object-cover" decoding="async" src={user.avatar.url} />
              ) : (
                initials
              )}
            </span>
            <span className="hidden max-w-36 truncate text-sm font-medium md:inline">{displayName}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <span className="block truncate">{displayName}</span>
            <span className="block truncate text-xs font-normal text-muted-foreground">{user.email}</span>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link to="/profile">
              <User size={16} />
              Профиль
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link to="/workspace">
              <LayoutDashboard size={16} />
              {isAdmin ? "Рабочее пространство" : "Рабочая область"}
            </Link>
          </DropdownMenuItem>
          {isAdmin ? (
            <DropdownMenuItem asChild>
              <Link to="/admin">
                <Shield size={16} />
                Администрирование
              </Link>
            </DropdownMenuItem>
          ) : null}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            disabled={logout.isPending}
            onSelect={(event) => {
              event.preventDefault();
              logout.mutate(undefined, { onSuccess: () => navigate("/login") });
            }}
          >
            <LogOut size={16} />
            Выйти
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
