import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  type AnalyticsImportPayload,
  exportAnalytics,
  getAnalyticsDrilldown,
  getAnalyticsIssues,
  getAnalyticsMetrics,
  getAnalyticsSources,
  getAnalyticsTemplates,
  importDemoAnalytics,
  runAnalyticsCompare,
  runAnalyticsQuery,
  runAnalyticsTimeline,
  searchAnalyticsObjects
} from "./api";
import { analyticsKeys } from "./queryKeys";

export function useAnalyticsSources() {
  return useQuery({
    queryKey: analyticsKeys.sources(),
    queryFn: getAnalyticsSources
  });
}

export function useImportDemoAnalytics() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload?: AnalyticsImportPayload) => importDemoAnalytics(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.all });
    }
  });
}

export function useAnalyticsIssues() {
  return useQuery({
    queryKey: analyticsKeys.issues(),
    queryFn: getAnalyticsIssues
  });
}

export function useAnalyticsMetrics() {
  return useQuery({
    queryKey: analyticsKeys.metrics(),
    queryFn: getAnalyticsMetrics
  });
}

export function useAnalyticsTemplates() {
  return useQuery({
    queryKey: analyticsKeys.templates(),
    queryFn: getAnalyticsTemplates
  });
}

export function useAnalyticsSearch(query: string) {
  return useQuery({
    queryKey: analyticsKeys.search(query),
    queryFn: () => searchAnalyticsObjects(query),
    enabled: query.trim().length >= 2
  });
}

export function useRunAnalyticsQuery() {
  return useMutation({
    mutationFn: runAnalyticsQuery
  });
}

export function useRunAnalyticsTimeline() {
  return useMutation({
    mutationFn: runAnalyticsTimeline
  });
}

export function useRunAnalyticsCompare() {
  return useMutation({
    mutationFn: runAnalyticsCompare
  });
}

export function useAnalyticsDrilldown() {
  return useMutation({
    mutationFn: getAnalyticsDrilldown
  });
}

export function useAnalyticsExport() {
  return useMutation({
    mutationFn: exportAnalytics
  });
}
