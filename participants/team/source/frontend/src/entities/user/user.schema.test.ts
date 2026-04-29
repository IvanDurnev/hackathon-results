import { describe, expect, it } from "vitest";

import { adminDashboardResponseSchema, authResponseSchema } from "./user.schema";

describe("user schemas", () => {
  it("parses auth response with roles", () => {
    const parsed = authResponseSchema.parse({
      user: {
        id: 1,
        email: "admin@example.com",
        username: "admin",
        display_name: null,
        active: true,
        roles: ["user", "admin"],
        avatar: {
          id: 9,
          original_name: "avatar.png",
          mime_type: "image/png",
          size_bytes: 1024,
          access_scope: "private",
          url: "http://localhost:5000/api/v1/files/9",
          created_at: "2026-04-24T00:00:00",
          updated_at: "2026-04-24T00:00:00"
        },
        created_at: "2026-04-24T00:00:00",
        updated_at: "2026-04-24T00:00:00"
      }
    });

    expect(parsed.user.roles).toContain("admin");
    expect(parsed.user.avatar?.access_scope).toBe("private");
  });

  it("parses admin metrics", () => {
    const parsed = adminDashboardResponseSchema.parse({
      metrics: {
        users: 3,
        admins: 1,
        active: 2,
        inactive: 1
      }
    });

    expect(parsed.metrics.users).toBe(3);
  });
});
