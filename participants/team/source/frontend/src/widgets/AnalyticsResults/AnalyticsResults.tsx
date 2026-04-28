import { AlertTriangle, ChevronDown, ChevronLeft, ChevronRight, FileText, TrendingUp } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type {
  AnalyticsCompareRow,
  AnalyticsDrilldownRecord,
  AnalyticsQueryResponse,
  AnalyticsQueryRow,
  AnalyticsTimelinePoint
} from "../../entities/analytics/analytics.schema";
import { Badge } from "../../shared/ui/badge";
import { Button } from "../../shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../shared/ui/card";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "../../shared/ui/sheet";
import { Skeleton } from "../../shared/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../shared/ui/table";

const PAGE_SIZE_OPTIONS = [10, 25, 50];
const CHART_COLORS = ["#2563eb", "#059669", "#7c3aed", "#ea580c", "#0891b2", "#64748b", "#dc2626"];

function formatMoney(value: number) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);
}

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value));
}

function sourceLabel(value: string) {
  const labels: Record<string, string> = {
    rchb: "РЧБ",
    agreements: "Соглашения",
    gz_contracts: "ГЗ договоры",
    gz_payments: "ГЗ оплаты",
    buau: "БУАУ"
  };
  return labels[value] ?? value;
}

function warningLabel(value: string) {
  const labels: Record<string, string> = {
    equal_by_line_no_amount: "Сумма распределена поровну",
    contract_amount_allocated_equally: "Сумма распределена поровну",
    payment_budget_line_missing: "Платежки без бюджетной строки",
    payment_contract_missing: "Платежки без договора",
    missing_columns: "Не хватает колонок"
  };
  return labels[value] ?? value;
}

function detailLabel(value: string) {
  const labels: Record<string, string> = {
    budget_name: "Бюджет",
    source_file: "Файл",
    posting_date: "Дата проводки",
    grantor: "Орган-субсидодатель",
    document_id: "Документ",
    reg_number: "Рег. номер",
    recipient: "Получатель",
    documentclass_id: "Класс документа",
    con_document_id: "Документ ГЗ",
    zakazchik_key: "Заказчик",
    allocation_method: "Распределение",
    platezhka_key: "Ключ платежки"
  };
  return labels[value] ?? value;
}

export function AnalyticsResults({
  result,
  timeline,
  compareRows,
  isLoading,
  selectedRow,
  drilldown,
  drilldownOpen,
  onDrilldownOpenChange,
  onOpenDrilldown
}: {
  result?: AnalyticsQueryResponse | null;
  timeline: AnalyticsTimelinePoint[];
  compareRows: AnalyticsCompareRow[];
  isLoading: boolean;
  selectedRow?: AnalyticsQueryRow | null;
  drilldown: AnalyticsDrilldownRecord[];
  drilldownOpen: boolean;
  onDrilldownOpenChange: (open: boolean) => void;
  onOpenDrilldown: (row: AnalyticsQueryRow) => void;
}) {
  const rows = result?.rows ?? [];
  const totals = result?.totals ?? {};
  const totalEntries = Object.entries(totals).filter(([, value]) => value !== 0);
  const metricNames = new Map(rows.map((row) => [row.metric_code, row.metric_name]));
  const [resultPage, setResultPage] = useState(1);
  const [resultPerPage, setResultPerPage] = useState(10);
  const [comparePage, setComparePage] = useState(1);
  const [comparePerPage, setComparePerPage] = useState(10);
  const resultTotalPages = Math.max(1, Math.ceil(rows.length / resultPerPage));
  const compareTotalPages = Math.max(1, Math.ceil(compareRows.length / comparePerPage));
  const pagedRows = useMemo(
    () => rows.slice((resultPage - 1) * resultPerPage, resultPage * resultPerPage),
    [resultPage, resultPerPage, rows]
  );
  const pagedCompareRows = useMemo(
    () => compareRows.slice((comparePage - 1) * comparePerPage, comparePage * comparePerPage),
    [comparePage, comparePerPage, compareRows]
  );

  useEffect(() => {
    setResultPage(1);
  }, [rows.length, resultPerPage]);

  useEffect(() => {
    setComparePage(1);
  }, [compareRows.length, comparePerPage]);

  if (isLoading) {
    return (
      <div className="grid gap-4">
        <div className="grid gap-3 md:grid-cols-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!result && !compareRows.length) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Результаты</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-3 md:grid-cols-4">
            {[0, 1, 2, 3].map((item) => (
              <div key={item} className="flex h-20 items-center gap-3 rounded-md border bg-background px-4">
                <div className="size-9 rounded-full bg-muted" />
                <div className="grid flex-1 gap-2">
                  <div className="h-2.5 w-20 rounded-full bg-muted" />
                  <div className="h-2.5 w-28 rounded-full bg-muted" />
                </div>
              </div>
            ))}
          </div>
          <div className="overflow-hidden rounded-md border bg-background">
            {[0, 1, 2, 3, 4].map((row) => (
              <div key={row} className="grid grid-cols-[1.5rem_repeat(7,minmax(5rem,1fr))] gap-5 border-b px-4 py-3 last:border-b-0">
                <div className="size-4 rounded border bg-card" />
                {[0, 1, 2, 3, 4, 5, 6].map((cell) => (
                  <div key={cell} className="h-2.5 rounded-full bg-muted" />
                ))}
              </div>
            ))}
          </div>
          <div className="flex min-h-40 flex-col items-center justify-center rounded-md border border-dashed bg-background px-4 text-center">
            <FileText className="size-8 text-muted-foreground" />
            <h2 className="mt-3 font-semibold text-muted-foreground">После формирования здесь появятся итоговые карточки, таблица и динамика</h2>
            <p className="mt-2 text-sm text-muted-foreground">Задайте параметры и нажмите «Сформировать».</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4">
      {totalEntries.length ? (
        <section className="grid gap-3 md:grid-cols-3">
          {totalEntries.slice(0, 6).map(([metricCode, value]) => (
            <div key={metricCode} className="rounded-lg border bg-card p-4 shadow-sm">
              <div className="text-xs font-semibold uppercase text-muted-foreground">{metricNames.get(metricCode) ?? metricCode}</div>
              <div className="mt-2 text-xl font-semibold">{formatMoney(value)}</div>
            </div>
          ))}
        </section>
      ) : null}

      {result?.warnings.length ? (
        <div className="rounded-lg border border-warning/35 bg-warning/10 p-3 text-sm text-warning-foreground">
          <div className="flex items-center gap-2 font-medium">
            <AlertTriangle size={16} />
            Предупреждения качества данных
          </div>
          <div className="mt-2 grid gap-1 text-xs">
            {result.warnings.slice(0, 4).map((warning, index) => (
              <div key={`${warning.code}-${index}`}>{warning.message}</div>
            ))}
          </div>
        </div>
      ) : null}

      {compareRows.length ? (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Сравнение периодов</CardTitle>
            <CardDescription>База, сравниваемое значение и отклонение</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-auto px-6 pt-4">
              <Table className="table-fixed">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[36%]">Объект</TableHead>
                  <TableHead className="w-[18%]">Показатель</TableHead>
                  <TableHead className="text-right">База</TableHead>
                  <TableHead className="text-right">Сравнение</TableHead>
                  <TableHead className="text-right">Дельта</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pagedCompareRows.map((row) => (
                  <TableRow key={`${row.object_key}-${row.metric_code}`}>
                    <TableCell className="max-w-0 font-medium">
                      <div className="line-clamp-2 break-words">{row.object_name}</div>
                    </TableCell>
                    <TableCell className="break-words">{row.metric_name}</TableCell>
                    <TableCell className="text-right">{formatMoney(row.base_value)}</TableCell>
                    <TableCell className="text-right">{formatMoney(row.compare_value)}</TableCell>
                    <TableCell className="text-right">{formatMoney(row.delta)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            </div>
            <PaginationFooter
              page={comparePage}
              perPage={comparePerPage}
              total={compareRows.length}
              totalPages={compareTotalPages}
              onPageChange={setComparePage}
              onPerPageChange={setComparePerPage}
            />
          </CardContent>
        </Card>
      ) : null}

      {rows.length ? (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Результат выборки</CardTitle>
            <CardDescription>{rows.length} строк по выбранным показателям</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-auto px-6 pt-4">
              <Table className="table-fixed">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[38%]">Объект</TableHead>
                  <TableHead className="w-[14%]">КЦСР</TableHead>
                  <TableHead className="w-[18%]">Показатель</TableHead>
                  <TableHead className="w-[12%]">Источник</TableHead>
                  <TableHead className="w-[14%] text-right">Сумма</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {pagedRows.map((row) => (
                  <TableRow key={row.row_id}>
                    <TableCell className="max-w-0 font-medium">
                      <div className="line-clamp-2 break-words">{row.object_name}</div>
                      {row.warning_codes.length ? (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {row.warning_codes.map((warning) => (
                            <Badge key={warning} className="max-w-full whitespace-normal text-left" variant="secondary">
                              {warningLabel(warning)}
                            </Badge>
                          ))}
                        </div>
                      ) : null}
                    </TableCell>
                    <TableCell className="break-all font-mono text-xs">{row.codes.kcsr ?? "—"}</TableCell>
                    <TableCell className="break-words">{row.metric_name}</TableCell>
                    <TableCell className="break-words">{sourceLabel(row.source_type)}</TableCell>
                    <TableCell className="whitespace-nowrap text-right font-semibold">{formatMoney(row.amount)}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        type="button"
                        size="icon-sm"
                        variant="ghost"
                        disabled={!row.drilldown_available}
                        onClick={() => onOpenDrilldown(row)}
                      >
                        <ChevronRight size={16} />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            </div>
            <PaginationFooter
              page={resultPage}
              perPage={resultPerPage}
              total={rows.length}
              totalPages={resultTotalPages}
              onPageChange={setResultPage}
              onPerPageChange={setResultPerPage}
            />
          </CardContent>
        </Card>
      ) : result ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            По выбранным условиям строк нет.
          </CardContent>
        </Card>
      ) : null}

      {timeline.length ? <TimelineDashboard points={timeline} /> : null}

      <Sheet open={drilldownOpen} onOpenChange={onDrilldownOpenChange}>
        <SheetContent className="overflow-y-auto sm:max-w-2xl">
          <SheetHeader>
            <SheetTitle>Расшифровка</SheetTitle>
            <SheetDescription>{selectedRow?.object_name}</SheetDescription>
          </SheetHeader>
          <div className="mt-6 grid gap-3">
            {drilldown.map((record, index) => (
              <div key={`${record.source_type}-${record.label}-${index}`} className="rounded-lg border bg-card p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <Badge variant="secondary">{sourceLabel(record.source_type)}</Badge>
                    <div className="mt-2 font-medium">{record.label}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{formatDate(record.event_date)}</div>
                  </div>
                  <div className="whitespace-nowrap text-sm font-semibold">{formatMoney(record.amount)}</div>
                </div>
                <dl className="mt-3 grid gap-1 text-xs text-muted-foreground">
                  {Object.entries(record.details).slice(0, 8).map(([key, value]) => (
                    <div key={key} className="grid grid-cols-[9rem_minmax(0,1fr)] gap-2">
                      <dt>{detailLabel(key)}</dt>
                      <dd className="truncate text-foreground">{String(value ?? "—")}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

function TimelineChart({ points }: { points: AnalyticsTimelinePoint[] }) {
  const max = Math.max(...points.map((point) => Math.abs(point.amount)), 1);
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp size={18} />
          Динамика
        </CardTitle>
        <CardDescription>Помесячные значения по выбранным условиям</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2">
          {points.slice(0, 40).map((point) => (
            <div key={`${point.period}-${point.metric_code}`} className="grid gap-2 sm:grid-cols-[9rem_10rem_minmax(0,1fr)_8rem] sm:items-center">
              <div className="text-xs text-muted-foreground">{formatDate(point.period)}</div>
              <div className="truncate text-sm">{point.metric_name}</div>
              <div className="h-3 overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary" style={{ width: `${Math.max(2, (Math.abs(point.amount) / max) * 100)}%` }} />
              </div>
              <div className="text-right text-xs font-medium">{formatMoney(point.amount)}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function TimelineDashboard({ points }: { points: AnalyticsTimelinePoint[] }) {
  const totals = Array.from(
    points.reduce((map, point) => {
      map.set(point.metric_code, (map.get(point.metric_code) ?? 0) + point.amount);
      return map;
    }, new Map<string, number>())
  ).slice(0, 6);

  return (
    <section className="grid gap-4">
      <section className="grid gap-3 md:grid-cols-3">
        {totals.map(([metric, value]) => (
          <div key={metric} className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="truncate text-sm font-medium">{points.find((point) => point.metric_code === metric)?.metric_name ?? metric}</div>
            <div className="mt-2 text-xl font-semibold">{formatMoney(value)}</div>
            <div className="mt-1 text-xs text-muted-foreground">Сумма по точкам графика</div>
          </div>
        ))}
      </section>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp size={18} />
            Динамика показателей
          </CardTitle>
          <CardDescription>Помесячные значения по активной выборке.</CardDescription>
        </CardHeader>
        <CardContent>
          <TimelineSvg points={points} />
        </CardContent>
      </Card>

      <TimelinePointsTable points={points} />
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

function TimelinePointsTable({ points }: { points: AnalyticsTimelinePoint[] }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Точки графика</CardTitle>
        <CardDescription>Последние рассчитанные значения по месяцам и показателям.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-auto">
          <Table className="min-w-[42rem]">
            <TableHeader>
              <TableRow>
                <TableHead>Период</TableHead>
                <TableHead>Показатель</TableHead>
                <TableHead className="text-right">Сумма</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {points.slice(-24).map((point) => (
                <TableRow key={`${point.period}-${point.metric_code}`}>
                  <TableCell>{formatDate(point.period)}</TableCell>
                  <TableCell>{point.metric_name}</TableCell>
                  <TableCell className="text-right font-semibold">{formatMoney(point.amount)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function PaginationFooter({
  total,
  page,
  perPage,
  totalPages,
  onPageChange,
  onPerPageChange
}: {
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onPerPageChange: (value: number) => void;
}) {
  const safeTotalPages = Math.max(totalPages, 1);
  const currentPage = Math.min(Math.max(page, 1), safeTotalPages);
  const start = total === 0 ? 0 : (currentPage - 1) * perPage + 1;
  const end = total === 0 ? 0 : Math.min(currentPage * perPage, total);

  return (
    <div className="flex flex-col gap-3 border-t bg-muted/10 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
      <div className="text-sm text-muted-foreground">{total > 0 ? `Показано ${start}-${end} из ${total}` : "Строки не найдены."}</div>
      <div className="flex items-center gap-2">
        <Button type="button" variant="outline" className="h-9 w-9" onClick={() => onPageChange(Math.max(1, currentPage - 1))} disabled={currentPage <= 1} aria-label="Предыдущая страница">
          <ChevronLeft size={16} />
        </Button>
        <Button type="button" className="h-9 min-w-9 px-3" disabled>
          {currentPage}
        </Button>
        <Button type="button" variant="outline" className="h-9 w-9" onClick={() => onPageChange(Math.min(safeTotalPages, currentPage + 1))} disabled={currentPage >= safeTotalPages} aria-label="Следующая страница">
          <ChevronRight size={16} />
        </Button>
        <div className="relative">
          <select
            className="h-9 appearance-none rounded-md border bg-background py-1 pl-2 pr-8 text-sm"
            value={perPage}
            onChange={(event) => onPerPageChange(Number(event.target.value))}
            aria-label="Строк на странице"
          >
            {PAGE_SIZE_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <ChevronDown aria-hidden="true" className="pointer-events-none absolute right-2 top-1/2 size-4 -translate-y-1/2 text-foreground" />
        </div>
      </div>
    </div>
  );
}
