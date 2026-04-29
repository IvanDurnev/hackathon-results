import { Boxes, ShieldCheck, UserPlus } from "lucide-react";

import { RegisterForm } from "../features/auth-register/RegisterForm";
import type { AuthSurfaceFeature } from "../widgets/AuthSurface/AuthSurface";
import { AuthSurface } from "../widgets/AuthSurface/AuthSurface";

const registerFeatures: AuthSurfaceFeature[] = [
  {
    icon: UserPlus,
    text: "Создайте обычный пользовательский аккаунт."
  },
  {
    icon: Boxes,
    text: "Права администратора назначаются отдельно."
  },
  {
    icon: ShieldCheck,
    text: "Профиль можно обновить позже."
  }
];

export function RegisterPage() {
  return (
    <AuthSurface
      badge="Регистрация"
      title="Создать аккаунт"
      description="Создайте учетную запись для доступа к системе."
      cardTitle="Профиль"
      cardDescription="Укажите данные и перейдите к работе."
      footerPrompt="Уже есть аккаунт?"
      footerLinkTo="/login"
      footerLinkLabel="Войти"
      panelEyebrow="Доступ"
      panelTitle="Готово к работе"
      panelDescription="Регистрация создаёт обычную учетную запись."
      panelIcon={UserPlus}
      features={registerFeatures}
    >
      <RegisterForm />
    </AuthSurface>
  );
}
