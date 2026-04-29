import { z } from "zod";

export const assistantChatResponseSchema = z.object({
  text: z.string(),
  provider: z.string().nullable().optional(),
  model: z.string().nullable().optional(),
  tool_calls: z.array(z.record(z.unknown())).optional().default([]),
  actions: z.array(z.record(z.unknown())).optional().default([])
});

export const assistantHealthResponseSchema = z.object({
  ok: z.boolean(),
  providers: z.array(z.string()),
  message: z.string().nullable().optional()
});

export const assistantTranscriptionResponseSchema = z.object({
  text: z.string()
});

export type AssistantChatResponse = z.infer<typeof assistantChatResponseSchema>;
export type AssistantHealthResponse = z.infer<typeof assistantHealthResponseSchema>;
export type AssistantTranscriptionResponse = z.infer<typeof assistantTranscriptionResponseSchema>;
