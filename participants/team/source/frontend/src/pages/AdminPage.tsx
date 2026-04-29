import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  PencilLine,
  Power,
  Search,
  Shield,
  Trash2,
  UserCog,
  UserPlus,
  Users
} from "lucide-react";
import { Fragment, useEffect, useState } from "react";
import { toast } from "sonner";

import type { User } from "../entities/user/user.schema";
import {
  useAdminDashboard,
  useAdminUsers,
  useDeleteAdminUser,
  useMe,
  useUpdateAdminUser
} from "../entities/user/hooks";
import { CreateUserForm } from "../features/admin-create-user/CreateUserForm";
import { Alert, AlertDescription } from "../shared/ui/alert";
import { Badge } from "../shared/ui/badge";
import { Button } from "../shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../shared/ui/card";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "../shared/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "../shared/ui/dropdown-menu";
import { Input } from "../shared/ui/input";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "../shared/ui/sheet";
import { Skeleton } from "../shared/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../shared/ui/table";
import { PasswordField } from "../shared/ui/password-field";
import { ToggleCard } from "../shared/ui/toggle-card";
import { useDebouncedValue } from "../shared/lib/use-debounced-value";
import { TextField } from "../shared/ui/text-field";
import { cn } from "../shared/lib/utils";

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50] as const;

type EditableUser = {
  email: string;
  username: string;
  display_name: string;
  password: string;
};

function userToEditable(user: User): EditableUser {
  return {
    email: user.email,
    username: user.username,
    display_name: user.display_name?.trim() || user.username,
    password: ""
  };
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

function RoleBadge({ user }: { user: User }) {
  return user.roles.includes("admin") ? (
    <Badge className="rounded-full px-3 text-xs" variant="default">
      Админ
    </Badge>
  ) : (
    <Badge className="rounded-full px-3 text-xs" variant="muted">
      Пользователь
    </Badge>
  );
}

function StatusBadge({ user }: { user: User }) {
  return user.active ? (
    <Badge className="rounded-full px-3 text-xs" variant="success">
      Активен
    </Badge>
  ) : (
    <Badge className="rounded-full px-3 text-xs" variant="destructive">
      Отключен
    </Badge>
  );
}

function CreatedPanel({ createdAt, className }: { createdAt: string; className?: string }) {
  return (
    <div className={cn("rounded-2xl border bg-muted/15 p-3", className)}>
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Создан</div>
      <div className="mt-2 text-sm font-medium">{formatDate(createdAt)}</div>
    </div>
  );
}

function AccountEditor({
  draft,
  setDraft,
  onSave,
  onCancel,
  isPending,
  error
}: {
  draft: EditableUser;
  setDraft: (value: EditableUser) => void;
  onSave: () => void;
  onCancel: () => void;
  isPending: boolean;
  error?: Error | null;
}) {
  return (
    <div className="grid gap-4 rounded-[1.5rem] border bg-card/80 p-4 shadow-sm">
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField
          id="admin-user-email"
          label="Почта"
          value={draft.email}
          onChange={(event) => setDraft({ ...draft, email: event.target.value })}
        />
        <TextField
          id="admin-user-username"
          label="Логин"
          value={draft.username}
          onChange={(event) => setDraft({ ...draft, username: event.target.value })}
        />
        <TextField
          id="admin-user-display-name"
          label="Отображаемое имя"
          value={draft.display_name}
          required
          pattern=".*\\S.*"
          onChange={(event) => setDraft({ ...draft, display_name: event.target.value })}
        />
        <PasswordField
          id="admin-user-password"
          label="Новый пароль"
          value={draft.password}
          onChange={(event) => setDraft({ ...draft, password: event.target.value })}
        />
      </div>

      {error ? (
        <Alert variant="destructive">
          <AlertDescription>{error.message}</AlertDescription>
        </Alert>
      ) : null}

      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" onClick={onSave} disabled={isPending} className="h-11 rounded-2xl">
          {isPending ? "Сохраняем..." : "Сохранить"}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel} className="h-11 rounded-2xl">
          Отмена
        </Button>
      </div>
    </div>
  );
}

function AccessToggles({
  user,
  isSelf,
  isPending,
  layout = "stacked",
  onActiveChange,
  onAdminChange
}: {
  user: User;
  isSelf: boolean;
  isPending: boolean;
  layout?: "stacked" | "responsive";
  onActiveChange: (checked: boolean) => void;
  onAdminChange: (checked: boolean) => void;
}) {
  return (
    <div className={layout === "responsive" ? "grid grid-cols-1 gap-2 sm:grid-cols-2" : "flex flex-col gap-2"}>
      <ToggleCard
        id={`admin-user-${user.id}-active`}
        label="Активен"
        checked={user.active}
        disabled={isSelf || isPending}
        onChange={onActiveChange}
        icon={Power}
        tone="primary"
        compact
        className={layout === "responsive" ? "min-w-0" : undefined}
      />
      <ToggleCard
        id={`admin-user-${user.id}-admin`}
        label="Админ"
        checked={user.roles.includes("admin")}
        disabled={isSelf || isPending}
        onChange={onAdminChange}
        icon={Shield}
        tone="dark"
        compact
        className={layout === "responsive" ? "min-w-0" : undefined}
      />
    </div>
  );
}

function DeleteUserDialog({
  user,
  isSelf,
  isPending,
  buttonClassName,
  onDelete
}: {
  user: User;
  isSelf: boolean;
  isPending: boolean;
  buttonClassName?: string;
  onDelete: () => void;
}) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          type="button"
          variant="destructive"
          size="sm"
          className={cn("h-10 w-full rounded-2xl", buttonClassName)}
          disabled={isSelf || isPending}
        >
          <Trash2 size={16} />
          Удалить
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Удалить аккаунт?</DialogTitle>
          <DialogDescription>
            Аккаунт {user.username} будет удалён без возможности отката.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline" className="rounded-2xl">
              Отмена
            </Button>
          </DialogClose>
          <DialogClose asChild>
            <Button type="button" variant="destructive" onClick={onDelete} disabled={isPending} className="rounded-2xl">
              Удалить
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function AccountActions({
  user,
  actions,
  layout = "stacked",
  variant = "desktop"
}: {
  user: User;
  actions: ReturnType<typeof useAccountActions>;
  layout?: "stacked" | "responsive";
  variant?: "desktop" | "mobile";
}) {
  const responsiveLayout = layout === "responsive";

  return (
    <div
      className={
        variant === "mobile"
          ? "grid gap-2"
          : responsiveLayout
            ? "ml-auto flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-end"
            : "ml-auto grid w-full max-w-[10rem] gap-2"
      }
    >
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => actions.setIsEditing(true)}
        className={cn("h-10 rounded-2xl px-4", responsiveLayout ? "w-full sm:w-auto" : "w-full")}
      >
        <PencilLine size={16} />
        Изменить
      </Button>
      <DeleteUserDialog
        user={user}
        isSelf={actions.isSelf}
        isPending={actions.deleteUser.isPending}
        buttonClassName={responsiveLayout ? "w-full px-4 sm:w-auto" : undefined}
        onDelete={actions.deleteAccount}
      />
    </div>
  );
}

function useAccountActions(user: User, currentUserId: number) {
  const updateUser = useUpdateAdminUser();
  const deleteUser = useDeleteAdminUser();
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState<EditableUser>(() => userToEditable(user));
  const isSelf = user.id === currentUserId;

  const saveDraft = () => {
    updateUser.mutate(
      {
        userId: user.id,
        payload: {
          email: draft.email,
          username: draft.username,
          display_name: draft.display_name.trim(),
          ...(draft.password ? { password: draft.password } : {})
        }
      },
      {
        onSuccess: () => {
          setDraft((current) => ({ ...current, password: "" }));
          setIsEditing(false);
          toast.success("Аккаунт обновлён");
        }
      }
    );
  };

  const setActive = (active: boolean) => {
    updateUser.mutate(
      { userId: user.id, payload: { active } },
      { onSuccess: () => toast.success(active ? "Аккаунт активирован" : "Аккаунт отключён") }
    );
  };

  const setAdmin = (isAdmin: boolean) => {
    updateUser.mutate(
      { userId: user.id, payload: { is_admin: isAdmin } },
      { onSuccess: () => toast.success(isAdmin ? "Роль администратора выдана" : "Роль администратора снята") }
    );
  };

  const deleteAccount = () => {
    if (isSelf) return;
    deleteUser.mutate(user.id, { onSuccess: () => toast.success("Аккаунт удалён") });
  };

  return {
    updateUser,
    deleteUser,
    isEditing,
    setIsEditing,
    draft,
    setDraft,
    isSelf,
    saveDraft,
    setActive,
    setAdmin,
    deleteAccount
  };
}

function AccountEditorSheet({ user, actions }: { user: User; actions: ReturnType<typeof useAccountActions> }) {
  return (
    <Sheet open={actions.isEditing} onOpenChange={actions.setIsEditing}>
      <SheetContent className="overflow-y-auto sm:max-w-xl">
        <SheetHeader className="space-y-2">
          <SheetDescription>Редактирование учетной записи</SheetDescription>
          <SheetTitle>{user.username}</SheetTitle>
        </SheetHeader>
        <div className="mt-6 grid gap-4">
          <AccountEditor
            draft={actions.draft}
            setDraft={actions.setDraft}
            onSave={actions.saveDraft}
            onCancel={() => actions.setIsEditing(false)}
            isPending={actions.updateUser.isPending}
            error={actions.updateUser.error}
          />

          <div className="grid gap-3 rounded-[1.5rem] border bg-muted/10 p-4 shadow-sm">
            <div>
              <div className="text-sm font-semibold text-foreground">Права и состояние</div>
              <p className="mt-1 text-sm leading-5 text-muted-foreground">
                Эти параметры применяются сразу, без сохранения формы профиля.
              </p>
            </div>
            <AccessToggles
              user={user}
              isSelf={actions.isSelf}
              isPending={actions.updateUser.isPending}
              layout="responsive"
              onActiveChange={actions.setActive}
              onAdminChange={actions.setAdmin}
            />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

function AccountUserCell({ user }: { user: User }) {
  const displayName = user.display_name?.trim();

  return (
    <TableCell className="align-top">
      <div className="flex items-start gap-3">
        <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
          {user.username.slice(0, 2).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate font-medium text-foreground">{user.username}</div>
          <div className="truncate text-sm text-muted-foreground">{displayName || "Без отображаемого имени"}</div>
        </div>
      </div>
    </TableCell>
  );
}

function AccountRowWide({ user, currentUserId }: { user: User; currentUserId: number }) {
  const actions = useAccountActions(user, currentUserId);

  return (
    <Fragment>
      <TableRow>
        <AccountUserCell user={user} />
        <TableCell className="align-top text-sm text-muted-foreground">
          <div className="max-w-64 truncate">{user.email}</div>
        </TableCell>
        <TableCell className="align-top">
          <RoleBadge user={user} />
        </TableCell>
        <TableCell className="align-top">
          <StatusBadge user={user} />
        </TableCell>
        <TableCell className="align-top whitespace-nowrap text-sm text-muted-foreground">{formatDate(user.created_at)}</TableCell>
        <TableCell className="align-top">
          <AccountActions user={user} actions={actions} />
        </TableCell>
      </TableRow>

      <AccountEditorSheet user={user} actions={actions} />

      {actions.deleteUser.error ? (
        <TableRow>
          <TableCell colSpan={6} className="pb-4 pt-0">
            <Alert variant="destructive">
              <AlertDescription>{actions.deleteUser.error.message}</AlertDescription>
            </Alert>
          </TableCell>
        </TableRow>
      ) : null}
    </Fragment>
  );
}

function AccountMobileCard({ user, currentUserId }: { user: User; currentUserId: number }) {
  const actions = useAccountActions(user, currentUserId);
  const displayName = user.display_name?.trim();

  return (
    <Card className="mobile-scroll-skip overflow-hidden rounded-[1.75rem] border-border/70 bg-card/90 shadow-soft">
      <CardContent className="p-0">
        <div className="grid md:grid-cols-[minmax(0,1fr)_12rem]">
          <div className="relative min-w-0 p-4 sm:p-5 lg:p-6">
            <div aria-hidden="true" className="absolute left-0 top-5 h-16 w-1 rounded-r-full bg-primary/60" />

            <div className="flex min-w-0 items-start gap-4">
              <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-sm font-bold text-primary shadow-inner">
                {user.username.slice(0, 2).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <div className="truncate text-base font-semibold tracking-tight text-foreground">{user.username}</div>
                <div className="truncate text-sm text-muted-foreground">{displayName || "Без отображаемого имени"}</div>
                <div className="mt-3 inline-flex max-w-full rounded-full border bg-muted/15 px-3 py-1 text-sm text-muted-foreground">
                  <span className="min-w-0 truncate">{user.email}</span>
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <CreatedPanel createdAt={user.created_at} className="bg-background/60" />

              <div className="rounded-2xl border bg-background/60 p-3">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Профиль</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  <StatusBadge user={user} />
                  <RoleBadge user={user} />
                </div>
              </div>
            </div>
          </div>

          <div className="grid gap-4 border-t bg-muted/10 p-4 sm:p-5 md:content-between md:border-l md:border-t-0">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Действия</div>
              <p className="mt-1 text-sm leading-5 text-muted-foreground">Профиль, роль и статус.</p>
            </div>

            <AccountActions user={user} actions={actions} variant="mobile" />
          </div>
        </div>

        <AccountEditorSheet user={user} actions={actions} />

        {actions.deleteUser.error ? (
          <div className="border-t p-4 sm:p-5">
            <Alert variant="destructive">
              <AlertDescription>{actions.deleteUser.error.message}</AlertDescription>
            </Alert>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function CreateUserSheet({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="overflow-y-auto sm:max-w-xl">
        <SheetHeader className="space-y-2">
          <SheetDescription>Создание учетной записи</SheetDescription>
          <SheetTitle>Новый пользователь</SheetTitle>
        </SheetHeader>
        <div className="mt-6">
          <CreateUserForm />
        </div>
      </SheetContent>
    </Sheet>
  );
}

function PageSizeMenu({
  perPage,
  onChange
}: {
  perPage: number;
  onChange: (value: number) => void;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button type="button" variant="outline" className="h-10 rounded-2xl px-4">
          {perPage} / стр.
          <ChevronDown size={14} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {PAGE_SIZE_OPTIONS.map((option) => (
          <DropdownMenuItem key={option} onSelect={() => onChange(option)}>
            {option} / стр.
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function TableSkeletonRowsWide() {
  return Array.from({ length: 3 }).map((_, index) => (
    <TableRow key={index}>
      <TableCell className="align-top">
        <div className="flex items-center gap-3">
          <Skeleton className="size-11 rounded-full" />
          <div className="grid gap-2">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-3 w-40" />
          </div>
        </div>
      </TableCell>
      <TableCell className="align-top">
        <Skeleton className="h-4 w-40" />
      </TableCell>
      <TableCell className="align-top">
        <Skeleton className="h-6 w-20 rounded-full" />
      </TableCell>
      <TableCell className="align-top">
        <Skeleton className="h-6 w-20 rounded-full" />
      </TableCell>
      <TableCell className="align-top">
        <Skeleton className="h-4 w-28" />
      </TableCell>
      <TableCell className="align-top">
        <div className="flex justify-end gap-2">
          <Skeleton className="h-10 w-28 rounded-2xl" />
          <Skeleton className="h-10 w-20 rounded-2xl" />
        </div>
      </TableCell>
    </TableRow>
  ));
}

function CardSkeletonRows() {
  return Array.from({ length: 3 }).map((_, index) => (
    <Card key={index} className="mobile-scroll-skip overflow-hidden rounded-[1.75rem] border-border/70 bg-card/90 shadow-soft">
      <CardContent className="p-0">
        <div className="grid md:grid-cols-[minmax(0,1fr)_12rem]">
          <div className="p-4 sm:p-5 lg:p-6">
            <div className="flex items-start gap-4">
              <Skeleton className="size-12 rounded-2xl" />
              <div className="min-w-0 flex-1 space-y-2">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-8 w-full max-w-sm rounded-full" />
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <Skeleton className="h-20 rounded-2xl" />
              <Skeleton className="h-20 rounded-2xl" />
            </div>
          </div>

          <div className="grid gap-4 border-t bg-muted/10 p-4 sm:p-5 md:border-l md:border-t-0">
            <div className="space-y-2">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-4 w-28" />
            </div>
            <div className="grid gap-2">
              <Skeleton className="h-10 rounded-2xl" />
              <Skeleton className="h-10 rounded-2xl" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  ));
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
      <div className="text-sm text-muted-foreground">
        {total > 0 ? `Показано ${start}–${end} из ${total}` : "Аккаунты не найдены."}
      </div>

      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          className="h-10 w-10 rounded-2xl"
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage <= 1}
          aria-label="Предыдущая страница"
        >
          <ChevronLeft size={16} />
        </Button>

        <Button type="button" className="h-10 min-w-10 rounded-2xl px-4" disabled>
          {currentPage}
        </Button>

        <Button
          type="button"
          variant="outline"
          className="h-10 w-10 rounded-2xl"
          onClick={() => onPageChange(Math.min(safeTotalPages, currentPage + 1))}
          disabled={currentPage >= safeTotalPages}
          aria-label="Следующая страница"
        >
          <ChevronRight size={16} />
        </Button>

        <PageSizeMenu perPage={perPage} onChange={onPerPageChange} />
      </div>
    </div>
  );
}

export function AdminPage() {
  const [searchValue, setSearchValue] = useState("");
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const me = useMe();
  const currentUser = me.data?.user;
  const isAdmin = Boolean(currentUser?.roles.includes("admin"));
  const debouncedSearchValue = useDebouncedValue(searchValue, 300);
  const users = useAdminUsers(debouncedSearchValue, page, perPage, isAdmin);
  const dashboard = useAdminDashboard(isAdmin);

  const metrics = dashboard.data?.metrics;
  const userItems = users.data?.items ?? [];
  const pagination = users.data?.pagination;
  const currentUserId = currentUser?.id ?? 0;
  const currentUserLabel = currentUser?.display_name?.trim() || currentUser?.username || "Пользователь";
  const currentUserEmail = currentUser?.email ?? "Нет активной сессии";
  const total = pagination?.total ?? 0;
  const totalPages = pagination?.pages ?? 1;

  useEffect(() => {
    if (pagination && pagination.pages > 0 && page > pagination.pages) {
      setPage(pagination.pages);
    }
  }, [page, pagination]);

  const heroNotes = [
    "Права и статусы меняются сразу.",
    "Только учетные записи, роли и доступ."
  ];

  const metricItems = [
    { label: "Всего пользователей", value: metrics?.users ?? 0, icon: Users, tone: "text-primary" },
    { label: "Администраторы", value: metrics?.admins ?? 0, icon: Shield, tone: "text-success" },
    { label: "Отключены", value: metrics?.inactive ?? 0, icon: UserCog, tone: "text-destructive" }
  ];

  const handleSearchChange = (value: string) => {
    setSearchValue(value);
    setPage(1);
  };

  const handlePerPageChange = (value: number) => {
    setPerPage(value);
    setPage(1);
  };

  return (
    <main className="mx-auto min-h-[calc(100vh-4rem)] max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <div className="grid gap-6">
        <section className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(320px,0.9fr)] xl:items-start">
          <Card className="overflow-hidden rounded-[2rem] border bg-card/85 shadow-soft">
            <CardContent className="grid gap-5 p-5 sm:p-6 lg:p-7">
              <div className="space-y-3">
                <Badge variant="secondary" className="w-fit">
                  Управление доступом
                </Badge>
                <div className="space-y-3">
                  <h1 className="font-display text-4xl font-semibold tracking-tight">Аккаунты</h1>
                  <p className="max-w-3xl text-sm leading-6 text-muted-foreground sm:text-base">
                    Управление пользователями и правами доступа.
                  </p>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {heroNotes.map((note, index) => (
                  <div key={note} className="rounded-2xl border bg-muted/15 p-3">
                    <div className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">0{index + 1}</div>
                    <p className="mt-2 text-sm leading-5 text-muted-foreground">{note}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="inverse-panel relative overflow-hidden rounded-[2rem] shadow-soft">
            <div className="inverse-gradient absolute inset-0 opacity-90" />
            <div className="inverse-grid absolute inset-0 opacity-15" />
            <CardContent className="relative grid gap-4 p-5 sm:p-6 lg:p-7">
              <div className="flex items-start gap-4">
                <div className="inverse-soft flex size-11 shrink-0 items-center justify-center rounded-2xl">
                  <Users size={20} />
                </div>
                <div className="space-y-2">
                  <Badge className="inverse-chip">Админ-панель</Badge>
                  <h2 className="font-display text-3xl font-semibold tracking-tight">Админ</h2>
                  <p className="inverse-muted text-sm leading-6">Создание, редактирование и контроль доступа.</p>
                </div>
              </div>

              <div className="grid gap-3">
                <div className="inverse-tile">
                  <div className="inverse-muted text-xs font-semibold uppercase tracking-[0.18em]">Сеанс</div>
                  <div className="mt-2 text-sm font-medium">{currentUserLabel}</div>
                  <p className="inverse-muted mt-1 text-sm">{currentUserEmail}</p>
                </div>
              </div>

            </CardContent>
          </Card>
        </section>

        <section className="grid gap-3 sm:grid-cols-3">
          {metricItems.map((item) => {
            const Icon = item.icon;

            return (
              <Card key={item.label} className="glass-panel rounded-[1.75rem] border-border/70 shadow-soft">
                <CardContent className="flex min-h-24 items-start justify-between gap-3 p-5 sm:p-6">
                  <div>
                    <div className="text-sm text-muted-foreground">{item.label}</div>
                    <div className="mt-1 text-3xl font-semibold tracking-tight">{item.value}</div>
                  </div>
                  <Icon className={item.tone} size={24} />
                </CardContent>
              </Card>
            );
          })}
        </section>

        <Card id="accounts" className="overflow-hidden rounded-[2rem] border bg-card/85 shadow-soft">
          <CardHeader className="gap-4 border-b bg-muted/10 px-5 py-5 sm:px-6">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
              <div>
                <CardTitle className="text-xl">Список аккаунтов</CardTitle>
                <CardDescription className="mt-1">
                  Таблица пользователей с пагинацией и поиском.
                </CardDescription>
              </div>
              <div className="flex w-full flex-col gap-3 sm:flex-row xl:max-w-3xl xl:items-center">
                <label className="flex h-11 flex-1 items-center gap-2 rounded-2xl border bg-background/80 px-3 text-sm shadow-sm">
                  <Search className="size-4 shrink-0 text-muted-foreground" />
                  <Input
                    className="border-0 bg-transparent p-0 shadow-none focus-visible:ring-0"
                    value={searchValue}
                    onChange={(event) => handleSearchChange(event.target.value)}
                    placeholder="Поиск по имени, email или роли..."
                  />
                </label>
                <Button type="button" onClick={() => setIsCreateOpen(true)} className="h-11 rounded-2xl whitespace-nowrap">
                  <UserPlus size={16} />
                  Создать пользователя
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-0">
            {users.error ? (
              <div className="px-5 pt-5 sm:px-6">
                <Alert variant="destructive">
                  <AlertDescription>{users.error.message}</AlertDescription>
                </Alert>
              </div>
            ) : null}

            <div className="grid gap-3 p-4 sm:p-5 lg:hidden">
              {users.isLoading
                ? CardSkeletonRows()
                : userItems.length > 0
                  ? userItems.map((user) => <AccountMobileCard key={user.id} user={user} currentUserId={currentUserId} />)
                  : null}

              {!users.isLoading && userItems.length === 0 ? (
                <div className="rounded-[1.5rem] border border-dashed bg-card/85 p-6 text-center text-sm text-muted-foreground">
                  Аккаунты не найдены.
                </div>
              ) : null}
            </div>

            <Table className="hidden table-auto lg:table [&_td]:px-3 [&_th]:px-3">
              <TableHeader>
                <TableRow className="bg-muted/20 hover:bg-muted/20">
                  <TableHead className="w-[25%]">Пользователь</TableHead>
                  <TableHead className="w-[21%]">Email</TableHead>
                  <TableHead className="w-[13%]">Роль</TableHead>
                  <TableHead className="w-[11%]">Статус</TableHead>
                  <TableHead className="w-[14%]">Создан</TableHead>
                  <TableHead className="w-[16%] text-right">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.isLoading ? (
                  <TableSkeletonRowsWide />
                ) : userItems.length > 0 ? (
                  userItems.map((user) => <AccountRowWide key={user.id} user={user} currentUserId={currentUserId} />)
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="py-14 text-center text-sm text-muted-foreground">
                      Аккаунты не найдены.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>

            <PaginationFooter
              total={total}
              page={pagination?.page ?? page}
              perPage={pagination?.per_page ?? perPage}
              totalPages={totalPages}
              onPageChange={setPage}
              onPerPageChange={handlePerPageChange}
            />
          </CardContent>
        </Card>
      </div>

      <CreateUserSheet open={isCreateOpen} onOpenChange={setIsCreateOpen} />
    </main>
  );
}
