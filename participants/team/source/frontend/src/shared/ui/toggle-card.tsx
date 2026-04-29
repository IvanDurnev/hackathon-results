import type { LucideIcon } from "lucide-react";

import { cn } from "@/shared/lib/utils";

import { Label } from "./label";

const toggleCardToneStyles = {
  primary: {
    checked:
      "border-primary/30 bg-primary/10 text-foreground shadow-[0_18px_42px_-30px_rgba(59,130,246,0.55)]",
    unchecked: "border-border bg-background/80 text-muted-foreground hover:border-primary/20 hover:bg-muted/20",
    iconChecked: "border-transparent bg-primary text-primary-foreground shadow-sm",
    iconUnchecked: "border-border bg-background text-muted-foreground",
    trackChecked: "bg-primary",
    labelChecked: "text-foreground",
    labelUnchecked: "text-foreground",
    descriptionChecked: "text-foreground/70",
    descriptionUnchecked: "text-muted-foreground"
  },
  amber: {
    checked:
      "border-amber-500/30 bg-amber-500/10 text-foreground shadow-[0_18px_42px_-30px_rgba(245,158,11,0.45)]",
    unchecked: "border-border bg-background/80 text-muted-foreground hover:border-amber-500/20 hover:bg-muted/20",
    iconChecked: "border-transparent bg-amber-500 text-white shadow-sm",
    iconUnchecked: "border-border bg-background text-muted-foreground",
    trackChecked: "bg-amber-500",
    labelChecked: "text-foreground",
    labelUnchecked: "text-foreground",
    descriptionChecked: "text-foreground/70",
    descriptionUnchecked: "text-muted-foreground"
  },
  dark: {
    checked:
      "inverse-panel shadow-[0_18px_42px_-30px_rgba(15,23,42,0.65)]",
    unchecked: "border-border bg-background/80 text-muted-foreground hover:border-foreground/20 hover:bg-muted/20",
    iconChecked: "border-transparent inverse-soft shadow-sm",
    iconUnchecked: "border-border bg-background text-muted-foreground",
    trackChecked: "bg-[var(--inverse-subtle)]",
    labelChecked: "text-[var(--inverse-foreground)]",
    labelUnchecked: "text-foreground",
    descriptionChecked: "text-[var(--inverse-muted)]",
    descriptionUnchecked: "text-muted-foreground"
  }
} as const;

type ToggleCardTone = keyof typeof toggleCardToneStyles;

type ToggleCardProps = {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
  icon: LucideIcon;
  tone?: ToggleCardTone;
  compact?: boolean;
  className?: string;
};

function ToggleCard({
  id,
  label,
  description,
  checked,
  disabled,
  onChange,
  icon: Icon,
  tone = "primary",
  compact = false,
  className
}: ToggleCardProps) {
  const styles = toggleCardToneStyles[tone];

  return (
    <Label
      htmlFor={id}
      className={cn(
        "group relative flex w-full cursor-pointer items-center gap-3 overflow-hidden rounded-2xl border px-3 py-3 text-left shadow-sm transition-all duration-200 focus-within:ring-2 focus-within:ring-ring/30 focus-within:ring-offset-2 focus-within:ring-offset-background",
        compact ? "min-h-14" : "min-h-16",
        checked ? styles.checked : styles.unchecked,
        disabled && "cursor-not-allowed opacity-70",
        className
      )}
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
        className="sr-only"
      />

      <span
        aria-hidden="true"
        className={cn(
          "flex shrink-0 items-center justify-center rounded-xl border transition-all duration-200",
          compact ? "size-9" : "size-10",
          checked ? styles.iconChecked : styles.iconUnchecked
        )}
      >
        <Icon size={compact ? 16 : 18} />
      </span>

      <span className="min-w-0 flex-1">
        <span
          className={cn(
            "block font-medium",
            compact ? "text-[0.8rem]" : "text-sm",
            checked ? styles.labelChecked : styles.labelUnchecked
          )}
        >
          {label}
        </span>
        {description ? (
          <span
            className={cn(
              "block text-xs leading-4",
              checked ? styles.descriptionChecked : styles.descriptionUnchecked
            )}
          >
            {description}
          </span>
        ) : null}
      </span>

      <span
        aria-hidden="true"
        className={cn(
          "relative inline-flex shrink-0 items-center rounded-full p-1 transition-colors duration-200",
          compact ? "h-7 w-12" : "h-8 w-14",
          checked ? styles.trackChecked : "bg-muted/80"
        )}
      >
        <span
          className={cn(
            "rounded-full bg-background shadow-sm transition-transform duration-200",
            compact ? "size-5" : "size-6",
            checked ? (compact ? "translate-x-5" : "translate-x-6") : "translate-x-0"
          )}
        />
      </span>
    </Label>
  );
}

export { ToggleCard };
export type { ToggleCardProps, ToggleCardTone };
