import { z } from "zod";

export const fileAccessScopeSchema = z.enum(["public", "private"]);

export const fileAssetSchema = z.object({
  id: z.number(),
  original_name: z.string(),
  mime_type: z.string(),
  size_bytes: z.number().int().nonnegative(),
  access_scope: fileAccessScopeSchema,
  url: z.string().url(),
  created_at: z.string(),
  updated_at: z.string()
});

export const fileResponseSchema = z.object({
  file: fileAssetSchema
});

export type FileAccessScope = z.infer<typeof fileAccessScopeSchema>;
export type FileAsset = z.infer<typeof fileAssetSchema>;
export type FileResponse = z.infer<typeof fileResponseSchema>;

