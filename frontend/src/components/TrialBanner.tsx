import { useNavigate } from "react-router-dom";
import { useSubscriptionStatus } from "@/hooks/useSubscription";
import { Sparkles, AlertTriangle, X } from "lucide-react";
import { useState } from "react";

export function TrialBanner() {
  const navigate = useNavigate();
  const { data: sub } = useSubscriptionStatus();
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  const isTrial = sub?.status === "trial" && (sub?.trial_days_remaining ?? 0) > 0;
  const isExpired = sub?.is_expired ?? false;
  const isNone = sub?.status === "none" || !sub;

  if (!isTrial && !isExpired && !isNone) return null;

  return (
    <div
      className={`mb-5 flex items-center justify-between rounded-xl px-5 py-3 text-sm backdrop-blur-lg ${
        isExpired || isNone
          ? "border border-red-500/20 bg-red-500/10"
          : "border border-emerald-500/20 bg-emerald-500/10"
      }`}
    >
      <div className="flex items-center gap-3">
        {isTrial ? (
          <Sparkles className="h-5 w-5 shrink-0 text-emerald-500" />
        ) : (
          <AlertTriangle className="h-5 w-5 shrink-0 text-red-500" />
        )}
        <div>
          {isTrial && (
            <p className="text-sm font-medium text-emerald-400">
              🎯 Trial grátis — <strong>{sub.trial_days_remaining} dia(s)</strong> restantes
            </p>
          )}
          {isNone && <p className="text-sm font-medium">📋 Ative seu trial grátis de 7 dias</p>}
          {isExpired && (
            <p className="text-sm font-medium text-red-400">⏰ Trial expirado — renove para continuar usando</p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => navigate("/planos")}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
            isExpired
              ? "bg-red-500 text-white hover:bg-red-600"
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          }`}
        >
          {isExpired ? "Renovar" : "Ver planos"}
        </button>
        <button onClick={() => setDismissed(true)} className="rounded-lg p-1 text-muted-foreground hover:bg-white/5">
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
