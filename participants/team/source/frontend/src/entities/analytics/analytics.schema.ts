import { z } from "zod";

export const analyticsSourceSchema = z.object({
  id: z.number(),
  source_type: z.string(),
  original_name: z.string(),
  checksum: z.string(),
  period_date: z.string().nullable(),
  rows_total: z.number(),
  rows_imported: z.number(),
  warnings_count: z.number(),
  errors_count: z.number(),
  metadata: z.record(z.unknown())
});

export const analyticsIssueSchema = z.object({
  severity: z.string(),
  code: z.string(),
  message: z.string(),
  source_file_id: z.number().nullable().optional(),
  row_number: z.number().nullable().optional()
});

export const analyticsMetricSchema = z.object({
  code: z.string(),
  name: z.string(),
  source_type: z.string()
});

export const analyticsTemplateSchema = z.object({
  code: z.string(),
  name: z.string(),
  description: z.string()
});

export const analyticsSearchHitSchema = z.object({
  object_key: z.string(),
  object_type: z.string(),
  display_name: z.string(),
  matched_codes: z.record(z.string().nullable()),
  rank: z.number(),
  source_types: z.array(z.string())
});

export const analyticsQueryRowSchema = z.object({
  row_id: z.string(),
  object_key: z.string(),
  object_name: z.string(),
  metric_code: z.string(),
  metric_name: z.string(),
  amount: z.number(),
  source_type: z.string(),
  codes: z.record(z.string().nullable()),
  warning_codes: z.array(z.string()),
  drilldown_available: z.boolean()
});

export const analyticsQueryResponseSchema = z.object({
  columns: z.array(z.object({ key: z.string(), title: z.string() })),
  rows: z.array(analyticsQueryRowSchema),
  totals: z.record(z.number()),
  warnings: z.array(analyticsIssueSchema)
});

export const analyticsTimelinePointSchema = z.object({
  period: z.string(),
  metric_code: z.string(),
  metric_name: z.string(),
  amount: z.number()
});

export const analyticsCompareRowSchema = z.object({
  object_key: z.string(),
  object_name: z.string(),
  metric_code: z.string(),
  metric_name: z.string(),
  base_value: z.number(),
  compare_value: z.number(),
  delta: z.number(),
  delta_percent: z.number().nullable()
});

export const analyticsDrilldownRecordSchema = z.object({
  source_type: z.string(),
  label: z.string(),
  amount: z.number(),
  event_date: z.string().nullable(),
  details: z.record(z.unknown())
});

export const analyticsSourcesResponseSchema = z.object({ items: z.array(analyticsSourceSchema) });
export const analyticsIssuesResponseSchema = z.object({ items: z.array(analyticsIssueSchema) });
export const analyticsMetricsResponseSchema = z.object({ items: z.array(analyticsMetricSchema) });
export const analyticsTemplatesResponseSchema = z.object({ items: z.array(analyticsTemplateSchema) });
export const analyticsSearchResponseSchema = z.object({ items: z.array(analyticsSearchHitSchema) });
export const analyticsTimelineResponseSchema = z.object({ items: z.array(analyticsTimelinePointSchema) });
export const analyticsCompareResponseSchema = z.object({ items: z.array(analyticsCompareRowSchema) });
export const analyticsDrilldownResponseSchema = z.object({ items: z.array(analyticsDrilldownRecordSchema) });

export type AnalyticsSource = z.infer<typeof analyticsSourceSchema>;
export type AnalyticsIssue = z.infer<typeof analyticsIssueSchema>;
export type AnalyticsMetric = z.infer<typeof analyticsMetricSchema>;
export type AnalyticsTemplate = z.infer<typeof analyticsTemplateSchema>;
export type AnalyticsSearchHit = z.infer<typeof analyticsSearchHitSchema>;
export type AnalyticsQueryRow = z.infer<typeof analyticsQueryRowSchema>;
export type AnalyticsQueryResponse = z.infer<typeof analyticsQueryResponseSchema>;
export type AnalyticsTimelinePoint = z.infer<typeof analyticsTimelinePointSchema>;
export type AnalyticsCompareRow = z.infer<typeof analyticsCompareRowSchema>;
export type AnalyticsDrilldownRecord = z.infer<typeof analyticsDrilldownRecordSchema>;
