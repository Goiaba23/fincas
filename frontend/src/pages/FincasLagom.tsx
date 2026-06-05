import { useState } from "react";
import { formatCurrency } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useLagomBurndown } from "@/hooks/useFincas";
import { TrendingDown, Info } from "lucide-react";

export default function FincasLagom() {
  const { user } = useAuth();
  const workspaceId = user?.workspace_id;
  const now = new Date();
  const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const [month, setMonth] = useState(currentMonth);
  const { data: burndown } = useLagomBurndown(workspaceId, month);

  const budget = burndown?.budget ?? 0;
  const spent = burndown?.spent_so_far ?? 0;
  const pctUsed = budget > 0 ? (spent / budget) * 100 : 0;
  const daysElapsed = burndown?.days_elapsed ?? 1;
  const totalDays = burndown?.total_days ?? 30;
  const idealBurn = budget > 0 ? (budget / totalDays) * daysElapsed : 0;
  const remaining = budget - spent;
  const dailyRemaining = remaining > 0 && (totalDays - daysElapsed) > 0 ? remaining / (totalDays - daysElapsed) : 0;

  const zone = pctUsed < 85 ? "green" : pctUsed < 100 ? "yellow" : "red";

  const zoneConfig = {
    green: { border: "border-emerald-500/20", glow: "shadow-emerald-500/5", bar: "bg-emerald-500", badge: "bg-emerald-500/10 text-emerald-500", label: "🟢 Verde — Ritmo tranquilo", desc: "Você está gastando dentro do ideal. Continue assim!" },
    yellow: { border: "border-amber-500/20", glow: "shadow-amber-500/5", bar: "bg-amber-500", badge: "bg-amber-500/10 text-amber-500", label: "🟡 Amarelo — Atenção", desc: "Ritmo acelerado. Reveja seus gastos discricionários." },
    red: { border: "border-red-500/20", glow: "shadow-red-500/5", bar: "bg-red-500", badge: "bg-red-500/10 text-red-500", label: "🔴 Vermelho — Estourou!", desc: "Orçamento excedido. Hora de reavaliar." },
  };
  const zc = zoneConfig[zone];

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight">Gastômetro Lagom</h1>
          <span className="text-xl">🇸🇪</span>
        </div>
        <p className="text-sm text-muted-foreground">O equilíbrio sueco — nem demais, nem de menos</p>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-xs font-medium text-muted-foreground">Mês:</label>
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="glass-input h-9 rounded-lg px-3 py-1 text-sm outline-none"
        />
      </div>

      <div className={`glass-card animate-slide-up rounded-xl p-6 border ${zc.border} ${zc.glow}`} style={{ animationDelay: "0.1s" }}>
        <div className="mb-4 flex items-start justify-between">
          <div>
            <p className="text-sm font-bold">{zc.label}</p>
            <p className="mt-1 text-xs text-muted-foreground">{pctUsed.toFixed(0)}% utilizado • Dia {daysElapsed}/{totalDays}</p>
          </div>
          <span className={`rounded-full px-3 py-1 text-[10px] font-bold ${zc.badge}`}>
            Zona {zone === "green" ? "Verde" : zone === "yellow" ? "Amarela" : "Vermelha"}
          </span>
        </div>

        <div className="h-3 overflow-hidden rounded-full bg-muted">
          <div className={`h-full rounded-full transition-all duration-500 ${zc.bar}`} style={{ width: `${Math.min(pctUsed, 100)}%` }} />
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Orçamento" value={formatCurrency(budget)} />
          <Metric label="Gasto até agora" value={formatCurrency(spent)} color={spent > 0 ? "text-red-500" : ""} />
          <Metric label="Restante" value={formatCurrency(remaining)} color={remaining >= 0 ? "text-emerald-500" : "text-red-500"} />
          <Metric label="Ritmo diário ideal" value={`${formatCurrency(dailyRemaining)}/dia`} />
        </div>

        <p className="mt-4 text-xs" style={{ color: zone === "green" ? "oklch(0.723 0.219 149.579)" : zone === "yellow" ? "oklch(0.795 0.184 86.047)" : "oklch(0.637 0.237 25.331)" }}>
          {zc.desc}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ animationDelay: "0.2s" }}>
          <div className="border-b border-border/50 px-6 py-4">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-blue-500" />
              <h3 className="text-sm font-bold">Burndown Ideal vs Real</h3>
            </div>
          </div>
          <div className="space-y-4 p-5">
            <div>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Ideal (linear)</span>
                <span className="font-medium">{formatCurrency(idealBurn)}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${budget > 0 ? Math.min((idealBurn / budget) * 100, 100) : 0}%` }} />
              </div>
            </div>
            <div>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Real</span>
                <span className="font-medium">{formatCurrency(spent)}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div className={`h-full rounded-full ${spent <= idealBurn ? "bg-emerald-500" : "bg-red-500"}`} style={{ width: `${budget > 0 ? Math.min((spent / budget) * 100, 100) : 0}%` }} />
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              {spent <= idealBurn
                ? "✅ Dentro do esperado — continue assim!"
                : `⚠️ ${formatCurrency(spent - idealBurn)} acima do ideal`}
            </p>
          </div>
        </div>

        <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ animationDelay: "0.25s" }}>
          <div className="border-b border-border/50 px-6 py-4">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4 text-amber-500" />
              <h3 className="text-sm font-bold">🇸🇪 O que é Lagom?</h3>
            </div>
          </div>
          <div className="space-y-3 p-5 text-xs text-muted-foreground leading-relaxed">
            <p><strong className="text-foreground">Lagom</strong> (lah-gom) é o conceito sueco de "nem demais, nem de menos".</p>
            <p>O Gastômetro compara seu gasto real com o ideal linear do mês. Se o orçamento é R$ 5.000 em 30 dias, no dia 15 o ideal seria R$ 2.500.</p>
            <div className="space-y-1 text-xs">
              <p className="text-emerald-500"><strong>🟢 Verde</strong> (&lt;85%) — Ritmo tranquilo</p>
              <p className="text-amber-500"><strong>🟡 Amarelo</strong> (85-100%) — Atenção</p>
              <p className="text-red-500"><strong>🔴 Vermelho</strong> (&gt;100%) — Estourou</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`stat-value mt-0.5 ${color || ""}`}>{value}</p>
    </div>
  );
}
