import { zodResolver } from "@hookform/resolvers/zod";
import { LogIn } from "lucide-react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { useLogin } from "../../entities/user/hooks";
import { Alert, AlertDescription } from "../../shared/ui/alert";
import { Button } from "../../shared/ui/button";
import { PasswordField } from "../../shared/ui/password-field";
import { TextField } from "../../shared/ui/text-field";

const loginSchema = z.object({
  email: z.string().min(1, "Введите почту или логин."),
  password: z.string().min(1, "Введите пароль.")
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const navigate = useNavigate();
  const login = useLogin();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" }
  });

  const onSubmit = form.handleSubmit((values) => {
    login.mutate(values, {
      onSuccess: (response) => {
        navigate(response.user.roles.includes("admin") ? "/admin" : "/workspace");
      }
    });
  });

  return (
    <form className="grid gap-4" onSubmit={onSubmit}>
      <TextField
        label="Почта или логин"
        type="text"
        autoComplete="username"
        error={form.formState.errors.email?.message}
        {...form.register("email")}
      />
      <PasswordField
        label="Пароль"
        autoComplete="current-password"
        error={form.formState.errors.password?.message}
        {...form.register("password")}
      />
      {login.error ? (
        <Alert variant="destructive">
          <AlertDescription>{login.error.message}</AlertDescription>
        </Alert>
      ) : null}
      <Button className="h-11 w-full rounded-2xl" type="submit" disabled={login.isPending}>
        <LogIn size={18} />
        {login.isPending ? "Входим..." : "Войти"}
      </Button>
    </form>
  );
}
