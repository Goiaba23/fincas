import { useState } from "react";
import { useGoals, useCreateGoal, useDeleteGoal } from "@/hooks/useGoals";
import { formatCurrency } from "@/lib/utils";
import { Target, Plus, Trash2, CircleCheckBig } from "lucide-react";

export default function Goals() {
  const { data: goals, isLoading } = useGoals();
  const createGoal = useCreateGoal();
  const deleteGoal = useDeleteGoal();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [targetAmount, setTargetAmount] = useState("");

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !targetAmount) return;
    await createGoal.mutateAsync({ name, target_amount: parseFloat(targetAmount) });
    setName("");
    setTargetAmount("");
    setShowForm(false);
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Metas</h1>
          <p className="text-sm text-muted-foreground">Acompanhe seus objetivos financeiros</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="glass-button flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium"
        >
          <Plus className="h-4 w-4" />
          Nova Meta
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="glass-card animate-slide-up rounded-xl p-5 space-y-4">
          <input
            placeholder="Nome da meta"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          />
          <input
            type="number"
            step="0.01"
            placeholder="Valor alvo"
            value={targetAmount}
            onChange={(e) => setTargetAmount(e.target.value)}
            className="w-full rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          />
          <div className="flex gap-2">
            <button type="submit" className="glass-button rounded-lg px-4 py-2 text-sm font-medium">
              Criar
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="rounded-lg px-4 py-2 text-sm text-muted-foreground hover:text-foreground"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading
          ? Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="glass-card animate-pulse rounded-xl p-5 h-40" />
            ))
          : goals?.map((goal) => (
              <div key={goal.id} className="glass-card group rounded-xl p-5 transition-all hover:shadow-lg">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/10">
                      <Target className="h-4 w-4 text-amber-500" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{goal.name}</p>
                      {goal.target_date && (
                        <p className="text-xs text-muted-foreground">Até {goal.target_date}</p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => deleteGoal.mutate(goal.id)}
                    className="hidden h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-red-500/10 hover:text-red-500 group-hover:flex"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                <div className="mt-4">
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-muted-foreground">{formatCurrency(goal.current)}</span>
                    <span className="font-medium">{formatCurrency(goal.target)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted/50 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all"
                      style={{ width: `${Math.min(goal.progress, 100)}%` }}
                    />
                  </div>
                  <p className="mt-1.5 text-xs text-muted-foreground">
                    {goal.progress >= 100 ? (
                      <span className="flex items-center gap-1 text-emerald-500">
                        <CircleCheckBig className="h-3 w-3" /> Completa
                      </span>
                    ) : (
                      `${goal.progress}% concluído`
                    )}
                  </p>
                </div>

                {goal.description && (
                  <p className="mt-3 text-xs text-muted-foreground">{goal.description}</p>
                )}
              </div>
            ))}
      </div>

      {goals?.length === 0 && !isLoading && (
        <div className="glass-card rounded-xl p-12 text-center">
          <Target className="mx-auto h-8 w-8 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">Nenhuma meta criada ainda</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 text-sm font-medium text-primary hover:underline"
          >
            Criar sua primeira meta
          </button>
        </div>
      )}
    </div>
  );
}
