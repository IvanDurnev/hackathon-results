import { apiRequest } from "../../shared/api/client";
import {
  assistantChatResponseSchema,
  assistantHealthResponseSchema,
  assistantTranscriptionResponseSchema
} from "./assistant.schema";

export type AssistantMessagePayload = {
  role: "user" | "assistant";
  content: string;
};

export type AssistantChatPayload = {
  prompt: string;
  messages?: AssistantMessagePayload[];
  context?: Record<string, unknown>;
};

export type AssistantAction = {
  type?: string;
  label?: string;
  payload?: unknown;
};

export type AssistantToolCall = {
  name?: string;
  status?: string;
  summary?: string;
  arguments?: Record<string, unknown>;
};

export async function getAssistantHealth() {
  return apiRequest("/assistant/health", { method: "GET" }, assistantHealthResponseSchema);
}

export async function askAssistant(payload: AssistantChatPayload) {
  return apiRequest("/assistant/chat", { method: "POST", body: payload }, assistantChatResponseSchema);
}

export async function transcribeAssistantAudio(file: File) {
  const body = new FormData();
  body.append("file", file, file.name || "audio.webm");
  return apiRequest("/assistant/transcribe", { method: "POST", body }, assistantTranscriptionResponseSchema);
}
