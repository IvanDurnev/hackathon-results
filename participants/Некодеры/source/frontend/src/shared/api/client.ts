import { z } from "zod";

import { API_BASE_URL } from "../../app/config";
import { ApiError } from "./errors";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: BodyInit | Record<string, unknown>;
};

function buildUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

function buildRequest(options: RequestOptions): RequestInit {
  const headers = new Headers(options.headers);
  const { body, ...init } = options;

  if (body instanceof FormData) {
    return { ...init, body, headers, credentials: "include" };
  }

  if (body !== undefined) {
    headers.set("Content-Type", "application/json");
    return {
      ...init,
      body: JSON.stringify(body),
      headers,
      credentials: "include"
    };
  }

  return { ...init, headers, credentials: "include" };
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
  schema?: z.ZodType<T>
): Promise<T> {
  const response = await fetch(buildUrl(path), buildRequest(options));
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const error = payload?.error ?? {};
    throw new ApiError(
      response.status,
      error.code ?? "http_error",
      error.message ?? "Запрос не выполнен.",
      error.details ?? {}
    );
  }

  return schema ? schema.parse(payload) : (payload as T);
}
