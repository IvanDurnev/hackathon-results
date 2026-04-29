import { zodResolver } from "@hookform/resolvers/zod";
import {
  AtSign,
  CalendarClock,
  ChevronDown,
  Clock3,
  KeyRound,
  Mail,
  PencilLine,
  Shield,
  Trash2,
  Upload,
  User
} from "lucide-react";
import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { useUploadFile } from "../entities/file/hooks";
import type { UpdateProfilePayload } from "../entities/user/api";
import { useChangePassword, useMe, useUpdateMe } from "../entities/user/hooks";
import { Alert, AlertDescription } from "../shared/ui/alert";
import { Badge } from "../shared/ui/badge";
import { Button } from "../shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../shared/ui/card";
import { PasswordField } from "../shared/ui/password-field";
import { Skeleton } from "../shared/ui/skeleton";
import { TextField } from "../shared/ui/text-field";

const profileSchema = z.object({
  username: z.string().min(3, "Минимум 3 символа."),
  display_name: z.string().trim().min(1, "Введите отображаемое имя.").max(120)
});

type ProfileFormValues = z.infer<typeof profileSchema>;

const passwordSchema = z
  .object({
    current_password: z.string().min(1, "Введите текущий пароль."),
    new_password: z.string().min(8, "Минимум 8 символов."),
    confirm_password: z.string().min(1, "Повторите новый пароль.")
  })
  .refine((values) => values.new_password === values.confirm_password, {
    path: ["confirm_password"],
    message: "Пароли не совпадают."
  });

type PasswordFormValues = z.infer<typeof passwordSchema>;

const emptyPasswordValues: PasswordFormValues = {
  current_password: "",
  new_password: "",
  confirm_password: ""
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(value));
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : null;
}

function ProfileLoading() {
  return (
    <main className="mx-auto min-h-[calc(100vh-4rem)] max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)] xl:items-start">
        <Card className="inverse-panel self-start rounded-[2rem] shadow-soft">
          <CardContent className="grid gap-6 p-5 sm:p-6 lg:p-7">
            <div className="flex items-start gap-4">
              <Skeleton className="inverse-soft size-16 rounded-[1.5rem]" />
              <div className="grid flex-1 gap-3">
                <Skeleton className="inverse-soft h-6 w-24" />
                <Skeleton className="inverse-soft h-10 w-2/3" />
                <Skeleton className="inverse-soft h-5 w-full" />
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Skeleton className="inverse-soft h-24 rounded-2xl sm:col-span-2" />
              <Skeleton className="inverse-soft h-24 rounded-2xl sm:col-span-2" />
              <Skeleton className="inverse-soft h-24 rounded-2xl" />
              <Skeleton className="inverse-soft h-24 rounded-2xl" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel overflow-hidden rounded-[2rem] border bg-card/85 shadow-soft">
          <CardHeader className="gap-2 border-b bg-muted/10 px-5 py-5 sm:px-6">
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-7 w-48" />
          </CardHeader>
          <CardContent className="grid gap-4 p-5 sm:p-6">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-36 rounded-3xl" />
            <Skeleton className="h-24 rounded-3xl" />
            <Skeleton className="h-11 w-full rounded-2xl" />
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

export function ProfilePage() {
  const me = useMe();
  const user = me.data?.user;
  const updateMe = useUpdateMe();
  const uploadFile = useUploadFile();
  const changePassword = useChangePassword();
  const avatarInputRef = useRef<HTMLInputElement | null>(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarRemoved, setAvatarRemoved] = useState(false);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(null);

  const profileForm = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: "",
      display_name: ""
    }
  });

  const passwordForm = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: emptyPasswordValues
  });

  const userId = user?.id ?? null;
  const userUsername = user?.username ?? "";
  const userDisplayName = user?.display_name?.trim() || userUsername;
  const userAvatarId = user?.avatar?.id ?? null;

  useEffect(() => {
    if (!user || isEditingProfile) {
      return;
    }

    profileForm.reset({
      username: userUsername,
      display_name: userDisplayName
    });
    passwordForm.reset(emptyPasswordValues);
    setAvatarFile(null);
    setAvatarRemoved(false);
    setShowPasswordForm(false);
    setAvatarPreviewUrl(null);
    if (avatarInputRef.current) {
      avatarInputRef.current.value = "";
    }
  }, [isEditingProfile, userAvatarId, userDisplayName, userId, userUsername]);

  useEffect(() => {
    if (!avatarFile) {
      setAvatarPreviewUrl(null);
      return;
    }

    const preview = URL.createObjectURL(avatarFile);
    setAvatarPreviewUrl(preview);
    return () => URL.revokeObjectURL(preview);
  }, [avatarFile]);

  if (me.isLoading) {
    return <ProfileLoading />;
  }

  if (!user) {
    return null;
  }

  const displayName = user.display_name?.trim() || user.username;
  const initials = displayName.slice(0, 2).toUpperCase();
  const roleLabel = user.roles.includes("admin") ? "Администратор" : "Пользователь";
  const profilePending = updateMe.isPending || uploadFile.isPending;
  const profileError = errorMessage(updateMe.error) ?? errorMessage(uploadFile.error);
  const passwordError = errorMessage(changePassword.error);
  const avatarSource = avatarRemoved ? null : avatarPreviewUrl ?? user.avatar?.url ?? null;
  const avatarStatus = avatarFile
    ? "Новое фото выбрано"
    : avatarRemoved
      ? "Фото будет удалено после сохранения"
      : user.avatar
        ? "Фото профиля загружено"
        : "Фото пока не добавлено";

  const resetDraft = () => {
    profileForm.reset({
      username: user.username,
      display_name: user.display_name?.trim() || user.username
    });
    passwordForm.reset(emptyPasswordValues);
    setAvatarFile(null);
    setAvatarRemoved(false);
    setShowPasswordForm(false);
    setAvatarPreviewUrl(null);
    updateMe.reset();
    uploadFile.reset();
    changePassword.reset();
    if (avatarInputRef.current) {
      avatarInputRef.current.value = "";
    }
  };

  const beginEdit = () => {
    resetDraft();
    setIsEditingProfile(true);
  };

  const cancelEdit = () => {
    resetDraft();
    setIsEditingProfile(false);
  };

  const togglePasswordForm = () => {
    const nextValue = !showPasswordForm;
    setShowPasswordForm(nextValue);
    changePassword.reset();
    if (!nextValue) {
      passwordForm.reset(emptyPasswordValues);
    }
  };

  const handleProfileSubmit = profileForm.handleSubmit(async (values) => {
    try {
      const payload: UpdateProfilePayload = {
        username: values.username.trim(),
        display_name: values.display_name.trim()
      };

      if (avatarFile) {
        const uploaded = await uploadFile.mutateAsync({
          file: avatarFile,
          access_scope: "public"
        });
        payload.avatar_file_id = uploaded.file.id;
      } else if (avatarRemoved) {
        payload.avatar_file_id = null;
      }

      const response = await updateMe.mutateAsync(payload);
      profileForm.reset({
        username: response.user.username,
        display_name: response.user.display_name?.trim() || response.user.username
      });
      setAvatarFile(null);
      setAvatarRemoved(false);
      setAvatarPreviewUrl(null);
      setIsEditingProfile(false);
      if (avatarInputRef.current) {
        avatarInputRef.current.value = "";
      }
      toast.success("Профиль обновлён");
    } catch {}
  });

  const handlePasswordSubmit = passwordForm.handleSubmit(async (values) => {
    try {
      await changePassword.mutateAsync({
        current_password: values.current_password,
        new_password: values.new_password
      });
      passwordForm.reset(emptyPasswordValues);
      setShowPasswordForm(false);
      changePassword.reset();
      toast.success("Пароль обновлён");
    } catch {}
  });

  const handleAvatarChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    if (!file) {
      return;
    }

    setAvatarFile(file);
    setAvatarRemoved(false);
  };

  const clearSelectedAvatar = () => {
    setAvatarFile(null);
    if (avatarInputRef.current) {
      avatarInputRef.current.value = "";
    }
  };

  const handleRemoveAvatar = () => {
    setAvatarFile(null);
    setAvatarRemoved(true);
    if (avatarInputRef.current) {
      avatarInputRef.current.value = "";
    }
  };

  const handleRestoreAvatar = () => {
    setAvatarRemoved(false);
  };

  return (
    <main className="mx-auto min-h-[calc(100vh-4rem)] max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)] xl:items-start">
        <Card className="inverse-panel relative self-start overflow-hidden rounded-[2rem] shadow-soft">
          <div className="inverse-gradient absolute inset-0 opacity-90" />
          <div className="inverse-grid absolute inset-0 opacity-15" />
          <CardContent className="relative grid gap-6 p-5 sm:p-6 lg:p-7">
            <div className="flex items-start gap-4">
              <div className="inverse-soft flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-[1.6rem] border border-[var(--inverse-border)] shadow-inner">
                {avatarSource ? (
                  <img alt={displayName} className="size-full object-cover" decoding="async" src={avatarSource} />
                ) : (
                  <User size={30} />
                )}
              </div>

              <div className="min-w-0 space-y-3">
                <Badge className="inverse-chip">Профиль</Badge>
                <div className="space-y-2">
                  <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">{displayName}</h1>
                  <p className="inverse-muted max-w-2xl text-sm leading-6 sm:text-base">
                    Основная информация аккаунта и настройки, которые видны в интерфейсе.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="inverse-tile sm:col-span-2">
                <div className="inverse-muted flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em]">
                  <AtSign size={14} />
                  Логин
                </div>
                <div className="mt-2 min-w-0 break-words text-sm font-medium">{user.username}</div>
              </div>

              <div className="inverse-tile sm:col-span-2">
                <div className="inverse-muted flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em]">
                  <Mail size={14} />
                  Почта
                </div>
                <div className="mt-2 min-w-0 break-words text-sm font-medium">{user.email}</div>
              </div>

              <div className="inverse-tile">
                <div className="inverse-muted flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em]">
                  <Shield size={14} />
                  Роль
                </div>
                <div className="mt-2 text-sm font-medium">{roleLabel}</div>
              </div>

              <div className="inverse-tile">
                <div className="inverse-muted flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em]">
                  <CalendarClock size={14} />
                  Создан
                </div>
                <div className="mt-2 text-sm font-medium">{formatDate(user.created_at)}</div>
              </div>

              <div className="inverse-tile sm:col-span-2">
                <div className="inverse-muted flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em]">
                  <Clock3 size={14} />
                  Обновлён
                </div>
                <div className="mt-2 text-sm font-medium">{formatDateTime(user.updated_at)}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel overflow-hidden rounded-[2rem] border bg-card/85 shadow-soft">
          <CardHeader className="gap-2 border-b bg-muted/10 px-5 py-5 sm:px-6">
            <CardDescription>Аккаунт</CardDescription>
            <CardTitle className="text-2xl">Редактирование профиля</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-5 p-5 sm:p-6">
            {!isEditingProfile ? (
              <div className="grid gap-4">
                <p className="text-sm leading-6 text-muted-foreground">
                  Обновите логин, отображаемое имя, фото профиля или пароль.
                </p>
                <Button className="h-11 w-full rounded-2xl sm:w-fit" type="button" onClick={beginEdit}>
                  <PencilLine size={16} />
                  Редактировать профиль
                </Button>
              </div>
            ) : (
              <div className="grid gap-5">
                <form className="grid gap-4" onSubmit={handleProfileSubmit}>
                  <TextField
                    label="Логин"
                    autoComplete="username"
                    error={profileForm.formState.errors.username?.message}
                    {...profileForm.register("username")}
                  />
                  <TextField
                    label="Отображаемое имя"
                    autoComplete="name"
                    error={profileForm.formState.errors.display_name?.message}
                    {...profileForm.register("display_name")}
                  />

                  <div className="grid gap-4 rounded-3xl border bg-muted/20 p-4">
                    <div className="flex items-start gap-4">
                      <div className="flex size-20 shrink-0 items-center justify-center overflow-hidden rounded-[1.8rem] border bg-background text-foreground shadow-sm">
                        {avatarSource ? (
                          <img alt={displayName} className="size-full object-cover" decoding="async" src={avatarSource} />
                        ) : (
                          <span className="text-xl font-semibold">{initials}</span>
                        )}
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="font-medium">Фото профиля</div>
                        <p className="mt-1 text-sm leading-6 text-muted-foreground">
                          Используется в меню, профиле и местах, где отображается аккаунт.
                        </p>
                        <p className="mt-2 text-sm font-medium">{avatarStatus}</p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        className="h-10 rounded-full"
                        onClick={() => avatarInputRef.current?.click()}
                      >
                        <Upload size={16} />
                        {avatarFile || user.avatar ? "Заменить фото" : "Загрузить фото"}
                      </Button>
                      {avatarFile ? (
                        <Button type="button" variant="ghost" className="h-10 rounded-full" onClick={clearSelectedAvatar}>
                          Убрать выбранное фото
                        </Button>
                      ) : avatarRemoved ? (
                        <Button type="button" variant="ghost" className="h-10 rounded-full" onClick={handleRestoreAvatar}>
                          Вернуть фото
                        </Button>
                      ) : user.avatar ? (
                        <Button type="button" variant="ghost" className="h-10 rounded-full" onClick={handleRemoveAvatar}>
                          <Trash2 size={16} />
                          Удалить фото
                        </Button>
                      ) : null}
                    </div>

                    <input ref={avatarInputRef} accept="image/*" className="hidden" type="file" onChange={handleAvatarChange} />
                  </div>

                  {profileError ? (
                    <Alert variant="destructive">
                      <AlertDescription>{profileError}</AlertDescription>
                    </Alert>
                  ) : null}

                  <div className="flex flex-col gap-3 sm:flex-row">
                    <Button className="h-11 flex-1 rounded-2xl" type="submit" disabled={profilePending}>
                      {profilePending ? "Сохраняем..." : "Сохранить изменения"}
                    </Button>
                    <Button
                      className="h-11 rounded-2xl sm:w-auto"
                      type="button"
                      variant="outline"
                      onClick={cancelEdit}
                      disabled={profilePending || changePassword.isPending}
                    >
                      Отменить
                    </Button>
                  </div>
                </form>

                <div className="grid gap-4 rounded-3xl border bg-muted/15 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div className="font-medium">Пароль</div>
                      <p className="mt-1 text-sm leading-6 text-muted-foreground">
                        Откройте блок, если нужно задать новый пароль для входа.
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      className="h-10 rounded-full"
                      onClick={togglePasswordForm}
                      aria-expanded={showPasswordForm}
                    >
                      <KeyRound size={16} />
                      {showPasswordForm ? "Скрыть" : "Сменить пароль"}
                      <ChevronDown className={showPasswordForm ? "rotate-180 transition-transform" : "transition-transform"} size={16} />
                    </Button>
                  </div>

                  {showPasswordForm ? (
                    <form className="grid gap-4" onSubmit={handlePasswordSubmit}>
                      <PasswordField
                        label="Текущий пароль"
                        autoComplete="current-password"
                        error={passwordForm.formState.errors.current_password?.message}
                        {...passwordForm.register("current_password")}
                      />
                      <PasswordField
                        label="Новый пароль"
                        autoComplete="new-password"
                        error={passwordForm.formState.errors.new_password?.message}
                        {...passwordForm.register("new_password")}
                      />
                      <PasswordField
                        label="Повторите новый пароль"
                        autoComplete="new-password"
                        error={passwordForm.formState.errors.confirm_password?.message}
                        {...passwordForm.register("confirm_password")}
                      />

                      {passwordError ? (
                        <Alert variant="destructive">
                          <AlertDescription>{passwordError}</AlertDescription>
                        </Alert>
                      ) : null}

                      <Button className="h-11 w-full rounded-2xl" type="submit" disabled={changePassword.isPending}>
                        <KeyRound size={18} />
                        {changePassword.isPending ? "Обновляем..." : "Обновить пароль"}
                      </Button>
                    </form>
                  ) : null}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
