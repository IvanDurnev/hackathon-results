import { ArrowRight, Boxes, ShieldCheck, LockKeyhole } from "lucide-react";

import { LoginForm } from "../features/auth-login/LoginForm";
import type { AuthSurfaceFeature } from "../widgets/AuthSurface/AuthSurface";
import { AuthSurface } from "../widgets/AuthSurface/AuthSurface";

const loginFeatures: AuthSurfaceFeature[] = [
  {
    icon: ShieldCheck,
    text: "Один аккаунт для панели и рабочего интерфейса."
  },
  {
    icon: Boxes,
    text: "Права применяются после входа в систему."
  },
  {
    icon: ArrowRight,
    text: "Сессия сохраняется до выхода."
  }
];

export function LoginPage() {
  return (
    <AuthSurface
      badge="Авторизация"
      title="Вход в систему"
      description="Используйте учетную запись для доступа к панели."
      cardTitle="Доступ"
      cardDescription="Войдите, чтобы продолжить работу."
      footerPrompt="Нет аккаунта?"
      footerLinkTo="/register"
      footerLinkLabel="Создать аккаунт"
      panelEyebrow="Доступ"
      panelTitle="Единый вход"
      panelDescription="Одна учетная запись для панели и рабочего интерфейса."
      panelIcon={LockKeyhole}
      features={loginFeatures}
    >
      <LoginForm />
    </AuthSurface>
  );
}
