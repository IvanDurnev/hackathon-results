export const analyticsKeys = {
  all: ["analytics"] as const,
  sources: () => [...analyticsKeys.all, "sources"] as const,
  metrics: () => [...analyticsKeys.all, "metrics"] as const,
  templates: () => [...analyticsKeys.all, "templates"] as const,
  issues: () => [...analyticsKeys.all, "issues"] as const,
  search: (query: string) => [...analyticsKeys.all, "search", query] as const
};
