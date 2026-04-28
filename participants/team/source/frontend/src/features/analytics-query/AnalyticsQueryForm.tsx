import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarDays, Check, ChevronDown, Filter, Search, X } from "lucide-react";
import type { ComponentProps } from "react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { AnalyticsMetric, AnalyticsSearchHit, AnalyticsTemplate } from "../../entities/analytics/analytics.schema";
import type { AnalyticsQueryPayload } from "../../entities/analytics/api";
import { useAnalyticsSearch } from "../../entities/analytics/hooks";
import { useDebouncedValue } from "../../shared/lib/use-debounced-value";
import { cn } from "../../shared/lib/utils";
import { Badge } from "../../shared/ui/badge";
import { Button } from "../../shared/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "../../shared/ui/form";
import { Input } from "../../shared/ui/input";
import { Skeleton } from "../../shared/ui/skeleton";

const formSchema = z
  .object({
    mode: z.enum(["search", "template"]),
    template_code: z.string(),
    query: z.string(),
    metrics: z.array(z.string()).min(1, "Выберите хотя бы один показатель."),
    date_mode: z.enum(["range", "compare"]),
    date_from: z.string(),
    date_to: z.string(),
    base_date: z.string(),
    compare_date: z.string()
  })
  .superRefine((value, ctx) => {
    if (value.date_mode === "range" && (!value.date_from || !value.date_to)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["date_to"], message: "Укажите период." });
    }
    if (value.date_mode === "range" && value.date_from && value.date_to && value.date_from > value.date_to) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["date_to"], message: "Дата окончания не может быть раньше начала." });
    }
    if (value.date_mode === "compare" && (!value.base_date || !value.compare_date)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["compare_date"], message: "Укажите две даты." });
    }
  });

export type AnalyticsFormValues = z.infer<typeof formSchema>;

const DEFAULT_METRICS = ["LIMITS", "BO", "CASH_RCHB", "AGREEMENT_MBT", "CONTRACT_AMOUNT", "CONTRACT_PAYMENT"];

const FIELD_ICON_CLASS = "pointer-events-none absolute right-4 top-1/2 size-4 -translate-y-1/2 text-foreground";
const SELECT_CONTROL_CLASS =
  "h-10 w-full appearance-none rounded-md border border-input bg-background py-2 pl-3 pr-11 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";
const DATE_CONTROL_CLASS = "relative h-10 pr-11 budget-date-input";

const SOURCE_LABELS: Record<string, string> = {
  rchb: "РЧБ",
  agreements: "Соглашения",
  gz_budget_lines: "ГЗ строки",
  gz_contracts: "ГЗ договоры",
  gz_payments: "ГЗ платежи",
  buau: "БУАУ"
};

function sourceLabel(value: string) {
  return SOURCE_LABELS[value] ?? value;
}

export function AnalyticsQueryForm({
  activeTemplateCode,
  metrics,
  templates,
  selectedHits,
  isPending,
  onSelectedHitsChange,
  searchRequest,
  onSubmit
}: {
  activeTemplateCode?: string;
  metrics: AnalyticsMetric[];
  templates: AnalyticsTemplate[];
  selectedHits: AnalyticsSearchHit[];
  isPending: boolean;
  onSelectedHitsChange: (items: AnalyticsSearchHit[]) => void;
  searchRequest?: { value: string; nonce: number } | null;
  onSubmit: (payload: AnalyticsQueryPayload) => void;
}) {
  const form = useForm<AnalyticsFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      mode: "template",
      template_code: "skk",
      query: "6105",
      metrics: DEFAULT_METRICS,
      date_mode: "range",
      date_from: "2025-01-01",
      date_to: "2026-04-01",
      base_date: "2025-02-01",
      compare_date: "2026-01-01"
    }
  });

  const mode = form.watch("mode");
  const query = form.watch("query");
  const dateMode = form.watch("date_mode");
  const selectedMetrics = form.watch("metrics");
  const debouncedQuery = useDebouncedValue(query, 250);
  const search = useAnalyticsSearch(mode === "search" ? debouncedQuery : "");
  const searchItems = search.data?.items ?? [];

  useEffect(() => {
    if (mode === "template" && selectedHits.length) {
      onSelectedHitsChange([]);
    }
  }, [mode, onSelectedHitsChange, selectedHits.length]);

  useEffect(() => {
    if (!activeTemplateCode) return;
    if (form.getValues("template_code") === activeTemplateCode && form.getValues("mode") === "template") return;
    form.setValue("mode", "template");
    form.setValue("template_code", activeTemplateCode);
  }, [activeTemplateCode, form]);

  useEffect(() => {
    if (!searchRequest) return;
    form.setValue("mode", "search");
    form.setValue("query", searchRequest.value, { shouldValidate: true });
    onSelectedHitsChange([]);
  }, [form, onSelectedHitsChange, searchRequest?.nonce]);

  function toggleMetric(metricCode: string) {
    const current = form.getValues("metrics");
    if (current.includes(metricCode)) {
      form.setValue(
        "metrics",
        current.filter((item) => item !== metricCode),
        { shouldValidate: true }
      );
      return;
    }
    form.setValue("metrics", [...current, metricCode], { shouldValidate: true });
  }

  function toggleHit(hit: AnalyticsSearchHit) {
    if (selectedHits.some((item) => item.object_key === hit.object_key)) {
      onSelectedHitsChange(selectedHits.filter((item) => item.object_key !== hit.object_key));
      return;
    }
    onSelectedHitsChange([...selectedHits, hit]);
  }

  function submit(values: AnalyticsFormValues) {
    const selectedObjectKeys = values.mode === "search" ? selectedHits.map((item) => item.object_key) : [];
    const trimmedQuery = values.query.trim();

    if (values.mode === "search" && !trimmedQuery && !selectedObjectKeys.length) {
      form.setError("query", { type: "manual", message: "Введите запрос или выберите объект." });
      return;
    }

    onSubmit({
      mode: values.mode,
      template_code: values.mode === "template" ? values.template_code : null,
      query: values.mode === "search" && !selectedObjectKeys.length ? trimmedQuery || null : null,
      object_keys: selectedObjectKeys,
      metrics: values.metrics,
      date_mode: values.date_mode,
      date_from: values.date_mode === "range" ? values.date_from : null,
      date_to: values.date_mode === "range" ? values.date_to : null,
      base_date: values.date_mode === "compare" ? values.base_date : null,
      compare_date: values.date_mode === "compare" ? values.compare_date : null
    });
  }

  return (
    <Form {...form}>
      <form className="grid gap-5" onSubmit={form.handleSubmit(submit)}>
        <div className="grid gap-3 md:grid-cols-[13rem_minmax(0,1fr)]">
          <FormField
            control={form.control}
            name="mode"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Режим</FormLabel>
                <FormControl>
                  <SelectControl {...field}>
                    <option value="template">Контрольный шаблон</option>
                    <option value="search">Поиск объекта</option>
                  </SelectControl>
                </FormControl>
              </FormItem>
            )}
          />

          {mode === "template" ? (
            <FormField
              control={form.control}
              name="template_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Шаблон</FormLabel>
                  <FormControl>
                    <SelectControl {...field}>
                      {templates.map((template) => (
                        <option key={template.code} value={template.code}>
                          {template.name}
                        </option>
                      ))}
                    </SelectControl>
                  </FormControl>
                </FormItem>
              )}
            />
          ) : (
            <FormField
              control={form.control}
              name="query"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Поиск</FormLabel>
                  <FormControl>
                    <div className="flex min-w-0 items-center gap-2 rounded-md border bg-background px-3 shadow-sm">
                      <Search className="size-4 shrink-0 text-muted-foreground" />
                      <Input
                        className="h-10 min-w-0 border-0 px-0 shadow-none focus-visible:ring-0"
                        placeholder="6105, Тында, договор, получатель..."
                        {...field}
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
        </div>

        {mode === "search" ? (
          <div className="grid gap-2">
            {selectedHits.length ? (
              <div className="min-w-0 rounded-md border bg-muted/20 p-2">
                <div className="mb-2 flex items-center justify-between gap-3 text-xs text-muted-foreground">
                  <span>Выбрано: {selectedHits.length}</span>
                  <button type="button" className="font-medium text-foreground hover:text-primary" onClick={() => onSelectedHitsChange([])}>
                    Очистить
                  </button>
                </div>
                <div className="grid max-h-32 min-w-0 gap-1 overflow-auto pr-1">
                  {selectedHits.map((hit) => (
                    <button
                      key={hit.object_key}
                      type="button"
                      className="grid min-w-0 grid-cols-[minmax(0,1fr)_1rem] items-center gap-2 rounded-md border bg-card px-2.5 py-1.5 text-left text-xs font-medium"
                      onClick={() => toggleHit(hit)}
                      title={hit.display_name}
                    >
                      <span className="min-w-0 truncate">{hit.display_name}</span>
                      <X className="shrink-0" size={13} />
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
            <div className="max-h-44 min-w-0 overflow-auto rounded-md border bg-card">
              {search.isFetching ? (
                <div className="grid gap-2 p-3">
                  <Skeleton className="h-9" />
                  <Skeleton className="h-9" />
                </div>
              ) : searchItems.length ? (
                searchItems.map((hit) => {
                  const active = selectedHits.some((item) => item.object_key === hit.object_key);
                  return (
                    <button
                      key={hit.object_key}
                      type="button"
                      className={cn(
                        "flex min-w-0 w-full items-start justify-between gap-3 border-b px-3 py-2 text-left text-sm last:border-b-0 hover:bg-muted/40",
                        active && "bg-primary/8"
                      )}
                      onClick={() => toggleHit(hit)}
                      title={hit.display_name}
                    >
                      <span className="min-w-0 flex-1">
                        <span className="line-clamp-2 break-words font-medium">{hit.display_name}</span>
                        <span className="mt-1 block break-all text-xs text-muted-foreground">
                          {Object.values(hit.matched_codes).filter(Boolean).slice(0, 4).join(" / ")}
                        </span>
                      </span>
                      {active ? <Check className="size-4 shrink-0 text-primary" /> : null}
                    </button>
                  );
                })
              ) : (
                <div className="px-3 py-4 text-sm text-muted-foreground">Введите код, объект или номер документа.</div>
              )}
            </div>
          </div>
        ) : null}

        <FormField
          control={form.control}
          name="metrics"
          render={() => (
            <FormItem>
              <FormLabel>Показатели</FormLabel>
              <div className="grid gap-2 sm:grid-cols-2">
                {metrics.map((metric) => {
                  const active = selectedMetrics.includes(metric.code);
                  return (
                    <button
                      key={metric.code}
                      type="button"
                      className={cn(
                        "flex min-h-11 min-w-0 items-center justify-between gap-3 overflow-hidden rounded-md border bg-card px-3 py-2 text-left text-sm transition-colors hover:bg-muted/40",
                        active && "border-primary bg-primary/8"
                      )}
                      onClick={() => toggleMetric(metric.code)}
                    >
                      <span className="min-w-0 flex-1">
                        <span className="line-clamp-2 break-words font-medium">{metric.name}</span>
                        <span className="block text-xs text-muted-foreground">{sourceLabel(metric.source_type)}</span>
                      </span>
                      {active ? <Check className="size-4 shrink-0 text-primary" /> : null}
                    </button>
                  );
                })}
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid gap-3">
          <FormField
            control={form.control}
            name="date_mode"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Период</FormLabel>
                <FormControl>
                  <SelectControl {...field}>
                    <option value="range">Диапазон</option>
                    <option value="compare">Сравнение</option>
                  </SelectControl>
                </FormControl>
              </FormItem>
            )}
          />

          {dateMode === "range" ? (
            <div className="grid gap-3 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="date_from"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>С</FormLabel>
                    <FormControl>
                      <DateControl {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="date_to"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>По</FormLabel>
                    <FormControl>
                      <DateControl {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="base_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>База</FormLabel>
                    <FormControl>
                      <DateControl {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="compare_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Сравнить с</FormLabel>
                    <FormControl>
                      <DateControl {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          )}

          <Button type="submit" disabled={isPending} className="h-10 w-full">
            <Filter size={16} />
            {isPending ? "Считаем..." : "Сформировать"}
          </Button>
        </div>

        {mode === "template" ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <CalendarDays size={15} />
            <span>{templates.find((item) => item.code === form.watch("template_code"))?.description}</span>
          </div>
        ) : null}

        <div className="flex min-w-0 flex-wrap gap-2">
          {selectedMetrics.map((metricCode) => (
            <Badge key={metricCode} className="max-w-full whitespace-normal text-left" variant="secondary">
              {metrics.find((item) => item.code === metricCode)?.name ?? metricCode}
            </Badge>
          ))}
        </div>
      </form>
    </Form>
  );
}

function SelectControl({ children, className, ...props }: ComponentProps<"select">) {
  return (
    <div className="relative">
      <select className={cn(SELECT_CONTROL_CLASS, className)} {...props}>
        {children}
      </select>
      <ChevronDown aria-hidden="true" className={FIELD_ICON_CLASS} />
    </div>
  );
}

function DateControl({ className, ...props }: ComponentProps<typeof Input>) {
  return (
    <div className="relative">
      <Input {...props} type="date" className={cn(DATE_CONTROL_CLASS, className)} />
      <CalendarDays aria-hidden="true" className={FIELD_ICON_CLASS} />
    </div>
  );
}
