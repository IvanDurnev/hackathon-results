import { z } from "zod";

import { apiRequest } from "../../shared/api/client";
import { paginatedResponseSchema } from "../../shared/api/pagination";
import { adminDashboardResponseSchema, authResponseSchema, userSchema } from "./user.schema";

const adminUsersResponseSchema = paginatedResponseSchema(userSchema);
const adminUserResponseSchema = z.object({ user: userSchema });

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = LoginPayload & {
  username: string;
  display_name: string;
};

export type AdminCreateUserPayload = {
  email: string;
  username: string;
  display_name: string;
  password: string;
  active: boolean;
  is_admin: boolean;
};

export type AdminUpdateUserPayload = Partial<{
  email: string;
  username: string;
  display_name: string | null;
  password: string;
  active: boolean;
  is_admin: boolean;
}>;

export type UpdateProfilePayload = {
  username: string;
  display_name: string;
  avatar_file_id?: number | null;
};

export type ChangePasswordPayload = {
  current_password: string;
  new_password: string;
};

export type AdminUsersParams = {
  q?: string;
  page?: number;
  perPage?: number;
};

export async function login(payload: LoginPayload) {
  return apiRequest("/auth/login", { method: "POST", body: payload }, authResponseSchema);
}

export async function register(payload: RegisterPayload) {
  return apiRequest("/auth/register", { method: "POST", body: payload }, authResponseSchema);
}

export async function logout() {
  return apiRequest<{ message: string }>("/auth/logout", { method: "POST" });
}

export async function getMe() {
  return apiRequest("/auth/me", { method: "GET" }, authResponseSchema);
}

export async function updateMe(payload: UpdateProfilePayload) {
  return apiRequest("/users/me", { method: "PATCH", body: payload }, authResponseSchema);
}

export async function changePassword(payload: ChangePasswordPayload) {
  return apiRequest<{ message: string }>("/users/me/password", { method: "PATCH", body: payload });
}

export async function getAdminUsers({ q = "", page = 1, perPage = 10 }: AdminUsersParams = {}) {
  const params = new URLSearchParams();

  if (q.trim()) {
    params.set("q", q.trim());
  }

  params.set("page", String(page));
  params.set("per_page", String(perPage));

  return apiRequest(`/admin/users?${params.toString()}`, { method: "GET" }, adminUsersResponseSchema);
}

export async function getAdminDashboard() {
  return apiRequest("/admin/dashboard", { method: "GET" }, adminDashboardResponseSchema);
}

export async function createAdminUser(payload: AdminCreateUserPayload) {
  return apiRequest("/admin/users", { method: "POST", body: payload }, adminUserResponseSchema);
}

export async function updateAdminUser(userId: number, payload: AdminUpdateUserPayload) {
  return apiRequest(`/admin/users/${userId}`, { method: "PATCH", body: payload }, adminUserResponseSchema);
}

export async function deleteAdminUser(userId: number) {
  return apiRequest<{ message: string }>(`/admin/users/${userId}`, { method: "DELETE" });
}
