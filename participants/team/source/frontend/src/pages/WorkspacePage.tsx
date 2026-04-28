import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Database,
  Download,
  FileDown,
  FileSpreadsheet,
  FolderOpen,
  History,
  Info,
  Layers3,
  LayoutDashboard,
  ListChecks,
  Loader2,
  MessageSquareText,
  Play,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  TableProperties,
  Trash2
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import type { AnalyticsQueryPayload } from "../entities/analytics/api";
import type {
  AnalyticsCompareRow,
  AnalyticsDrilldownRecord,
  AnalyticsIssue,
  AnalyticsMetric,
  AnalyticsQueryResponse,
  AnalyticsQueryRow,
  AnalyticsSearchHit,
  AnalyticsSource,
  AnalyticsTemplate,
  AnalyticsTimelinePoint
} from "../entities/analytics/analytics.schema";
import {
  useAnalyticsDrilldown,
  useAnalyticsExport,
  useAnalyticsIssues,
  useAnalyticsMetrics,
  useAnalyticsSources,
  useAnalyticsTemplates,
  useImportDemoAnalytics,
  useRunAnalyticsCompare,
  useRunAnalyticsQuery,
  useRunAnalyticsTimeline
} from "../entities/analytics/hooks";
import { useMe } from "../entities/user/hooks";
import { AnalyticsQueryForm } from "../features/analytics-query/AnalyticsQueryForm";
import { cn } from "../shared/lib/utils";
import { Alert, AlertDescription, AlertTitle } from "../shared/ui/alert";
import { Badge } from "../shared/ui/badge";
import { Button } from "../shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../shared/ui/card";
import { Input } from "../shared/ui/input";
import { Skeleton } from "../shared/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../shared/ui/tabs";
import { AnalyticsResults } from "../widgets/AnalyticsResults/AnalyticsResults";
import { UserMenu } from "../widgets/UserMenu/UserMenu";

type WorkspaceTab =
  | "constructor"
  | "templates"
  | "sources"
  | "quality"
  | "selections"
  | "export"
  | "assistant";

type SelectionHistoryItem = {
  id: string;
  title: string;
  createdAt: string;
  payload: AnalyticsQueryPayload;
  rows: number;
  amount: number;
  warnings: number;
};

type LastExport = {
  format: "csv" | "xlsx";
  createdAt: string;
  size: number;
};

type SearchRequest = {
  value: string;
  nonce: number;
};

const DEFAULT_METRICS = ["LIMITS", "BO", "CASH_RCHB", "AGREEMENT_MBT", "CONTRACT_AMOUNT", "CONTRACT_PAYMENT"];

const NAV_ITEMS: Array<{ value: WorkspaceTab; label: string; icon: LucideIcon }> = [
  { value: "constructor", label: "Конструктор", icon: LayoutDashboard },
  { value: "templates", label: "Контрольные шаблоны", icon: ClipboardCheck },
  { value: "sources", label: "Источники данных", icon: Database },
  { value: "quality", label: "Качество данных", icon: ShieldAlert },
  { value: "selections", label: "Мои выборки", icon: FolderOpen },
  { value: "export", label: "Экспорт", icon: FileDown },
  { value: "assistant", label: "ИИ-помощник", icon: Sparkles }
];

const TEMPLATE_RULES: Record<string, string> = {
  kik: "КЦСР содержит 978",
  skk: "КЦСР содержит 6105",
  two_three: "КЦСР содержит 970",
  okv: "ДопКР не 000 или КВР 400/406/407/408/460-466"
};

const SOURCE_LABELS: Record<string, string> = {
  rchb: "РЧБ",
  agreements: "Соглашения",
  gz_budget_lines: "ГЗ строки",
  gz_contracts: "ГЗ договоры",
  gz_payments: "ГЗ платежи",
  buau: "БУАУ"
};

const ISSUE_TITLES: Record<string, string> = {
  payment_budget_line_missing: "Платежки без бюджетной строки",
  payment_contract_missing: "Платежки без договора",
  contract_budget_line_missing: "Договоры без бюджетной строки",
  contract_amount_allocated_equally: "Несколько бюджетных строк",
  equal_by_line_no_amount: "Сумма распределена поровну",
  row_parse_error: "Ошибки парсинга",
  missing_columns: "Не хватает колонок",
  unknown_template: "Неизвестный шаблон"
};

const CHART_COLORS = ["#2563eb", "#059669", "#7c3aed", "#ea580c", "#0891b2", "#64748b", "#dc2626"];

function sourceLabel(value: string) {
  return SOURCE_LABELS[value] ?? value;
}

function shortTemplateLabel(template: AnalyticsTemplate) {
  const labels: Record<string, string> = {
    kik: "КИК",
    skk: "СКК",
    two_three: "2/3",
    okv: "ОКВ"
  };
  return labels[template.code] ?? template.name;
}

function issueLabel(code: string) {
  return ISSUE_TITLES[code] ?? code;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("ru-RU").format(value);
}

function formatMoney(value: number) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);
}

function formatDate(value: string | null | undefined) {
  if (!value) return "—";
  const [year, month, day] = value.slice(0, 10).split("-");
  if (!year || !month || !day) return value;
  return `${day}.${month}.${year}`;
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function formatFileSize(value: number) {
  if (value < 1024) return `${value} Б`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} КБ`;
  return `${(value / 1024 / 1024).toFixed(1)} МБ`;
}

function sumTotals(totals: Record<string, number>) {
  return Object.values(totals).reduce((sum, value) => sum + value, 0);
}

function metricLabel(code: string, metrics: AnalyticsMetric[]) {
  return metrics.find((metric) => metric.code === code)?.name ?? code;
}

function createSearchPayload(query: string): AnalyticsQueryPayload {
  return {
    mode: "search",
    template_code: null,
    query: query.trim(),
    object_keys: [],
    metrics: DEFAULT_METRICS,
    date_mode: "range",
    date_from: "2025-01-01",
    date_to: "2026-04-01",
    base_date: null,
    compare_date: null
  };
}

function payloadTitle(payload: AnalyticsQueryPayload, templates: AnalyticsTemplate[]) {
  const template = templates.find((item) => item.code === payload.template_code);
  const target =
    payload.mode === "template"
      ? template?.name ?? payload.template_code ?? "Контрольный шаблон"
      : payload.object_keys?.length
        ? `${payload.object_keys.length} объект(а)`
        : payload.query?.trim() || "Поиск";
  const period =
    payload.date_mode === "range"
      ? `${formatDate(payload.date_from)} — ${formatDate(payload.date_to)}`
      : `${formatDate(payload.base_date)} → ${formatDate(payload.compare_date)}`;
  return `${target} · ${period}`;
}

function createTemplatePayload(templateCode: string, dateMode: "range" | "compare" = "range"): AnalyticsQueryPayload {
  if (dateMode === "compare") {
    return {
      mode: "template",
      template_code: templateCode,
      query: null,
      object_keys: [],
      metrics: DEFAULT_METRICS,
      date_mode: "compare",
      date_from: null,
      date_to: null,
      base_date: "2025-01-01",
      compare_date: "2026-01-01"
    };
  }

  return {
    mode: "template",
    template_code: templateCode,
    query: null,
    object_keys: [],
    metrics: DEFAULT_METRICS,
    date_mode: "range",
    date_from: "2025-01-01",
    date_to: "2026-04-01",
    base_date: null,
    compare_date: null
  };
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function sourceMetadata(source: AnalyticsSource, key: string) {
  const value = source.metadata[key];
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return "—";
}

export function WorkspacePage() {
  const me = useMe();
  const isAdmin = Boolean(me.data?.user.roles.includes("admin"));
  const sources = useAnalyticsSources();
  const issues = useAnalyticsIssues();
  const metrics = useAnalyticsMetrics();
  const templates = useAnalyticsTemplates();
  const importDemo = useImportDemoAnalytics();
  const query = useRunAnalyticsQuery();
  const timeline = useRunAnalyticsTimeline();
  const compare = useRunAnalyticsCompare();
  const drilldown = useAnalyticsDrilldown();
  const exportMutation = useAnalyticsExport();

  const [activeTab, setActiveTab] = useState<WorkspaceTab>("constructor");
  const [selectedHits, setSelectedHits] = useState<AnalyticsSearchHit[]>([]);
  const [lastPayload, setLastPayload] = useState<AnalyticsQueryPayload | null>(null);
  const [queryResult, setQueryResult] = useState<AnalyticsQueryResponse | null>(null);
  const [timelinePoints, setTimelinePoints] = useState<AnalyticsTimelinePoint[]>([]);
  const [compareRows, setCompareRows] = useState<AnalyticsCompareRow[]>([]);
  const [selectedRow, setSelectedRow] = useState<AnalyticsQueryRow | null>(null);
  const [drilldownRows, setDrilldownRows] = useState<AnalyticsDrilldownRecord[]>([]);
  const [drilldownOpen, setDrilldownOpen] = useState(false);
  const [history, setHistory] = useState<SelectionHistoryItem[]>([]);
  const [lastExport, setLastExport] = useState<LastExport | null>(null);
  const [searchRequest, setSearchRequest] = useState<SearchRequest | null>(null);

  const isLoading = query.isPending || timeline.isPending || compare.isPending;
  const sourceItems = sources.data?.items ?? [];
  const issueItems = issues.data?.items ?? [];
  const metricItems = metrics.data?.items ?? [];
  const templateItems = templates.data?.items ?? [];
  const totalRows = sourceItems.reduce((sum, source) => sum + source.rows_total, 0);
  const totalImported = sourceItems.reduce((sum, source) => sum + source.rows_imported, 0);
  const totalWarnings = sourceItems.reduce((sum, source) => sum + source.warnings_count, 0);
  const totalErrors = sourceItems.reduce((sum, source) => sum + source.errors_count, 0);
  const activeRows = queryResult?.rows.length ?? compareRows.length;
  const activeAmount = queryResult ? sumTotals(queryResult.totals) : compareRows.reduce((sum, row) => sum + row.compare_value, 0);
  const activeWarnings = queryResult?.warnings.length ?? 0;

  const metricNameByCode = useMemo(() => new Map(metricItems.map((metric) => [metric.code, metric.name])), [metricItems]);

  function rememberSelection(payload: AnalyticsQueryPayload, rows: number, amount: number, warnings: number) {
    const title = payloadTitle(payload, templateItems);
    setHistory((items) => [
      {
        id: `${Date.now()}-${items.length}`,
        title,
        createdAt: new Date().toISOString(),
        payload,
        rows,
        amount,
        warnings
      },
      ...items
    ].slice(0, 8));
  }

  async function handleSubmit(payload: AnalyticsQueryPayload) {
    setLastPayload(payload);
    setSelectedRow(null);
    setDrilldownRows([]);
    setCompareRows([]);
    setTimelinePoints([]);

    try {
      if (payload.date_mode === "compare") {
        const response = await compare.mutateAsync(payload);
        setQueryResult(null);
        setCompareRows(response.items);
        rememberSelection(
          payload,
          response.items.length,
          response.items.reduce((sum, row) => sum + row.compare_value, 0),
          0
        );
        return;
      }

      const [queryResponse, timelineResponse] = await Promise.all([
        query.mutateAsync(payload),
        timeline.mutateAsync(payload)
      ]);
      setQueryResult(queryResponse);
      setTimelinePoints(timelineResponse.items);
      rememberSelection(payload, queryResponse.rows.length, sumTotals(queryResponse.totals), queryResponse.warnings.length);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Запрос не выполнен.");
    }
  }

  async function handleOpenDrilldown(row: AnalyticsQueryRow) {
    if (!lastPayload || lastPayload.date_mode !== "range") return;
    setSelectedRow(row);
    setDrilldownOpen(true);
    try {
      const response = await drilldown.mutateAsync({ ...lastPayload, row_id: row.row_id });
      setDrilldownRows(response.items);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Расшифровка не загружена.");
    }
  }

  async function handleExport(payload: AnalyticsQueryPayload | null, format: "csv" | "xlsx") {
    if (!payload) return;
    if (payload.date_mode !== "range") {
      toast.error("Экспорт доступен для выборки с диапазоном дат.");
      return;
    }

    try {
      const blob = await exportMutation.mutateAsync({ ...payload, format });
      setLastExport({ format, createdAt: new Date().toISOString(), size: blob.size });
      downloadBlob(blob, `budget-selection.${format}`);
      toast.success(`Экспорт ${format.toUpperCase()} сформирован.`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Экспорт не выполнен.");
    }
  }

  async function handleImportDemo(folderPath?: string) {
    try {
      const response = await importDemo.mutateAsync({ folder_path: folderPath?.trim() || null });
      toast.success(response.message);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Импорт не выполнен.");
    }
  }

  async function handleOpenTemplate(templateCode: string) {
    setActiveTab("constructor");
    await handleSubmit(createTemplatePayload(templateCode));
  }

  async function handleSearchRequest(value: string) {
    const queryText = value.trim();
    if (!queryText) {
      setActiveTab("constructor");
      return;
    }
    setActiveTab("constructor");
    setSelectedHits([]);
    setSearchRequest({ value: queryText, nonce: Date.now() });
    await handleSubmit(createSearchPayload(queryText));
  }

  async function handleOpenCodeSearch() {
    await handleSearchRequest("6105");
  }

  async function handleCompareTemplate(templateCode: string) {
    setActiveTab("constructor");
    await handleSubmit(createTemplatePayload(templateCode, "compare"));
  }

  return (
    <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as WorkspaceTab)} className="min-h-screen bg-background text-foreground">
      <div className="min-h-screen lg:grid lg:grid-cols-[252px_minmax(0,1fr)]">
        <aside className="sticky top-0 hidden h-screen flex-col overflow-y-auto border-r bg-card lg:flex">
          <div className="flex h-[70px] items-center px-5">
            <BudgetLogo />
          </div>
          <TabsList className="grid h-auto w-full grid-cols-1 gap-1 bg-transparent px-3 py-5 text-foreground">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <TabsTrigger
                  key={item.value}
                  value={item.value}
                  className="h-11 justify-start gap-3 rounded-md px-3 text-[15px] font-medium text-slate-600 data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none"
                >
                  <Icon size={18} />
                  <span className="truncate">{item.label}</span>
                </TabsTrigger>
              );
            })}
          </TabsList>
        </aside>

        <div className="min-w-0">
          <WorkspaceTopBar
            isExporting={exportMutation.isPending}
            lastPayload={lastPayload}
            totalErrors={totalErrors}
            totalWarnings={totalWarnings}
            onExport={() => handleExport(lastPayload, "xlsx")}
            onOpenQuality={() => setActiveTab("quality")}
            onSearch={handleSearchRequest}
          />

          <main className="px-4 py-5 sm:px-6 lg:px-7 lg:py-6">
            <TabsList className="mb-5 grid h-auto w-full grid-cols-2 gap-1 bg-transparent p-0 text-foreground sm:grid-cols-4 lg:hidden">
              {NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                return (
                  <TabsTrigger
                    key={item.value}
                    value={item.value}
                    className="h-10 justify-start gap-2 rounded-md border border-transparent px-3 data-[state=active]:border-primary/20 data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none"
                  >
                    <Icon size={16} />
                    <span className="truncate">{item.label}</span>
                  </TabsTrigger>
                );
              })}
            </TabsList>

            <div className="mx-auto grid max-w-[96rem] gap-5">
            <TabsContent value="constructor" className="mt-0">
              <ConstructorTab
                activeWarnings={activeWarnings}
                compareRows={compareRows}
                drilldownOpen={drilldownOpen}
                drilldownRows={drilldownRows}
                isLoading={isLoading}
                lastPayload={lastPayload}
                metrics={metricItems}
                metricsLoading={metrics.isLoading}
                queryResult={queryResult}
                selectedHits={selectedHits}
                selectedRow={selectedRow}
                sourceItems={sourceItems}
                templates={templateItems}
                activeTemplateCode={lastPayload?.mode === "template" ? lastPayload.template_code ?? "skk" : "skk"}
                templatesLoading={templates.isLoading}
                timelinePoints={timelinePoints}
                onCompareTemplate={handleCompareTemplate}
                onDrilldownOpenChange={setDrilldownOpen}
                onOpenCodeSearch={handleOpenCodeSearch}
                onOpenTemplate={handleOpenTemplate}
                onOpenDrilldown={handleOpenDrilldown}
                onOpenQuality={() => setActiveTab("quality")}
                onSearch={handleSearchRequest}
                onSelectedHitsChange={setSelectedHits}
                searchRequest={searchRequest}
                onSubmit={handleSubmit}
              />
            </TabsContent>

            <TabsContent value="templates" className="mt-0">
              <TemplatesTab
                isLoading={templates.isLoading}
                lastPayload={lastPayload}
                queryResult={queryResult}
                sourceItems={sourceItems}
                templates={templateItems}
                onCompare={handleCompareTemplate}
                onExport={(payload) => handleExport(payload, "xlsx")}
                onOpen={handleOpenTemplate}
              />
            </TabsContent>

            <TabsContent value="sources" className="mt-0">
              <SourcesTab
                error={sources.error}
                isAdmin={isAdmin}
                isImporting={importDemo.isPending}
                isLoading={sources.isLoading}
                sourceItems={sourceItems}
                totalImported={totalImported}
                totalRows={totalRows}
                totalWarnings={totalWarnings}
                onImportDemo={handleImportDemo}
              />
            </TabsContent>

            <TabsContent value="quality" className="mt-0">
              <QualityTab isLoading={issues.isLoading} issueItems={issueItems} sourceItems={sourceItems} />
            </TabsContent>

            <TabsContent value="selections" className="mt-0">
              <SelectionsTab
                history={history}
                isLoading={isLoading}
                onDelete={(id) => setHistory((items) => items.filter((item) => item.id !== id))}
                onExport={(payload) => handleExport(payload, "xlsx")}
                onReplay={(payload) => {
                  setActiveTab("constructor");
                  void handleSubmit(payload);
                }}
              />
            </TabsContent>

            <TabsContent value="export" className="mt-0">
              <ExportTab
                activeAmount={activeAmount}
                activeRows={activeRows}
                isExporting={exportMutation.isPending}
                lastExport={lastExport}
                lastPayload={lastPayload}
                metrics={metricItems}
                templates={templateItems}
                warningsCount={activeWarnings}
                onExport={(format) => handleExport(lastPayload, format)}
              />
            </TabsContent>

            <TabsContent value="assistant" className="mt-0">
              <AssistantTab activeAmount={activeAmount} activeRows={activeRows} lastPayload={lastPayload} templates={templateItems} warningsCount={activeWarnings} />
            </TabsContent>
            </div>
          </main>
          </div>
      </div>
    </Tabs>
  );
}

function BudgetLogo() {
  return (
    <Link className="flex min-w-0 items-center gap-3" to="/workspace">
      <span className="grid size-8 shrink-0 grid-cols-2 gap-1">
        <span className="rounded-[3px] bg-primary" />
        <span className="rounded-[3px] border-2 border-primary" />
        <span className="rounded-[3px] border-2 border-primary" />
        <span className="rounded-[3px] bg-primary" />
      </span>
      <span className="grid min-w-0 leading-tight">
        <span className="truncate text-base font-semibold text-slate-950">Бюджетный</span>
        <span className="truncate text-base font-semibold text-slate-950">конструктор</span>
      </span>
    </Link>
  );
}

function WorkspaceTopBar({
  isExporting,
  lastPayload,
  totalErrors,
  totalWarnings,
  onExport,
  onOpenQuality,
  onSearch
}: {
  isExporting: boolean;
  lastPayload: AnalyticsQueryPayload | null;
  totalErrors: number;
  totalWarnings: number;
  onExport: () => void;
  onOpenQuality: () => void;
  onSearch: (value: string) => void;
}) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch(value);
  }

  return (
    <header className="sticky top-0 z-30 border-b bg-card/95 backdrop-blur">
      <div className="flex min-h-[60px] items-center gap-3 px-4 sm:px-6 lg:px-7">
        <form className="flex min-w-0 flex-1 items-center gap-2 rounded-md border bg-background px-3 shadow-sm" onSubmit={submit}>
          <Search className="size-4 text-slate-500" />
          <input
            ref={inputRef}
            className="h-9 min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
            placeholder="Поиск по объектам, КЦСР, организациям, договорам..."
            value={value}
            onChange={(event) => setValue(event.target.value)}
          />
          <button type="submit" className="sr-only">Искать</button>
          <span className="hidden rounded border bg-muted px-2 py-0.5 text-xs text-muted-foreground sm:inline">Ctrl + K</span>
        </form>
        <div className="ml-auto flex shrink-0 items-center gap-3">
          <Button
            type="button"
            variant="outline"
            className="hidden border-warning/25 bg-warning/10 text-warning-foreground hover:bg-warning/15 md:inline-flex"
            onClick={onOpenQuality}
          >
            <AlertTriangle size={16} />
            {totalErrors ? "Есть ошибки" : totalWarnings ? "Есть предупреждения" : "Качество OK"}
          </Button>
          <Button
            type="button"
            variant="outline"
            className="hidden text-slate-500 lg:inline-flex"
            disabled={!lastPayload || lastPayload.date_mode !== "range" || isExporting}
            onClick={onExport}
          >
            {isExporting ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
            Быстрый экспорт
          </Button>
          <div className="hidden h-7 w-px bg-border lg:block" />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}

function CompactStat({ detail, icon: Icon, label, value }: { detail: string; icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="grid grid-cols-[2rem_minmax(0,1fr)] gap-3 rounded-md border bg-background p-3">
      <div className="flex size-8 items-center justify-center rounded-md bg-primary/10 text-primary">
        <Icon size={16} />
      </div>
      <div className="min-w-0">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="mt-0.5 truncate text-lg font-semibold">{value}</div>
        <div className="truncate text-xs text-muted-foreground">{detail}</div>
      </div>
    </div>
  );
}

function ConstructorLead({
  activeTemplateCode,
  sourceItems,
  templates,
  onCompareTemplate,
  onOpenCodeSearch,
  onOpenQuality,
  onOpenTemplate,
  onSearch
}: {
  activeTemplateCode: string;
  sourceItems: AnalyticsSource[];
  templates: AnalyticsTemplate[];
  onCompareTemplate: (templateCode: string) => void;
  onOpenCodeSearch: () => void;
  onOpenQuality: () => void;
  onOpenTemplate: (templateCode: string) => void;
  onSearch: (value: string) => void;
}) {
  const [searchValue, setSearchValue] = useState("");
  const latestSources = ["rchb", "agreements", "gz_contracts", "buau"]
    .map((sourceType) => sourceItems.filter((source) => source.source_type === sourceType).sort((a, b) => (b.period_date ?? "").localeCompare(a.period_date ?? ""))[0])
    .filter((source): source is AnalyticsSource => Boolean(source));

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch(searchValue);
  }

  return (
    <section className="grid min-w-0 gap-5">
      <div className="grid min-w-0 gap-4">
        <h1 className="text-[28px] font-semibold leading-tight tracking-normal text-slate-950">Конструктор выборок</h1>
        <form className="flex h-14 min-w-0 items-center gap-3 rounded-md border bg-card px-4 shadow-sm" onSubmit={submitSearch}>
          <Search className="size-5 shrink-0 text-slate-500" />
          <input
            className="min-w-0 flex-1 bg-transparent text-[15px] outline-none placeholder:text-slate-400"
            placeholder="Например: 6105, Тында, котельная, Ф.2025, получатель"
            value={searchValue}
            onChange={(event) => setSearchValue(event.target.value)}
          />
          <Button type="submit" variant="ghost" size="icon-sm" aria-label="Искать">
            <Search size={18} />
          </Button>
        </form>

        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-950">
            Состояние данных
            <Info className="size-4 text-muted-foreground" />
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {latestSources.map((source) => (
              <DataStatusCard key={source.id} source={source} />
            ))}
          </div>
        </div>
      </div>

      <div className="hidden">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-950">
            Быстрый выбор шаблона
            <Info className="size-4 text-muted-foreground" />
          </div>
          <div className="flex flex-wrap gap-3">
            {templates.map((template) => (
              <TemplateQuickButton
                key={template.code}
                active={template.code === activeTemplateCode}
                label={shortTemplateLabel(template)}
                onClick={() => onOpenTemplate(template.code)}
              />
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 text-sm font-semibold text-slate-950">Что можно сделать</div>
          <div className="grid gap-2 sm:grid-cols-2">
            <ActionTile icon={BarChart3} label="Построить СКК" onClick={() => onOpenTemplate("skk")} />
            <ActionTile icon={Search} label="Найти по КЦСР" onClick={onOpenCodeSearch} />
            <ActionTile icon={ArrowRight} label="Сравнить периоды" onClick={() => onCompareTemplate("skk")} />
            <ActionTile icon={Layers3} label="Показать несвязанные платежки" onClick={onOpenQuality} />
            <button
              type="button"
              className="flex h-12 items-center gap-3 rounded-md border bg-card px-4 text-left text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-muted/40 sm:col-span-2"
              onClick={onOpenQuality}
            >
              <ShieldAlert className="size-5 text-blue-600" />
              Открыть контроль качества
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function TemplateQuickButton({ active, label, onClick }: { active: boolean; label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      className={cn(
        "h-10 min-w-16 rounded-md border px-4 text-sm font-medium shadow-sm transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border bg-card text-slate-700 hover:border-primary/40 hover:bg-primary/5"
      )}
      aria-pressed={active}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function DataStatusCard({ source }: { source: AnalyticsSource }) {
  const hasIssues = source.warnings_count > 0 || source.errors_count > 0;

  return (
    <div className="grid min-h-40 gap-3 rounded-md border bg-card p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-950">
          <Database className="size-5 text-blue-600" />
          {sourceLabel(source.source_type)}
        </div>
        {source.errors_count ? <XCircleIcon /> : <CheckCircle2 className="size-5 text-success" />}
      </div>
      <div className="grid gap-1 text-sm">
        <span className="text-xs text-muted-foreground">Загружено</span>
        <span className="font-medium">{formatDate(source.period_date)}</span>
        <span className="text-xs text-muted-foreground">Строк</span>
        <span className="font-medium">{formatNumber(source.rows_imported)}</span>
      </div>
      <div className={cn("mt-auto flex items-start gap-2 text-xs", hasIssues ? "text-orange-600" : "text-success")}>
        {hasIssues ? <AlertTriangle className="mt-0.5 size-4 shrink-0" /> : <CheckCircle2 className="mt-0.5 size-4 shrink-0" />}
        <span>
          {source.errors_count
            ? `${formatNumber(source.errors_count)} ошибок импорта`
            : source.warnings_count
              ? `${formatNumber(source.warnings_count)} предупреждений`
              : "Без предупреждений"}
        </span>
      </div>
    </div>
  );
}

function XCircleIcon() {
  return <span className="flex size-5 items-center justify-center rounded-full bg-destructive/10 text-destructive">!</span>;
}

function ActionTile({ icon: Icon, label, onClick }: { icon: LucideIcon; label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      className="flex h-12 items-center gap-3 rounded-md border bg-card px-4 text-left text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-muted/40"
      onClick={onClick}
    >
      <Icon className="size-5 text-blue-600" />
      {label}
    </button>
  );
}

function ConstructorTab({
  activeWarnings,
  activeTemplateCode,
  compareRows,
  drilldownOpen,
  drilldownRows,
  isLoading,
  lastPayload,
  metrics,
  metricsLoading,
  queryResult,
  selectedHits,
  selectedRow,
  sourceItems,
  templates,
  templatesLoading,
  timelinePoints,
  onCompareTemplate,
  onDrilldownOpenChange,
  onOpenCodeSearch,
  onOpenTemplate,
  onOpenDrilldown,
  onOpenQuality,
  onSearch,
  onSelectedHitsChange,
  searchRequest,
  onSubmit
}: {
  activeWarnings: number;
  activeTemplateCode: string;
  compareRows: AnalyticsCompareRow[];
  drilldownOpen: boolean;
  drilldownRows: AnalyticsDrilldownRecord[];
  isLoading: boolean;
  lastPayload: AnalyticsQueryPayload | null;
  metrics: AnalyticsMetric[];
  metricsLoading: boolean;
  queryResult: AnalyticsQueryResponse | null;
  selectedHits: AnalyticsSearchHit[];
  selectedRow: AnalyticsQueryRow | null;
  sourceItems: AnalyticsSource[];
  templates: AnalyticsTemplate[];
  templatesLoading: boolean;
  timelinePoints: AnalyticsTimelinePoint[];
  onCompareTemplate: (templateCode: string) => void;
  onDrilldownOpenChange: (open: boolean) => void;
  onOpenCodeSearch: () => void;
  onOpenTemplate: (templateCode: string) => void;
  onOpenDrilldown: (row: AnalyticsQueryRow) => void;
  onOpenQuality: () => void;
  onSearch: (value: string) => void;
  onSelectedHitsChange: (items: AnalyticsSearchHit[]) => void;
  searchRequest: SearchRequest | null;
  onSubmit: (payload: AnalyticsQueryPayload) => void;
}) {
  return (
    <div className="grid gap-4">
      <ConstructorLead
        activeTemplateCode={activeTemplateCode}
        sourceItems={sourceItems}
        templates={templates}
        onCompareTemplate={onCompareTemplate}
        onOpenCodeSearch={onOpenCodeSearch}
        onOpenQuality={onOpenQuality}
        onOpenTemplate={onOpenTemplate}
        onSearch={onSearch}
      />

      {activeWarnings ? (
        <Alert className="border-warning/40 bg-warning/10">
          <AlertTriangle size={18} />
          <AlertTitle>Есть предупреждения качества в активной выборке</AlertTitle>
          <AlertDescription className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <span>{activeWarnings} предупреждений влияют на интерпретацию результата.</span>
            <Button type="button" variant="outline" size="sm" onClick={onOpenQuality}>
              Открыть качество данных
              <ArrowRight size={15} />
            </Button>
          </AlertDescription>
        </Alert>
      ) : null}

      <section className="grid min-w-0 gap-4 xl:grid-cols-[26rem_minmax(0,1fr)]">
        <Card className="h-fit min-w-0 overflow-hidden">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Search size={18} />
              Параметры выборки
            </CardTitle>
            <CardDescription>Поиск, шаблон, показатели и период обрабатываются текущим API аналитики.</CardDescription>
          </CardHeader>
          <CardContent className="min-w-0">
            {metricsLoading || templatesLoading ? (
              <div className="grid gap-3">
                <Skeleton className="h-10" />
                <Skeleton className="h-28" />
                <Skeleton className="h-24" />
              </div>
            ) : (
              <AnalyticsQueryForm
                activeTemplateCode={activeTemplateCode}
                metrics={metrics}
                templates={templates}
                selectedHits={selectedHits}
                isPending={isLoading}
                onSelectedHitsChange={onSelectedHitsChange}
                searchRequest={searchRequest}
                onSubmit={onSubmit}
              />
            )}
          </CardContent>
        </Card>

        <div className="min-w-0">
          <AnalyticsResults
            result={queryResult}
            timeline={timelinePoints}
            compareRows={compareRows}
            isLoading={isLoading}
            selectedRow={selectedRow}
            drilldown={drilldownRows}
            drilldownOpen={drilldownOpen}
            onDrilldownOpenChange={onDrilldownOpenChange}
            onOpenDrilldown={onOpenDrilldown}
          />
        </div>
      </section>

      {lastPayload ? (
        <div className="rounded-lg border bg-card p-4 text-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="font-medium">Текущий контекст</div>
              <div className="mt-1 text-muted-foreground">{payloadTitle(lastPayload, templates)}</div>
            </div>
            <div className="flex flex-wrap gap-2">
              {lastPayload.metrics.map((metric) => (
                <Badge key={metric} variant="muted">
                  {metricLabel(metric, metrics)}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function DynamicsTab({
  compareRows,
  metricNameByCode,
  timelinePoints
}: {
  compareRows: AnalyticsCompareRow[];
  metricNameByCode: Map<string, string>;
  timelinePoints: AnalyticsTimelinePoint[];
}) {
  if (!timelinePoints.length && !compareRows.length) {
    return (
      <EmptyState
        icon={BarChart3}
        title="Динамика появится после формирования выборки"
        description="Графики строятся только по рассчитанным данным из вкладки «Конструктор» или сравнения контрольного шаблона."
      />
    );
  }

  return (
    <div className="grid gap-4">
      {timelinePoints.length ? (
        <>
          <MetricSummary points={timelinePoints} metricNameByCode={metricNameByCode} />
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <BarChart3 size={18} />
                Динамика показателей
              </CardTitle>
              <CardDescription>Помесячные значения по активной выборке.</CardDescription>
            </CardHeader>
            <CardContent>
              <TimelineSvg points={timelinePoints} />
            </CardContent>
          </Card>
          <TimelineTable points={timelinePoints} />
        </>
      ) : null}

      {compareRows.length ? <ComparePanel rows={compareRows} /> : null}
    </div>
  );
}

function MetricSummary({ metricNameByCode, points }: { metricNameByCode: Map<string, string>; points: AnalyticsTimelinePoint[] }) {
  const totals = Array.from(
    points.reduce((map, point) => {
      map.set(point.metric_code, (map.get(point.metric_code) ?? 0) + point.amount);
      return map;
    }, new Map<string, number>())
  ).slice(0, 6);

  return (
    <section className="grid gap-3 md:grid-cols-3">
      {totals.map(([metric, value]) => (
        <div key={metric} className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="truncate text-sm font-medium">{metricNameByCode.get(metric) ?? metric}</div>
          <div className="mt-2 text-xl font-semibold">{formatMoney(value)}</div>
          <div className="mt-1 text-xs text-muted-foreground">Сумма по точкам графика</div>
        </div>
      ))}
    </section>
  );
}

function TimelineSvg({ points }: { points: AnalyticsTimelinePoint[] }) {
  const periods = Array.from(new Set(points.map((point) => point.period))).sort();
  const metrics = Array.from(new Set(points.map((point) => point.metric_code))).slice(0, 7);
  const values = points.map((point) => point.amount);
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = Math.max(max - min, 1);
  const width = 760;
  const height = 300;
  const left = 58;
  const right = 24;
  const top = 24;
  const bottom = 48;
  const chartWidth = width - left - right;
  const chartHeight = height - top - bottom;

  function x(period: string) {
    const index = periods.indexOf(period);
    if (periods.length <= 1) return left;
    return left + (index / (periods.length - 1)) * chartWidth;
  }

  function y(amount: number) {
    return top + (1 - (amount - min) / range) * chartHeight;
  }

  const pointsByMetric = new Map<string, AnalyticsTimelinePoint[]>();
  for (const metric of metrics) {
    pointsByMetric.set(metric, points.filter((point) => point.metric_code === metric).sort((a, b) => a.period.localeCompare(b.period)));
  }

  return (
    <div className="grid gap-3">
      <div className="aspect-[16/7] min-h-72 overflow-hidden rounded-md border bg-background">
        <svg aria-label="График динамики" className="size-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
          {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
            const yPos = top + tick * chartHeight;
            const amount = max - tick * range;
            return (
              <g key={tick}>
                <line stroke="currentColor" strokeDasharray="4 4" strokeOpacity="0.12" x1={left} x2={width - right} y1={yPos} y2={yPos} />
                <text fill="currentColor" fontSize="11" opacity="0.62" textAnchor="end" x={left - 10} y={yPos + 4}>
                  {formatMoney(amount).replace(",00", "")}
                </text>
              </g>
            );
          })}
          {metrics.map((metric, index) => {
            const series = pointsByMetric.get(metric) ?? [];
            const path = series.map((point) => `${x(point.period)},${y(point.amount)}`).join(" ");
            return (
              <g key={metric}>
                <polyline fill="none" points={path} stroke={CHART_COLORS[index % CHART_COLORS.length]} strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
                {series.map((point) => (
                  <circle key={`${metric}-${point.period}`} cx={x(point.period)} cy={y(point.amount)} fill="white" r="4" stroke={CHART_COLORS[index % CHART_COLORS.length]} strokeWidth="2" />
                ))}
              </g>
            );
          })}
          {periods.length ? (
            <>
              <text fill="currentColor" fontSize="12" opacity="0.7" x={left} y={height - 18}>
                {formatDate(periods[0])}
              </text>
              <text fill="currentColor" fontSize="12" opacity="0.7" textAnchor="end" x={width - right} y={height - 18}>
                {formatDate(periods[periods.length - 1])}
              </text>
            </>
          ) : null}
        </svg>
      </div>
      <div className="flex flex-wrap gap-2">
        {metrics.map((metric, index) => (
          <span key={metric} className="inline-flex items-center gap-2 rounded-md border bg-card px-2.5 py-1 text-xs">
            <span className="size-2 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />
            {points.find((point) => point.metric_code === metric)?.metric_name ?? metric}
          </span>
        ))}
      </div>
    </div>
  );
}

function TimelineTable({ points }: { points: AnalyticsTimelinePoint[] }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Точки графика</CardTitle>
        <CardDescription>Последние рассчитанные значения по месяцам и показателям.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-auto">
          <table className="w-full min-w-[42rem] text-sm">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-3 py-2 font-medium">Период</th>
                <th className="px-3 py-2 font-medium">Показатель</th>
                <th className="px-3 py-2 text-right font-medium">Сумма</th>
              </tr>
            </thead>
            <tbody>
              {points.slice(-24).map((point) => (
                <tr key={`${point.period}-${point.metric_code}`} className="border-b last:border-0">
                  <td className="px-3 py-2">{formatDate(point.period)}</td>
                  <td className="px-3 py-2">{point.metric_name}</td>
                  <td className="px-3 py-2 text-right font-semibold">{formatMoney(point.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function ComparePanel({ rows }: { rows: AnalyticsCompareRow[] }) {
  const totalDelta = rows.reduce((sum, row) => sum + row.delta, 0);
  const topRows = [...rows].sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 8);
  const maxDelta = Math.max(...topRows.map((row) => Math.abs(row.delta)), 1);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Сравнение периодов</CardTitle>
        <CardDescription>Результат сформирован через эндпоинт сравнения.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="rounded-md border bg-background p-3">
          <div className="text-sm text-muted-foreground">Общее отклонение</div>
          <div className={cn("mt-1 text-2xl font-semibold", totalDelta < 0 ? "text-destructive" : "text-success")}>{formatMoney(totalDelta)}</div>
        </div>
        <div className="grid gap-2">
          {topRows.map((row) => (
            <div key={`${row.object_key}-${row.metric_code}`} className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_10rem] sm:items-center">
              <div className="min-w-0">
                <div className="truncate text-sm font-medium">{row.object_name}</div>
                <div className="text-xs text-muted-foreground">{row.metric_name}</div>
              </div>
              <div className="grid grid-cols-[minmax(0,1fr)_6rem] items-center gap-2">
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className={cn("h-full rounded-full", row.delta < 0 ? "bg-destructive" : "bg-success")}
                    style={{ width: `${Math.max(4, (Math.abs(row.delta) / maxDelta) * 100)}%` }}
                  />
                </div>
                <div className={cn("text-right text-xs font-semibold", row.delta < 0 ? "text-destructive" : "text-success")}>{formatMoney(row.delta)}</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function TemplatesTab({
  isLoading,
  lastPayload,
  queryResult,
  sourceItems,
  templates,
  onCompare,
  onExport,
  onOpen
}: {
  isLoading: boolean;
  lastPayload: AnalyticsQueryPayload | null;
  queryResult: AnalyticsQueryResponse | null;
  sourceItems: AnalyticsSource[];
  templates: AnalyticsTemplate[];
  onCompare: (templateCode: string) => void;
  onExport: (payload: AnalyticsQueryPayload) => void;
  onOpen: (templateCode: string) => void;
}) {
  if (isLoading) {
    return (
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {templates.map((template) => {
          const active = lastPayload?.mode === "template" && lastPayload.template_code === template.code && queryResult;
          const sourcesInData = Array.from(new Set(sourceItems.map((source) => source.source_type))).slice(0, 4);
          return (
            <Card key={template.code}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-3">
                  <Badge variant="outline">{shortTemplateLabel(template)}</Badge>
                  <ListChecks className="size-5 text-muted-foreground" />
                </div>
                <CardTitle className="text-lg leading-snug">{template.name}</CardTitle>
                <CardDescription>{template.description}</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                <div className="rounded-md border bg-background p-3 text-sm">
                  <div className="text-xs text-muted-foreground">Правило</div>
                  <div className="mt-1 font-mono text-xs">{TEMPLATE_RULES[template.code] ?? template.code}</div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <div className="text-xs text-muted-foreground">Строк найдено</div>
                    <div className="mt-1 font-semibold">{active ? formatNumber(queryResult.rows.length) : "—"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Предупр.</div>
                    <div className="mt-1 font-semibold">{active ? formatNumber(queryResult.warnings.length) : "—"}</div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1">
                  {sourcesInData.map((sourceType) => (
                    <Badge key={sourceType} variant="muted">
                      {sourceLabel(sourceType)}
                    </Badge>
                  ))}
                </div>
                <div className="grid gap-2">
                  <Button type="button" size="sm" onClick={() => onOpen(template.code)}>
                    <Play size={15} />
                    Открыть
                  </Button>
                  <div className="grid grid-cols-2 gap-2">
                    <Button type="button" size="sm" variant="outline" onClick={() => onCompare(template.code)}>
                      <BarChart3 size={15} />
                      Сравнить
                    </Button>
                    <Button type="button" size="sm" variant="outline" onClick={() => onExport(createTemplatePayload(template.code))}>
                      <Download size={15} />
                      XLSX
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </section>
    </div>
  );
}

function SourcesTab({
  error,
  isAdmin,
  isImporting,
  isLoading,
  sourceItems,
  totalImported,
  totalRows,
  totalWarnings,
  onImportDemo
}: {
  error: Error | null;
  isAdmin: boolean;
  isImporting: boolean;
  isLoading: boolean;
  sourceItems: AnalyticsSource[];
  totalImported: number;
  totalRows: number;
  totalWarnings: number;
  onImportDemo: (folderPath?: string) => void;
}) {
  const [folderPath, setFolderPath] = useState("task");

  if (isLoading) {
    return (
      <div className="grid gap-3">
        <Skeleton className="h-20" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {error ? (
        <Alert variant="destructive">
          <ShieldAlert size={18} />
          <AlertTitle>Данные не загружены</AlertTitle>
          <AlertDescription>{error.message}</AlertDescription>
        </Alert>
      ) : null}

      <section className="grid gap-3 md:grid-cols-3">
        <CompactStat label="Всего строк" value={formatNumber(totalRows)} detail="В исходных файлах" icon={Layers3} />
        <CompactStat label="Импортировано" value={formatNumber(totalImported)} detail="Доступно для выборок" icon={CheckCircle2} />
        <CompactStat label="Предупреждения" value={formatNumber(totalWarnings)} detail="По всем источникам" icon={AlertTriangle} />
      </section>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="text-lg">Источники данных</CardTitle>
              <CardDescription>Файлы, периоды, объем импорта и технический профиль CSV.</CardDescription>
            </div>
            {isAdmin ? (
              <div className="grid min-w-0 gap-2 sm:w-[30rem] sm:grid-cols-[minmax(0,1fr)_auto]">
                <Input
                  aria-label="Папка импорта"
                  value={folderPath}
                  onChange={(event) => setFolderPath(event.target.value)}
                  placeholder="task или C:\\data\\budget"
                />
                <Button type="button" variant="outline" onClick={() => onImportDemo(folderPath)} disabled={isImporting}>
                  {isImporting ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />}
                  Импортировать
                </Button>
              </div>
            ) : null}
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="w-full min-w-[64rem] text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="px-3 py-2 font-medium">Источник</th>
                  <th className="px-3 py-2 font-medium">Файл</th>
                  <th className="px-3 py-2 font-medium">Период</th>
                  <th className="px-3 py-2 text-right font-medium">Строк всего</th>
                  <th className="px-3 py-2 text-right font-medium">Импортировано</th>
                  <th className="px-3 py-2 text-right font-medium">Предупр.</th>
                  <th className="px-3 py-2 text-right font-medium">Ошибки</th>
                  <th className="px-3 py-2 font-medium">Checksum</th>
                  <th className="px-3 py-2 font-medium">Профиль</th>
                </tr>
              </thead>
              <tbody>
                {sourceItems.map((source) => (
                  <tr key={source.id} className="border-b last:border-b-0">
                    <td className="px-3 py-3">
                      <Badge variant="secondary">{sourceLabel(source.source_type)}</Badge>
                    </td>
                    <td className="max-w-[20rem] truncate px-3 py-3 font-medium">{source.original_name}</td>
                    <td className="px-3 py-3 text-muted-foreground">{formatDate(source.period_date)}</td>
                    <td className="px-3 py-3 text-right">{formatNumber(source.rows_total)}</td>
                    <td className="px-3 py-3 text-right">{formatNumber(source.rows_imported)}</td>
                    <td className="px-3 py-3 text-right">{formatNumber(source.warnings_count)}</td>
                    <td className="px-3 py-3 text-right">{formatNumber(source.errors_count)}</td>
                    <td className="px-3 py-3 font-mono text-xs">{source.checksum.slice(0, 10)}...</td>
                    <td className="px-3 py-3 text-xs text-muted-foreground">
                      {sourceMetadata(source, "encoding")} · {sourceMetadata(source, "delimiter")} · строка {sourceMetadata(source, "header_row")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function QualityTab({ isLoading, issueItems, sourceItems }: { isLoading: boolean; issueItems: AnalyticsIssue[]; sourceItems: AnalyticsSource[] }) {
  const grouped = Array.from(
    issueItems.reduce((map, issue) => {
      map.set(issue.code, (map.get(issue.code) ?? 0) + 1);
      return map;
    }, new Map<string, number>())
  ).sort((a, b) => b[1] - a[1]);

  if (isLoading) {
    return (
      <div className="grid gap-3">
        <Skeleton className="h-28" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!issueItems.length) {
    return <EmptyState icon={ShieldAlert} title="Предупреждений качества нет" description="Текущий импорт не вернул ошибок или предупреждений." />;
  }

  return (
    <div className="grid gap-4">
      <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-4">
        {grouped.slice(0, 8).map(([code, count]) => (
          <div key={code} className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="truncate text-sm font-medium">{issueLabel(code)}</div>
                <div className="mt-2 text-2xl font-semibold">{formatNumber(count)}</div>
              </div>
              <AlertTriangle className="size-5 text-warning" />
            </div>
          </div>
        ))}
      </section>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Протокол качества данных</CardTitle>
          <CardDescription>Сообщения сформированы backend-проверками при импорте и построении выборок.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="w-full min-w-[62rem] text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="px-3 py-2 font-medium">Тип</th>
                  <th className="px-3 py-2 font-medium">Источник</th>
                  <th className="px-3 py-2 font-medium">Строка</th>
                  <th className="px-3 py-2 font-medium">Проверка</th>
                  <th className="px-3 py-2 font-medium">Объяснение</th>
                </tr>
              </thead>
              <tbody>
                {issueItems.map((issue, index) => {
                  const source = sourceItems.find((item) => item.id === issue.source_file_id);
                  return (
                    <tr key={`${issue.code}-${issue.row_number ?? "source"}-${index}`} className="border-b last:border-b-0">
                      <td className="px-3 py-3">
                        <Badge variant={issue.severity === "error" ? "destructive" : "secondary"}>
                          {issue.severity === "error" ? "Ошибка" : "Предупреждение"}
                        </Badge>
                      </td>
                      <td className="px-3 py-3">{source ? sourceLabel(source.source_type) : "—"}</td>
                      <td className="px-3 py-3">{issue.row_number ?? "—"}</td>
                      <td className="px-3 py-3">{issueLabel(issue.code)}</td>
                      <td className="px-3 py-3">{issue.message}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function SelectionsTab({
  history,
  isLoading,
  onDelete,
  onExport,
  onReplay
}: {
  history: SelectionHistoryItem[];
  isLoading: boolean;
  onDelete: (id: string) => void;
  onExport: (payload: AnalyticsQueryPayload) => void;
  onReplay: (payload: AnalyticsQueryPayload) => void;
}) {
  if (!history.length) {
    return <EmptyState icon={History} title="В этой сессии еще нет запусков" description="После формирования выборки здесь появятся последние параметры и результаты." />;
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Запуски текущей сессии</CardTitle>
        <CardDescription>Повторный запуск и экспорт используют сохраненные параметры запроса в браузере.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-auto">
          <table className="w-full min-w-[58rem] text-sm">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="px-3 py-2 font-medium">Выборка</th>
                <th className="px-3 py-2 font-medium">Запуск</th>
                <th className="px-3 py-2 text-right font-medium">Строк</th>
                <th className="px-3 py-2 text-right font-medium">Сумма</th>
                <th className="px-3 py-2 text-right font-medium">Предупр.</th>
                <th className="px-3 py-2 text-right font-medium">Действия</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id} className="border-b last:border-b-0">
                  <td className="max-w-[28rem] px-3 py-3">
                    <div className="truncate font-medium">{item.title}</div>
                    <div className="mt-1 text-xs text-muted-foreground">{item.payload.date_mode === "compare" ? "Сравнение периодов" : "Диапазон дат"}</div>
                  </td>
                  <td className="px-3 py-3">{formatDateTime(item.createdAt)}</td>
                  <td className="px-3 py-3 text-right">{formatNumber(item.rows)}</td>
                  <td className="px-3 py-3 text-right font-semibold">{formatMoney(item.amount)}</td>
                  <td className="px-3 py-3 text-right">{formatNumber(item.warnings)}</td>
                  <td className="px-3 py-3">
                    <div className="flex justify-end gap-1">
                      <Button type="button" variant="ghost" size="icon-sm" disabled={isLoading} onClick={() => onReplay(item.payload)} aria-label="Повторить выборку">
                        <RefreshCw size={15} />
                      </Button>
                      <Button type="button" variant="ghost" size="icon-sm" disabled={item.payload.date_mode !== "range"} onClick={() => onExport(item.payload)} aria-label="Экспортировать выборку">
                        <Download size={15} />
                      </Button>
                      <Button type="button" variant="ghost" size="icon-sm" onClick={() => onDelete(item.id)} aria-label="Удалить из истории">
                        <Trash2 size={15} />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function ExportTab({
  activeAmount,
  activeRows,
  isExporting,
  lastExport,
  lastPayload,
  metrics,
  templates,
  warningsCount,
  onExport
}: {
  activeAmount: number;
  activeRows: number;
  isExporting: boolean;
  lastExport: LastExport | null;
  lastPayload: AnalyticsQueryPayload | null;
  metrics: AnalyticsMetric[];
  templates: AnalyticsTemplate[];
  warningsCount: number;
  onExport: (format: "csv" | "xlsx") => void;
}) {
  const canExport = Boolean(lastPayload && lastPayload.date_mode === "range");
  const exportScope = lastPayload
    ? lastPayload.mode === "template"
      ? "контрольный шаблон"
      : lastPayload.object_keys?.length
        ? "выбранные объекты"
        : "поисковый запрос"
    : "—";

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_22rem]">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Экспорт активной выборки</CardTitle>
          <CardDescription>Форматы соответствуют текущему backend-экспортеру: CSV или XLSX.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          {lastPayload ? (
            <div className="rounded-md border bg-background p-4">
              <div className="text-sm text-muted-foreground">Параметры</div>
              <div className="mt-1 font-medium">{payloadTitle(lastPayload, templates)}</div>
              <div className="mt-3 grid gap-2 text-sm text-muted-foreground">
                <div>В файл попадет агрегированная таблица результата, который сейчас показан в конструкторе.</div>
                <div>Состав: {exportScope}; {activeRows ? formatNumber(activeRows) : "0"} строк; предупреждений: {formatNumber(warningsCount)}.</div>
                <div>Показатели: {lastPayload.metrics.map((metric) => metricLabel(metric, metrics)).join(", ")}.</div>
                <div>XLSX дополнительно содержит лист с предупреждениями активной выборки.</div>
              </div>
            </div>
          ) : (
            <Alert>
              <Info size={18} />
              <AlertTitle>Нет активной выборки</AlertTitle>
              <AlertDescription>Экспорт станет доступен после запуска конструктора.</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-3 md:grid-cols-3">
            <CompactStat label="Строк в выборке" value={activeRows ? formatNumber(activeRows) : "—"} detail="По последнему расчету" icon={TableProperties} />
            <CompactStat label="Сумма" value={activeRows ? formatMoney(activeAmount) : "—"} detail="Сумма активных показателей" icon={BarChart3} />
            <CompactStat label="Предупреждения" value={formatNumber(warningsCount)} detail="Попадут в XLSX при наличии" icon={AlertTriangle} />
          </div>

          <div className="flex flex-wrap gap-2">
            <Button type="button" disabled={!canExport || isExporting} onClick={() => onExport("xlsx")}>
              {isExporting ? <Loader2 className="animate-spin" size={16} /> : <FileSpreadsheet size={16} />}
              Сформировать XLSX
            </Button>
            <Button type="button" variant="outline" disabled={!canExport || isExporting} onClick={() => onExport("csv")}>
              {isExporting ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
              Скачать CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Последний экспорт</CardTitle>
          <CardDescription>Фактический результат текущей сессии.</CardDescription>
        </CardHeader>
        <CardContent>
          {lastExport ? (
            <dl className="grid gap-3 text-sm">
              <div className="flex justify-between gap-3">
                <dt className="text-muted-foreground">Время</dt>
                <dd className="font-medium">{formatDateTime(lastExport.createdAt)}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted-foreground">Формат</dt>
                <dd className="font-medium uppercase">{lastExport.format}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-muted-foreground">Размер</dt>
                <dd className="font-medium">{formatFileSize(lastExport.size)}</dd>
              </div>
            </dl>
          ) : (
            <div className="rounded-md border bg-background p-4 text-sm text-muted-foreground">Экспорт еще не запускался.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function AssistantTab({
  activeAmount,
  activeRows,
  lastPayload,
  templates,
  warningsCount
}: {
  activeAmount: number;
  activeRows: number;
  lastPayload: AnalyticsQueryPayload | null;
  templates: AnalyticsTemplate[];
  warningsCount: number;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_24rem]">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Контекст для помощника</CardTitle>
          <CardDescription>Панель показывает, какие данные можно было бы передать ИИ после подключения логики.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          <CompactStat label="Выборка" value={activeRows ? formatNumber(activeRows) : "—"} detail={lastPayload ? payloadTitle(lastPayload, templates) : "Нет активного расчета"} icon={TableProperties} />
          <CompactStat label="Сумма" value={activeRows ? formatMoney(activeAmount) : "—"} detail="По последнему результату" icon={BarChart3} />
          <CompactStat label="Качество" value={formatNumber(warningsCount)} detail="Предупреждения активной выборки" icon={ShieldAlert} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Bot size={18} />
              ИИ-помощник
            </CardTitle>
            <Badge variant="muted">Визуал</Badge>
          </div>
          <CardDescription>Функции ИИ не подключены: здесь нет сетевого запроса, изменения параметров или генерации ответа.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="rounded-md border bg-muted/35 p-3 text-sm">
            <div className="text-xs text-muted-foreground">Пользовательский запрос</div>
            <div className="mt-2">Покажи СКК по транспортным мероприятиям за 2025 год</div>
          </div>
          <div className="rounded-md border bg-background p-3 text-sm">
            <div className="font-medium">Предлагаемые параметры</div>
            <ul className="mt-2 grid gap-1 text-muted-foreground">
              <li>Шаблон: СКК</li>
              <li>Период: 01.01.2025 — 31.12.2025</li>
              <li>Показатели: лимиты, БО, касса, соглашения, контракты</li>
            </ul>
          </div>
          <div className="grid gap-2">
            <Button type="button" disabled>
              <Sparkles size={16} />
              Применить параметры
            </Button>
            <Button type="button" variant="outline" disabled>
              <MessageSquareText size={16} />
              Объяснить результат
            </Button>
          </div>
          <Input disabled placeholder="ИИ-подсказки будут доступны после подключения сервиса" />
        </CardContent>
      </Card>
    </div>
  );
}

function EmptyState({ description, icon: Icon, title }: { description: string; icon: LucideIcon; title: string }) {
  return (
    <Card>
      <CardContent className="flex min-h-64 flex-col items-center justify-center gap-3 text-center">
        <div className="flex size-11 items-center justify-center rounded-md bg-muted text-muted-foreground">
          <Icon size={22} />
        </div>
        <div>
          <h2 className="font-semibold">{title}</h2>
          <p className="mt-1 max-w-lg text-sm text-muted-foreground">{description}</p>
        </div>
      </CardContent>
    </Card>
  );
}
