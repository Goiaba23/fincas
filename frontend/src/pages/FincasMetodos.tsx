import { formatCurrency, formatDate } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useDesafioSuico, useLimpezaFinanceira } from "@/hooks/useFincas";
import {
  Flame,
  HeartHandshake,
  Scissors,
  Globe,
  AlertTriangle,
  XCircle,
  Users,
  DollarSign,
} from "lucide-react";

function Regra10Card() {
  return (
    <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ borderColor: "rgba(249,115,22,0.2)" }}>
      <div className="border-b border-orange-500/10 px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🇳🇱</span>
          <h3 className="text-sm font-bold">Regra 10 — Pay Yourself First</h3>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">Holanda — 85% dos holandeses poupam. O segredo? Automatizar.</p>
      </div>
      <div className="space-y-4 p-5">
        <div className="rounded-xl bg-orange-500/5 border border-orange-500/10 p-4">
          <p className="text-xs text-muted-foreground leading-relaxed">
            Todo dinheiro que entra, <strong>10% vai automaticamente para poupança</strong> antes de qualquer gasto. Os holandeses chamam isso de <em>"jezelf eerst betalen"</em> — pagar-se primeiro.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            { val: "10%", label: "Percentual mínimo" },
            { val: "Auto", label: "Sem esforço" },
            { val: "🎯", label: "Meta: aposentadoria" },
          ].map((item) => (
            <div key={item.label} className="rounded-xl bg-orange-500/5 border border-orange-500/10 p-3 text-center">
              <p className="text-lg font-bold text-orange-500">{item.val}</p>
              <p className="text-[10px] text-muted-foreground">{item.label}</p>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-muted-foreground">Configure na aba <strong>Micro-Poupança</strong> com regra do tipo "Percentual da receita".</p>
      </div>
    </div>
  );
}

function DesafioSuicoCard() {
  const { user } = useAuth();
  const workspaceId = user?.workspace_id;
  const { data, isLoading } = useDesafioSuico(workspaceId);

  return (
    <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ borderColor: "rgba(239,68,68,0.2)", animationDelay: "0.1s" }}>
      <div className="border-b border-red-500/10 px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🇨🇭</span>
          <h3 className="text-sm font-bold">Desafio Suíço</h3>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">Suíça — Streak de faturas pagas 100%</p>
      </div>
      <div className="space-y-4 p-5">
        {isLoading ? (
          <div className="flex items-center justify-center py-6">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : data ? (
          <>
            <div className="flex items-center gap-4">
              <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${(data.streak ?? 0) > 0 ? "bg-red-500/10" : "bg-muted"}`}>
                <Flame className={`h-7 w-7 ${(data.streak ?? 0) > 0 ? "text-red-500" : "text-muted-foreground"}`} />
              </div>
              <div>
                <p className="stat-value">{data.streak ?? 0}</p>
                <p className="text-xs text-muted-foreground">meses sem juros</p>
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/10 p-3">
                <p className="text-[10px] text-muted-foreground">Juros evitados</p>
                <p className="text-lg font-bold text-emerald-500">{formatCurrency(data.total_interest_saved ?? 0)}</p>
              </div>
              <div className="rounded-xl bg-card p-3 border border-border/40">
                <p className="text-[10px] text-muted-foreground">Próximo marco</p>
                <p className="text-lg font-bold">{data.next_milestone ? `${data.next_milestone} meses` : "—"}</p>
              </div>
            </div>
            {data.history && data.history.length > 0 && (
              <div>
                <p className="mb-2 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Últimos 6 meses</p>
                <div className="flex gap-2">
                  {data.history.slice(-6).map((h: any) => (
                    <div key={h.month} className={`flex-1 rounded-lg p-2 text-center ${h.paid_full ? "bg-emerald-500/10" : "bg-red-500/10"}`}>
                      <p className="text-[10px] font-medium">{h.month.slice(0, 3)}</p>
                      <p className="text-xs mt-0.5">{h.paid_full ? "✅" : "❌"}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <p className="py-6 text-center text-sm text-muted-foreground">Nenhum dado de cartão de crédito importado ainda.</p>
        )}
      </div>
    </div>
  );
}

function AcordoDoisCard() {
  return (
    <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ borderColor: "rgba(139,92,246,0.2)", animationDelay: "0.2s" }}>
      <div className="border-b border-violet-500/10 px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🇳🇱</span>
          <h3 className="text-sm font-bold">Acordo a Dois — Polder Model</h3>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">Holanda — Consenso holandês no orçamento do casal</p>
      </div>
      <div className="space-y-4 p-5">
        <div className="rounded-xl bg-violet-500/5 border border-violet-500/10 p-4">
          <p className="text-xs text-muted-foreground leading-relaxed">
            O <strong>Polder Model</strong> holandês é baseado em consenso e diálogo. Aplicado às finanças do casal, oferece 3 modelos de organização:
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          {[
            { icon: Users, label: "Merged", desc: "Tudo junto" },
            { icon: DollarSign, label: "Separado", desc: "Cada um o seu" },
            { icon: HeartHandshake, label: "Híbrido", desc: "Proporcional" },
          ].map((item) => (
            <div key={item.label} className="rounded-xl bg-violet-500/5 border border-violet-500/10 p-3 text-center">
              <item.icon className="mx-auto mb-1 h-5 w-5 text-violet-500" />
              <p className="text-sm font-medium">{item.label}</p>
              <p className="text-[10px] text-muted-foreground">{item.desc}</p>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-muted-foreground">Em breve: gestão compartilhada com convite por e-mail.</p>
      </div>
    </div>
  );
}

function LimpezaCard() {
  const { user } = useAuth();
  const workspaceId = user?.workspace_id;
  const { data, isLoading } = useLimpezaFinanceira(workspaceId);

  return (
    <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ borderColor: "rgba(100,116,139,0.2)", animationDelay: "0.3s" }}>
      <div className="border-b border-slate-500/10 px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🇸🇪</span>
          <h3 className="text-sm font-bold">Limpeza Financeira — Döstädning</h3>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">Suécia — A "limpeza da morte" para assinaturas e gastos esquecidos</p>
      </div>
      <div className="space-y-4 p-5">
        {isLoading ? (
          <div className="flex items-center justify-center py-6">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : data?.subscriptions?.length > 0 ? (
          <>
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10">
                <AlertTriangle className="h-7 w-7 text-amber-500" />
              </div>
              <div>
                <p className="stat-value">{data.subscriptions.length}</p>
                <p className="text-xs text-muted-foreground">{data.unused_count ?? 0} podem estar esquecidas</p>
              </div>
            </div>
            <div className="space-y-2">
              {data.subscriptions.slice(0, 5).map((sub: any) => (
                <div key={sub.id} className="flex items-center justify-between rounded-lg border border-border/40 bg-card/30 p-3">
                  <div>
                    <p className="text-sm font-medium">{sub.description}</p>
                    <p className="text-[10px] text-muted-foreground">
                      {sub.frequency} • última cobrança: {sub.last_charge ? formatDate(sub.last_charge) : "n/a"}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold">{formatCurrency(sub.amount)}/mês</p>
                    {sub.unused && (
                      <span className="flex items-center gap-1 text-[10px] text-red-500">
                        <XCircle className="h-3 w-3" /> Não usado
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {data.total_waste_year > 0 && (
              <div className="rounded-xl bg-red-500/5 border border-red-500/10 p-4">
                <p className="text-xs"><strong className="text-red-400">Desperdício anual:</strong> {formatCurrency(data.total_waste_year)} — assinaturas não utilizadas.</p>
              </div>
            )}
          </>
        ) : (
          <div className="py-6 text-center">
            <Scissors className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Importe suas transações para detectar assinaturas esquecidas.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function EnvelopesCard() {
  return (
    <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ borderColor: "rgba(34,197,94,0.2)", animationDelay: "0.4s" }}>
      <div className="border-b border-emerald-500/10 px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🇧🇷</span>
          <h3 className="text-sm font-bold">Envelopes Pix — Caixinhas 2.0</h3>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">Brasil + YNAB — Zero-sum budgeting com caixinhas digitais</p>
      </div>
      <div className="space-y-4 p-5">
        <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/10 p-4">
          <p className="text-xs text-muted-foreground leading-relaxed">
            Inspirado no <strong>YNAB</strong> e nas <strong>Caixinhas do Nubank</strong>. Cada real tem um propósito. Zero-sum: se um envelope acaba, você realoca de outro.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            { label: "Zero-sum", desc: "Disponível = Receita - Alocado" },
            { label: "Rollover", desc: "Saldo não usado vai pro mês seguinte" },
          ].map((item) => (
            <div key={item.label} className="rounded-xl bg-emerald-500/5 border border-emerald-500/10 p-3">
              <p className="text-[10px] text-muted-foreground">{item.label}</p>
              <p className="text-xs font-medium mt-0.5">{item.desc}</p>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-muted-foreground">Em breve: envelopes personalizados com categoria e alerta de 80%.</p>
      </div>
    </div>
  );
}

export default function FincasMetodos() {
  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Todos os Métodos</h1>
        <p className="text-sm text-muted-foreground">Sabedoria financeira de 5 países — cada método com sua origem e lógica única</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Regra10Card />
        <DesafioSuicoCard />
        <AcordoDoisCard />
        <LimpezaCard />
        <div className="md:col-span-2">
          <EnvelopesCard />
        </div>
      </div>

      <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ animationDelay: "0.5s" }}>
        <div className="border-b border-border/50 px-6 py-4">
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-bold">🗺️ Mapa dos Métodos</h3>
          </div>
        </div>
        <div className="p-5">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {[
              { flag: "🇯🇵", method: "Kakeibo + Tsumitate", country: "Japão", color: "from-rose-500/10 to-pink-500/5" },
              { flag: "🇸🇪", method: "Lagom + Döstädning", country: "Suécia", color: "from-blue-500/10 to-cyan-500/5" },
              { flag: "🇳🇱", method: "Regra 10 + Polder", country: "Holanda", color: "from-orange-500/10 to-amber-500/5" },
              { flag: "🇨🇭", method: "Desafio Suíço", country: "Suíça", color: "from-red-500/10 to-rose-500/5" },
              { flag: "🇧🇷", method: "Caixinhas + Envelopes", country: "Brasil", color: "from-emerald-500/10 to-lime-500/5" },
            ].map((item) => (
              <div key={item.country} className={`rounded-xl bg-gradient-to-br ${item.color} border border-border/40 p-4 text-center`}>
                <p className="text-2xl mb-1">{item.flag}</p>
                <p className="text-xs font-medium">{item.method}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{item.country}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
