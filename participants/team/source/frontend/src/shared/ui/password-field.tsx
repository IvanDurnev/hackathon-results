import { Eye, EyeOff } from "lucide-react";
import { useId, useState, type InputHTMLAttributes } from "react";

import { cn } from "@/shared/lib/utils";

import { Button } from "./button";
import { Input } from "./input";
import { Label } from "./label";

type PasswordFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

function PasswordField({ label, error, className, id, ...props }: PasswordFieldProps) {
  const generatedId = useId();
  const inputId = id ?? props.name ?? generatedId;
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="grid gap-2">
      <Label htmlFor={inputId}>{label}</Label>
      <div className="relative">
        <Input
          id={inputId}
          type={isVisible ? "text" : "password"}
          className={cn("pr-10", error && "border-destructive focus-visible:ring-destructive", className)}
          {...props}
        />
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className="absolute right-1 top-1/2 -translate-y-1/2 rounded-md text-muted-foreground hover:bg-transparent hover:text-foreground"
          onClick={() => setIsVisible((current) => !current)}
          aria-label={isVisible ? "Скрыть пароль" : "Показать пароль"}
          aria-pressed={isVisible}
        >
          {isVisible ? <EyeOff size={16} /> : <Eye size={16} />}
        </Button>
      </div>
      {error ? <p className="text-sm font-medium text-destructive">{error}</p> : null}
    </div>
  );
}

export { PasswordField };
export type { PasswordFieldProps };
