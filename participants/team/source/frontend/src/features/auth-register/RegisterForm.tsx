import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus } from "lucide-react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { useRegister } from "../../entities/user/hooks";
import { Alert, AlertDescription } from "../../shared/ui/alert";
import { Button } from "../../shared/ui/button";
import { PasswordField } from "../../shared/ui/password-field";
import { TextField } from "../../shared/ui/text-field";

const registerSchema = z.object({
  email: z.string().email("Введите корректную почту."),
  username: z.string().min(3, "Минимум 3 символа."),
  display_name: z.string().trim().min(1, "Введите отображаемое имя."),
  password: z.string().min(8, "Минимум 8 символов.")
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const navigate = useNavigate();
  const register = useRegister();
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", username: "", display_name: "", password: "" }
  });

  const onSubmit = form.handleSubmit((values) => {
    register.mutate(values, { onSuccess: () => navigate("/workspace") });
  });

  return (
    <form className="grid gap-4" onSubmit={onSubmit}>
      <TextField label="Почта" type="email" error={form.formState.errors.email?.message} {...form.register("email")} />
      <TextField label="Логин" error={form.formState.errors.username?.message} {...form.register("username")} />
      <TextField label="Отображаемое имя" error={form.formState.errors.display_name?.message} {...form.register("display_name")} />
      <PasswordField
        label="Пароль"
        error={form.formState.errors.password?.message}
        {...form.register("password")}
      />
      {register.error ? (
        <Alert variant="destructive">
          <AlertDescription>{register.error.message}</AlertDescription>
        </Alert>
      ) : null}
      <Button className="h-11 w-full rounded-2xl" type="submit" disabled={register.isPending}>
        <UserPlus size={18} />
        {register.isPending ? "Создаем..." : "Создать аккаунт"}
      </Button>
    </form>
  );
}
