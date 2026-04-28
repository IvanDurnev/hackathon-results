import { API_BASE_URL } from "../../app/config";
import { apiRequest } from "../../shared/api/client";
import {
  analyticsCompareResponseSchema,
  analyticsDrilldownResponseSchema,
  analyticsIssuesResponseSchema,
  analyticsMetricsResponseSchema,
  analyticsQueryResponseSchema,
  analyticsSearchResponseSchema,
  analyticsSourcesResponseSchema,
  analyticsTemplatesResponseSchema,
  analyticsTimelineResponseSchema
} from "./analytics.schema";

export type AnalyticsQueryPayload = {
  mode: "search" | "template";
  template_code?: string | null;
  query?: string | null;
  object_keys?: string[];
  metrics: string[];
  date_mode: "range" | "compare";
  date_from?: string | null;
  date_to?: string | null;
  base_date?: string | null;
  compare_date?: string | null;
};

export type AnalyticsDrilldownPayload = AnalyticsQueryPayload & {
  row_id: string;
};

export type AnalyticsExportPayload = AnalyticsQueryPayload & {
  format: "csv" | "xlsx";
};

export type AnalyticsImportPayload = {
  folder_path?: string | null;
};

export async function getAnalyticsSources() {
  return apiRequest("/analytics/sources", { method: "GET" }, analyticsSourcesResponseSchema);
}

export async function importDemoAnalytics(payload: AnalyticsImportPayload = {}) {
  return apiRequest<{ message: string; sources: number; issues: number }>("/analytics/import-demo", { method: "POST", body: payload });
}

export async function getAnalyticsIssues() {
  return apiRequest("/analytics/import-issues", { method: "GET" }, analyticsIssuesResponseSchema);
}

export async function getAnalyticsMetrics() {
  return apiRequest("/analytics/metrics", { method: "GET" }, analyticsMetricsResponseSchema);
}

export async function getAnalyticsTemplates() {
  return apiRequest("/analytics/templates", { method: "GET" }, analyticsTemplatesResponseSchema);
}

export async function searchAnalyticsObjects(query: string) {
  const params = new URLSearchParams({ q: query });
  return apiRequest(`/analytics/search?${params.toString()}`, { method: "GET" }, analyticsSearchResponseSchema);
}

export async function runAnalyticsQuery(payload: AnalyticsQueryPayload) {
  return apiRequest("/analytics/query", { method: "POST", body: payload }, analyticsQueryResponseSchema);
}

export async function runAnalyticsTimeline(payload: AnalyticsQueryPayload) {
  return apiRequest("/analytics/timeline", { method: "POST", body: payload }, analyticsTimelineResponseSchema);
}

export async function runAnalyticsCompare(payload: AnalyticsQueryPayload) {
  return apiRequest("/analytics/compare", { method: "POST", body: payload }, analyticsCompareResponseSchema);
}

export async function getAnalyticsDrilldown(payload: AnalyticsDrilldownPayload) {
  return apiRequest("/analytics/drilldown", { method: "POST", body: payload }, analyticsDrilldownResponseSchema);
}

export async function exportAnalytics(payload: AnalyticsExportPayload) {
  const response = await fetch(`${API_BASE_URL}/analytics/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("Экспорт не выполнен.");
  }

  return response.blob();
}
