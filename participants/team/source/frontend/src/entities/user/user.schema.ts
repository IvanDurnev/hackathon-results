import { z } from "zod";

import { fileAssetSchema } from "../file/file.schema";

export const userSchema = z.object({
  id: z.number(),
  email: z.string(),
  username: z.string(),
  display_name: z.string().nullable(),
  active: z.boolean(),
  roles: z.array(z.string()),
  avatar: fileAssetSchema.nullish(),
  created_at: z.string(),
  updated_at: z.string()
});

export const authResponseSchema = z.object({
  user: userSchema
});

export const adminMetricsSchema = z.object({
  users: z.number(),
  admins: z.number(),
  active: z.number(),
  inactive: z.number()
});

export const adminDashboardResponseSchema = z.object({
  metrics: adminMetricsSchema
});

export type User = z.infer<typeof userSchema>;
export type AdminMetrics = z.infer<typeof adminMetricsSchema>;
