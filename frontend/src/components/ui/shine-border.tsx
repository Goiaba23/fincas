import { type ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Check, Flame } from "lucide-react";
import { cn } from "@/lib/utils";

type ShineBorderProps = {
  children: ReactNode;
  className?: string;
  borderWidth?: number;
  duration?: number;
};

function ShineBorder({ children, className, borderWidth = 2, duration = 3 }: ShineBorderProps) {
  return (
    <div className={cn("relative rounded-3xl", className)} style={{ padding: borderWidth }}>
      <div
        className="absolute inset-0 rounded-3xl"
        style={{
          padding: borderWidth,
          background: "conic-gradient(from 0deg, #3b82f6, #ef4444, #14b8a6, #3b82f6)",
          WebkitMask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
          animation: `spin ${duration}s linear infinite`,
        }}
      />
      <div className="relative rounded-3xl bg-card">{children}</div>
    </div>
  );
}

interface PricingPlan {
  plan_name: string;
  plan_descp: string;
  plan_price: number;
  plan_feature: string[];
  recommended?: boolean;
  priceLabel?: string;
  ctaText?: string;
  onCta?: () => void;
}

function PricingCard({ plan_name, plan_descp, plan_price, plan_feature, recommended, priceLabel, ctaText, onCta }: PricingPlan) {
  return (
    <Card className="relative h-full rounded-3xl p-8 gap-8 border-0 ring-0 shadow-none">
      <CardHeader className="p-0">
        <div className="flex flex-col gap-3 self-stretch">
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl font-semibold tracking-tight text-[#1D1D1F]">{plan_name}</CardTitle>
            {recommended && (
              <Badge className="py-1 px-3 text-sm font-medium leading-5 h-7 flex items-center gap-1.5 [&>svg]:size-4! bg-primary/10 text-primary hover:bg-primary/20 border-0">
                <Flame size={16} /> Recomendado
              </Badge>
            )}
          </div>
          <CardDescription className="text-base font-normal max-w-2xl text-gray-500">{plan_descp}</CardDescription>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col flex-1 gap-8 p-0">
        <div className="flex items-baseline gap-1">
          <span className="text-[#1D1D1F] text-4xl sm:text-5xl font-light tracking-tight">R$ {plan_price}</span>
          {priceLabel && <span className="text-gray-400 text-base font-normal">{priceLabel}</span>}
        </div>

        <Separator className="bg-gray-200/60" />

        <ul className="flex flex-col gap-4 flex-1">
          {plan_feature.map((feature, idx) => (
            <li key={idx} className="flex items-center gap-3 text-base font-normal text-gray-500">
              <Check className="size-4 text-primary shrink-0" />
              {feature}
            </li>
          ))}
        </ul>

        <Button onClick={onCta} className="w-full h-12 rounded-full bg-[#1D1D1F] text-white hover:bg-[#1D1D1F]/80 text-sm font-semibold">
          {ctaText || "Assinar Agora"}
        </Button>
      </CardContent>
    </Card>
  );
}

export { ShineBorder, PricingCard };
export type { PricingPlan, ShineBorderProps };
