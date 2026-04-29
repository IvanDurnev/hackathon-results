import { describe, expect, it } from "vitest";

import { analyticsQueryResponseSchema } from "./analytics.schema";

describe("analytics schemas", () => {
  it("parses numeric analytics response", () => {
    const parsed = analyticsQueryResponseSchema.parse({
      columns: [{ key: "object_name", title: "Объект" }],
      rows: [
        {
          row_id: "row-1",
          object_key: "kcsr:1320261051",
          object_name: "Мероприятие",
          metric_code: "LIMITS",
          metric_name: "Доведенные лимиты",
          amount: 1000,
          source_type: "rchb",
          codes: { kcsr: "1320261051" },
          warning_codes: [],
          drilldown_available: true
        }
      ],
      totals: { LIMITS: 1000 },
      warnings: []
    });

    expect(parsed.rows[0].amount).toBe(1000);
    expect(parsed.totals.LIMITS).toBe(1000);
  });
});
