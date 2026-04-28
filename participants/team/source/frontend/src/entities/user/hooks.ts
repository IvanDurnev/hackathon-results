import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createAdminUser,
  changePassword,
  deleteAdminUser,
  getAdminDashboard,
  getAdminUsers,
  getMe,
  login,
  logout,
  register,
  updateMe,
  updateAdminUser
} from "./api";
import { userKeys } from "./queryKeys";
import { ApiError } from "../../shared/api/errors";

function isUnauthorized(error: unknown) {
  return error instanceof ApiError && error.status === 401;
}

function clearSession(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.setQueryData(userKeys.me(), null);
  queryClient.removeQueries({ queryKey: userKeys.admin() });
}

export function useMe() {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: userKeys.me(),
    queryFn: async () => {
      try {
        return await getMe();
      } catch (error) {
        if (isUnauthorized(error)) {
          clearSession(queryClient);
          return null;
        }

        throw error;
      }
    }
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: login,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: userKeys.all })
  });
}

export function useRegister() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: register,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: userKeys.all })
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      try {
        return await logout();
      } catch (error) {
        if (isUnauthorized(error)) {
          return { message: "Сессия завершена." };
        }

        throw error;
      }
    },
    onSuccess: async () => {
      await queryClient.cancelQueries({ queryKey: userKeys.all });
      clearSession(queryClient);
      queryClient.invalidateQueries({ queryKey: userKeys.all });
    }
  });
}

export function useAdminUsers(q: string, page: number, perPage: number, enabled = true) {
  return useQuery({
    queryKey: userKeys.adminUsers(q, page, perPage),
    queryFn: () => getAdminUsers({ q, page, perPage }),
    enabled,
    placeholderData: keepPreviousData
  });
}

export function useAdminDashboard(enabled = true) {
  return useQuery({
    queryKey: userKeys.adminDashboard(),
    queryFn: getAdminDashboard,
    enabled
  });
}

export function useUpdateMe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateMe,
    onSuccess: (response) => {
      queryClient.setQueryData(userKeys.me(), response);
      queryClient.invalidateQueries({ queryKey: userKeys.admin() });
    }
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: changePassword
  });
}

export function useCreateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createAdminUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.admin() });
      queryClient.invalidateQueries({ queryKey: userKeys.all });
    }
  });
}

export function useUpdateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: number; payload: Parameters<typeof updateAdminUser>[1] }) =>
      updateAdminUser(userId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.admin() });
      queryClient.invalidateQueries({ queryKey: userKeys.all });
    }
  });
}

export function useDeleteAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteAdminUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.admin() });
      queryClient.invalidateQueries({ queryKey: userKeys.all });
    }
  });
}
