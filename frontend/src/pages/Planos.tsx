import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useSubscriptionStatus, useStartTrial, useActivateSubscription, useCancelSubscription } from "@/hooks/useSubscription";
import { CheckCircle2, ShieldCheck, Zap, Globe, Loader2, AlertTriangle, Sparkles } from "lucide-react";

const trialFeatures = [
  "Kakeibo — método japonês de controle financeiro",
  "Tsumitate — micro-poupança automática",
  "Gastômetro Lagom — burndown orçamentário",
  "Desafio Suíço — streak de faturas 100%",
  "Regra 10 — pay yourself first",
  "Limpeza Financeira — auditoria Döstädning",
];

const premiumFeatures = [
  "Kakeibo — método japonês de controle financeiro",
  "Tsumitate — micro-poupança automática estilo Acorns",
  "Gastômetro Lagom — burndown orçamentário sueco",
  "Desafio Suíço — streak de faturas pagas 100%",
  "Regra 10 — pay yourself first holandês",
  "Limpeza Financeira — auditoria de assinaturas",
  "Acordo a Dois — orçamento compartilhado",
  "Envelopes Pix — caixinhas digitais zero-sum",
  "Assistente IA com OpenAI/Anthropic",
  "Sincronização bancária automática",
  "Múltiplos workspaces",
  "Suporte prioritário",
];

export default function Planos() {
  const { data: sub, isLoading } = useSubscriptionStatus();
  const startTrial = useStartTrial();
  const activate = useActivateSubscription();
  const cancel = useCancelSubscription();
  const [confirmCancel, setConfirmCancel] = useState(false);

  const hasAccess = sub?.has_access ?? false;
  const isTrial = sub?.status === "trial" && (sub?.trial_days_remaining ?? 0) > 0;
  const isActive = sub?.status === "active" && hasAccess;
  const trialDays = sub?.trial_days_remaining ?? 0;
  const isExpired = sub?.is_expired ?? false;

  return (
    <div className="animate-fade-in space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Planos</h1>
        <p className="text-sm text-muted-foreground">Escolha o plano ideal para suas finanças</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {hasAccess && (
            <div className={`animate-slide-down rounded-xl border p-4 ${isTrial ? "glass-card border-emerald-500/20" : "glass-card border-primary/20"}`}>
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-6 w-6 shrink-0 ${isTrial ? "text-emerald-500" : "text-primary"}`} />
                <div>
                  <p className={`font-medium ${isTrial ? "text-emerald-400" : "text-foreground"}`}>
                    {isTrial && `🎯 Trial ativo — ${trialDays} dia(s) restantes`}
                    {isActive && "✅ Plano ativo — todos os recursos liberados!"}
                  </p>
                  <p className="text-sm text-muted-foreground">{sub?.message}</p>
                </div>
              </div>
            </div>
          )}

          {isExpired && (
            <div className="glass-card animate-slide-down rounded-xl border border-red-500/20 p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-6 w-6 shrink-0 text-red-500" />
                <div>
                  <p className="font-medium text-red-400">⏰ Período expirado</p>
                  <p className="text-sm text-muted-foreground">{sub?.message}</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid gap-8 md:grid-cols-2">
            <div className="glass-card animate-slide-up overflow-hidden rounded-xl" style={{ animationDelay: "0.1s" }}>
              <div className="relative border-b border-border/50 px-6 py-4">
                <div className="absolute right-4 top-0 rounded-bl-lg rounded-br-none rounded-tl-none rounded-tr-lg bg-primary/20 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-primary">
                  Trial grátis
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <Zap className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-bold">Trial de 7 Dias</h3>
                </div>
                <p className="text-xs text-muted-foreground">Teste todos os recursos gratuitamente</p>
              </div>
              <div className="space-y-5 p-6">
                <div>
                  <p className="stat-value">Grátis</p>
                  <p className="text-xs text-muted-foreground">por 7 dias</p>
                </div>
                <ul className="space-y-2.5">
                  {trialFeatures.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-xs">
                      <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                      <span className="text-muted-foreground">{f}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => startTrial.mutate()}
                  disabled={startTrial.isPending || hasAccess}
                >
                  {startTrial.isPending ? "Ativando..." : hasAccess ? "✅ Já ativo" : "Ativar Trial Grátis"}
                </Button>
              </div>
            </div>

            <div className="gradient-border animate-slide-up overflow-hidden rounded-xl" style={{ animationDelay: "0.2s" }}>
              <div className="glass-card rounded-xl" style={{ border: "none" }}>
                <div className="relative border-b border-border/50 px-6 py-4">
                  <div className="absolute right-4 top-0 rounded-bl-lg rounded-br-none rounded-tl-none rounded-tr-lg bg-primary px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-primary-foreground">
                    Recomendado
                  </div>
                  <div className="flex items-center gap-2 pt-2">
                    <ShieldCheck className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-bold">Fincas Premium</h3>
                  </div>
                  <p className="text-xs text-muted-foreground">Acesso completo a todos os métodos globais</p>
                </div>
                <div className="space-y-5 p-6">
                  <div>
                    <p className="stat-value">
                      R$ 40
                      <span className="text-base font-normal text-muted-foreground">/mês</span>
                    </p>
                    <p className="text-xs text-muted-foreground">Menos de R$ 1,40 por dia</p>
                  </div>
                  <ul className="space-y-2.5">
                    {premiumFeatures.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-xs">
                        <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                        <span className="text-muted-foreground">{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className="w-full gap-2"
                    onClick={() => activate.mutate()}
                    disabled={activate.isPending || isActive}
                  >
                    {activate.isPending ? "Ativando..." : isActive ? "✅ Já ativo" : <>
                      <Sparkles className="h-4 w-4" />
                      Assinar Agora
                    </>}
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ animationDelay: "0.3s" }}>
            <div className="border-b border-border/50 px-6 py-4">
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-bold">Por que R$ 40/mês?</h3>
              </div>
            </div>
            <div className="space-y-3 p-6 text-sm text-muted-foreground leading-relaxed">
              <p><strong className="text-foreground">8 métodos financeiros de 5 países</strong> — cada um com décadas (ou séculos) de comprovação prática. Não é mais um app de orçamento genérico.</p>
              <p><strong className="text-foreground">Assistente IA</strong> com suporte a OpenAI e Anthropic para análises personalizadas das suas finanças.</p>
              <p><strong className="text-foreground">Sincronização bancária automática</strong> via Pluggy — suas transações sempre atualizadas sem trabalho manual.</p>
              <p>Menos de <strong className="text-emerald-500">R$ 1,40 por dia</strong> — o preço de um cafezinho para transformar sua saúde financeira.</p>
            </div>
          </div>

          {hasAccess && !confirmCancel && (
            <div className="text-center">
              <Button variant="ghost" size="sm" className="text-muted-foreground" onClick={() => setConfirmCancel(true)}>
                Cancelar assinatura
              </Button>
            </div>
          )}

          {confirmCancel && (
            <div className="glass-card animate-scale-in rounded-xl border border-red-500/30 p-6 text-center">
              <AlertTriangle className="mx-auto h-8 w-8 text-destructive" />
              <p className="mt-2 font-medium">Tem certeza que deseja cancelar?</p>
              <p className="mt-1 text-sm text-muted-foreground">Você perderá acesso aos métodos financeiros globais.</p>
              <div className="mt-4 flex justify-center gap-3">
                <Button variant="outline" onClick={() => setConfirmCancel(false)}>
                  Continuar assinatura
                </Button>
                <Button variant="destructive" onClick={() => { cancel.mutate(); setConfirmCancel(false); }} disabled={cancel.isPending}>
                  {cancel.isPending ? "Cancelando..." : "Sim, cancelar"}
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
