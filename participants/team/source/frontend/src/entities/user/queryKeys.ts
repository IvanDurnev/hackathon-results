export const userKeys = {
  all: ["user"] as const,
  me: () => [...userKeys.all, "me"] as const,
  admin: () => [...userKeys.all, "admin"] as const,
  adminDashboard: () => [...userKeys.admin(), "dashboard"] as const,
  adminUsers: (q: string, page: number, perPage: number) => [...userKeys.admin(), "users", q, page, perPage] as const
};
