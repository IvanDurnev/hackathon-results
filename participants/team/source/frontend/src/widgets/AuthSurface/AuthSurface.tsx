import type { ReactNode } from "react";

import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "../../shared/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../shared/ui/card";
import { Separator } from "../../shared/ui/separator";

export type AuthSurfaceFeature = {
  icon: LucideIcon;
  text: string;
};

type AuthSurfaceProps = {
  badge: string;
  title: string;
  description: string;
  cardTitle: string;
  cardDescription: string;
  footerPrompt: string;
  footerLinkTo: string;
  footerLinkLabel: string;
  panelEyebrow: string;
  panelTitle: string;
  panelDescription: string;
  panelIcon: LucideIcon;
  features: AuthSurfaceFeature[];
  children: ReactNode;
};

export function AuthSurface({
  badge,
  title,
  description,
  cardTitle,
  cardDescription,
  footerPrompt,
  footerLinkTo,
  footerLinkLabel,
  panelEyebrow,
  panelTitle,
  panelDescription,
  panelIcon: PanelIcon,
  features,
  children
}: AuthSurfaceProps) {
  return (
    <main className="mx-auto min-h-[calc(100vh-4rem)] max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(360px,430px)] lg:items-start">
        <div className="grid gap-6">
          <div className="space-y-3">
            <Badge className="w-fit" variant="secondary">
              {badge}
            </Badge>
            <div className="space-y-2">
              <h1 className="font-display text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">{title}</h1>
              <p className="max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">{description}</p>
            </div>
          </div>

          <Card className="glass-panel overflow-hidden rounded-[2rem] border-border/70 shadow-soft">
            <CardHeader className="space-y-3">
              <CardTitle className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">{cardTitle}</CardTitle>
              <CardDescription className="max-w-xl text-sm leading-6 sm:text-base">{cardDescription}</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-5 px-6 pb-6 pt-0 sm:px-8 sm:pb-8">
              {children}
              <p className="text-center text-sm text-muted-foreground">
                {footerPrompt}{" "}
                <Link className="font-medium text-primary underline-offset-4 hover:underline" to={footerLinkTo}>
                  {footerLinkLabel}
                </Link>
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="inverse-panel relative overflow-hidden rounded-[2rem] shadow-soft">
          <div className="inverse-gradient absolute inset-0 opacity-90" />
          <div className="inverse-grid absolute inset-0 opacity-15" />
          <CardContent className="relative grid h-full gap-6 px-6 py-6 sm:px-8 sm:py-8">
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="inverse-soft relative flex size-14 shrink-0 items-center justify-center overflow-hidden rounded-3xl shadow-soft">
                  <div className="inverse-gradient absolute inset-0 opacity-80" />
                  <PanelIcon className="relative" size={26} />
                </div>
                <div className="space-y-3">
                  <Badge className="inverse-chip">{panelEyebrow}</Badge>
                  <div className="space-y-2">
                    <CardTitle className="font-display text-3xl font-semibold tracking-tight leading-tight text-[var(--inverse-foreground)]">
                      {panelTitle}
                    </CardTitle>
                    <CardDescription className="inverse-muted max-w-md text-sm leading-6">
                      {panelDescription}
                    </CardDescription>
                  </div>
                </div>
              </div>
              <Separator className="bg-[var(--inverse-border)]" />
            </div>

            <div className="grid gap-3">
              {features.map((feature) => {
                const FeatureIcon = feature.icon;

                return (
                  <div
                    key={feature.text}
                    className="inverse-tile flex items-start gap-3 text-sm leading-6"
                  >
                    <FeatureIcon className="mt-0.5 shrink-0 text-primary" size={18} />
                    <p>{feature.text}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
