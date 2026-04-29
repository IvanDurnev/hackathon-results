import type { InputHTMLAttributes } from "react";

import { cn } from "@/shared/lib/utils";
import { Input } from "./input";
import { Label } from "./label";

type TextFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

function TextField({ label, error, className, id, ...props }: TextFieldProps) {
  const inputId = id ?? props.name;

  return (
    <div className="grid gap-2">
      <Label htmlFor={inputId}>{label}</Label>
      <Input id={inputId} className={cn(error && "border-destructive focus-visible:ring-destructive", className)} {...props} />
      {error ? <p className="text-sm font-medium text-destructive">{error}</p> : null}
    </div>
  );
}

export { TextField };
export type { TextFieldProps };
