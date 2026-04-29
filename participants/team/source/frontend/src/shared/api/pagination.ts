import { z } from "zod";

export const paginationSchema = z.object({
  page: z.number(),
  per_page: z.number(),
  total: z.number(),
  pages: z.number()
});

export type Pagination = z.infer<typeof paginationSchema>;

export function paginatedResponseSchema<T extends z.ZodTypeAny>(itemSchema: T) {
  return z.object({
    items: z.array(itemSchema),
    pagination: paginationSchema
  });
}
