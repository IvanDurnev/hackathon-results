import type { PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";

import { useMe } from "../entities/user/hooks";
import { Card, CardContent } from "../shared/ui/card";
import { Skeleton } from "../shared/ui/skeleton";

function LoadingState() {
  return (
    <main className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-10">
      <Card className="w-full max-w-sm">
        <CardContent className="grid gap-3 p-6">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-4/5" />
        </CardContent>
      </Card>
    </main>
  );
}

export function RequireAuth({ children }: PropsWithChildren) {
  const me = useMe();

  if (me.isLoading) return <LoadingState />;
  if (me.error || !me.data?.user) return <Navigate to="/login" replace />;

  return children;
}

export function RequireAdmin({ children }: PropsWithChildren) {
  const me = useMe();

  if (me.isLoading) return <LoadingState />;
  if (me.error || !me.data?.user) return <Navigate to="/login" replace />;
  if (!me.data.user.roles.includes("admin")) return <Navigate to="/workspace" replace />;

  return children;
}
