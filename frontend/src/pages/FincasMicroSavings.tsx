import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatCurrency } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useMicroSavingsRules, useCreateMicroSavingsRule, useDeleteMicroSavingsRule, useExecuteRoundup } from "@/hooks/useFincas";
import {
  TrendingDown,
  Plus,
  Trash2,
  Zap,
  ArrowDownToLine,
  Coins,
  Timer,
  Sparkles,
} from "lucide-react";

export default function FincasMicroSavings() {
  const { user } = useAuth();
  const workspaceId = user?.workspace_id;
  const { data: rules, isLoading } = useMicroSavingsRules(workspaceId);
  const createRule = useCreateMicroSavingsRule();
  const deleteRule = useDeleteMicroSavingsRule();
  const executeRoundup = useExecuteRoundup();

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    rule_type: "roundup",
    config_value: 5,
    frequency: "daily",
    target_amount: 0,
  });

  const handleCreate = async () => {
    try {
      await createRule.mutateAsync({ workspace_id: workspaceId, ...form });
      setShowForm(false);
      setForm({ name: "", rule_type: "roundup", config_value: 5, frequency: "daily", target_amount: 0 });
    } catch {}
  };

  const stats = [
    { icon: Coins, label: "Regras Ativas", value: String(rules?.length ?? 0), color: "emerald" },
    { icon: ArrowDownToLine, label: "Acumulado (mês)", value: formatCurrency(rules?.reduce((s: number, r: any) => s + (r.total_saved_this_month ?? 0), 0) ?? 0), color: "sky" },
    { icon: Timer, label: "Próximo Round-up", value: "Automático", color: "amber" },
  ];

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Micro-Poupança</h1>
            <span className="text-xl">🇯🇵</span>
          </div>
          <p className="text-sm text-muted-foreground">Poupe sem perceber — round-ups automáticos estilo Tsumitate + Acorns</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)} className="gap-2">
          <Plus className="h-4 w-4" />
          {showForm ? "Fechar" : "Nova Regra"}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((s, i) => (
          <div key={s.label} className="glass-card animate-slide-up rounded-xl p-5 text-center" style={{ animationDelay: `${i * 0.1}s` }}>
            <s.icon className={`mx-auto mb-2 h-7 w-7 text-${s.color}-500`} />
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className={`stat-value mt-0.5 text-${s.color}-500`}>{s.value}</p>
          </div>
        ))}
      </div>

      {showForm && (
        <div className="glass-card animate-slide-down rounded-xl overflow-hidden">
          <div className="border-b border-border/50 px-6 py-4">
            <h3 className="text-sm font-bold">Nova Regra de Poupança</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Crie uma regra automática para poupar sem esforço</p>
          </div>
          <div className="space-y-4 p-5">
            <div>
              <label className="mb-1.5 block text-xs font-medium">Nome da regra</label>
              <Input
                placeholder="Ex: Arredondar mercado"
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-xs font-medium">Tipo</label>
                <select
                  className="glass-input flex h-10 w-full rounded-lg px-3 py-2 text-sm outline-none"
                  value={form.rule_type}
                  onChange={(e) => setForm((p) => ({ ...p, rule_type: e.target.value }))}
                >
                  <option value="roundup">Round-up (arredondar compras)</option>
                  <option value="fixed">Valor fixo por período</option>
                  <option value="percent_income">Percentual da receita</option>
                </select>
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Frequência</label>
                <select
                  className="glass-input flex h-10 w-full rounded-lg px-3 py-2 text-sm outline-none"
                  value={form.frequency}
                  onChange={(e) => setForm((p) => ({ ...p, frequency: e.target.value }))}
                >
                  <option value="daily">Diária</option>
                  <option value="weekly">Semanal</option>
                  <option value="monthly">Mensal</option>
                </select>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-xs font-medium">
                  {form.rule_type === "percent_income" ? "Percentual (%)" : "Valor (R$)"}
                </label>
                <Input
                  type="number"
                  step="0.01"
                  value={form.config_value}
                  onChange={(e) => setForm((p) => ({ ...p, config_value: parseFloat(e.target.value) }))}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium">Meta total (R$) — opcional</label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0 = sem limite"
                  value={form.target_amount || ""}
                  onChange={(e) => setForm((p) => ({ ...p, target_amount: parseFloat(e.target.value) || 0 }))}
                />
              </div>
            </div>
            <Button onClick={handleCreate} className="w-full gap-2" disabled={createRule.isPending || !form.name}>
              <Sparkles className="h-4 w-4" />
              {createRule.isPending ? "Criando..." : "Criar Regra Automática"}
            </Button>
          </div>
        </div>
      )}

      <div className="glass-card animate-slide-up rounded-xl overflow-hidden" style={{ animationDelay: "0.3s" }}>
        <div className="border-b border-border/50 px-6 py-4">
          <h3 className="text-sm font-bold">⚡ Suas Regras</h3>
          <p className="text-xs text-muted-foreground mt-0.5">Gerencie suas regras de micro-poupança</p>
        </div>
        <div className="p-5">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : rules?.length === 0 ? (
            <div className="py-8 text-center">
              <TrendingDown className="mx-auto mb-3 h-10 w-10 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Nenhuma regra ainda. Crie sua primeira regra automática!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {rules?.map((rule: any) => (
                <div key={rule.id} className="flex items-center justify-between rounded-lg border border-border/40 bg-card/30 p-3 transition-all hover:bg-accent/20">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10">
                      <Zap className="h-4 w-4 text-emerald-500" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{rule.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {rule.rule_type === "roundup" && `Arredondar para cima em R$ ${rule.config_value}`}
                        {rule.rule_type === "fixed" && `R$ ${rule.config_value} por ${rule.frequency}`}
                        {rule.rule_type === "percent_income" && `${rule.config_value}% da receita`}
                        {" — "}
                        <span className="font-medium text-emerald-500">
                          {formatCurrency(rule.total_saved_this_month ?? 0)} no mês
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => executeRoundup.mutate({ rule_id: rule.id, workspace_id: workspaceId })} disabled={executeRoundup.isPending}>
                      Executar
                    </Button>
                    <Button variant="ghost" size="icon" className="text-destructive" onClick={() => deleteRule.mutate(rule.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
