import { zodResolver } from "@hookform/resolvers/zod";
import { Power, Shield, UserPlus } from "lucide-react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { useCreateAdminUser } from "../../entities/user/hooks";
import { Alert, AlertDescription } from "../../shared/ui/alert";
import { Button } from "../../shared/ui/button";
import { PasswordField } from "../../shared/ui/password-field";
import { ToggleCard } from "../../shared/ui/toggle-card";
import { TextField } from "../../shared/ui/text-field";

const createUserSchema = z.object({
  email: z.string().email("Введите корректную почту."),
  username: z.string().min(3, "Минимум 3 символа."),
  display_name: z.string().trim().min(1, "Введите отображаемое имя."),
  password: z.string().min(8, "Минимум 8 символов."),
  active: z.boolean(),
  is_admin: z.boolean()
});

type CreateUserValues = z.infer<typeof createUserSchema>;

export function CreateUserForm() {
  const createUser = useCreateAdminUser();
  const form = useForm<CreateUserValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: "",
      username: "",
      display_name: "",
      password: "",
      active: true,
      is_admin: false
    }
  });

  const onSubmit = form.handleSubmit((values) => {
    createUser.mutate(values, {
      onSuccess: () => {
        form.reset();
        toast.success("Пользователь создан");
      }
    });
  });

  return (
    <form className="grid gap-3" onSubmit={onSubmit}>
      <TextField label="Почта" type="email" error={form.formState.errors.email?.message} {...form.register("email")} />
      <TextField label="Логин" error={form.formState.errors.username?.message} {...form.register("username")} />
      <TextField
        label="Отображаемое имя"
        error={form.formState.errors.display_name?.message}
        {...form.register("display_name")}
      />
      <PasswordField
        label="Временный пароль"
        error={form.formState.errors.password?.message}
        {...form.register("password")}
      />
      <div className="grid gap-2 sm:grid-cols-2">
        <Controller
          control={form.control}
          name="active"
          render={({ field }) => (
            <ToggleCard
              id="admin-create-user-active"
              label="Активен"
              checked={field.value}
              onChange={field.onChange}
              icon={Power}
              tone="primary"
            />
          )}
        />
        <Controller
          control={form.control}
          name="is_admin"
          render={({ field }) => (
            <ToggleCard
              id="admin-create-user-admin"
              label="Админ"
              checked={field.value}
              onChange={field.onChange}
              icon={Shield}
              tone="dark"
            />
          )}
        />
      </div>
      {createUser.error ? (
        <Alert variant="destructive">
          <AlertDescription>{createUser.error.message}</AlertDescription>
        </Alert>
      ) : null}
      <Button className="h-11 w-full rounded-2xl" type="submit" disabled={createUser.isPending}>
        <UserPlus size={18} />
        {createUser.isPending ? "Создаем..." : "Создать пользователя"}
      </Button>
    </form>
  );
}
