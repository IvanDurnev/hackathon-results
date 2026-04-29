import { createBrowserRouter, Navigate } from "react-router-dom";

import { RequireAdmin, RequireAuth } from "./guards";
import { AdminPage } from "../pages/AdminPage";
import { LoginPage } from "../pages/LoginPage";
import { ProfilePage } from "../pages/ProfilePage";
import { RegisterPage } from "../pages/RegisterPage";
import { RootRedirect } from "../pages/RootRedirect";
import { WorkspacePage } from "../pages/WorkspacePage";
import { AppShell } from "../widgets/AppShell/AppShell";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootRedirect />
  },
  {
    element: <AppShell />,
    children: [
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      {
        path: "profile",
        element: (
          <RequireAuth>
            <ProfilePage />
          </RequireAuth>
        )
      },
      {
        path: "workspace",
        element: (
          <RequireAuth>
            <WorkspacePage />
          </RequireAuth>
        )
      },
      {
        path: "admin",
        element: (
          <RequireAdmin>
            <AdminPage />
          </RequireAdmin>
        )
      },
      { path: "*", element: <Navigate to="/" replace /> }
    ]
  }
]);
