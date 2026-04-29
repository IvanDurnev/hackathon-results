import { Outlet, useLocation } from "react-router-dom";

import { TopNav } from "../TopNav/TopNav";

export function AppShell() {
  const location = useLocation();

  if (location.pathname.startsWith("/workspace")) {
    return <Outlet />;
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <div className="surface-grid pointer-events-none absolute inset-x-0 top-16 h-72 opacity-40 sm:fixed" />
      <TopNav />
      <div className="relative">
        <Outlet />
      </div>
    </div>
  );
}
