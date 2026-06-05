import { useDashboard } from "@/hooks/useDashboard";
import { formatCurrency } from "@/lib/utils";
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  AlertCircle,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
} from "recharts";

const categoryColors: Record<string, string> = {
  Moradia: "#0D47A1",
  Alimentação: "#FF5A36",
  Transporte: "#22C55E",
  Lazer: "#8B5CF6",
  Saúde: "#EC4899",
  Educação: "#F59E0B",
  Assinaturas: "#06B6D4",
  Compras: "#64748B",
};

const COLORS = ["#0D47A1", "#FF5A36", "#22C55E", "#8B5CF6", "#EC4899", "#F59E0B", "#06B6D4", "#64748B"];

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-border/50 bg-card/90 px-4 py-3 shadow-xl backdrop-blur-xl">
      <p className="mb-1 text-xs font-medium text-muted-foreground">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} className="text-sm font-bold" style={{ color: p.color }}>
          {p.name}: {formatCurrency(p.value)}
        </p>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading } = useDashboard();

  if (isLoading || !data) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="mb-8 h-8 w-64 skeleton-shimmer rounded-lg" />
        <div className="bento-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-48 rounded-2xl skeleton-shimmer"
              style={{ gridColumn: i < 2 ? "span 6" : i < 4 ? "span 4" : "span 6" }}
            />
          ))}
        </div>
      </div>
    );
  }

  const { balance, monthly, category_breakdown, recent_transactions, goals, budget_progress, net_worth_history } = data;

  const MonthlyMiniChart = () => {
    const sparkData = data.balance_sparkline;
    return (
      <div className="h-20 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={sparkData} margin={{ top: 5, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0D47A1" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#0D47A1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke="#0D47A1"
              strokeWidth={2}
              fill="url(#sparkGrad)"
              dot={false}
              activeDot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const isPositive = monthly.net >= 0;

  return (
    <div className="animate-fade-in space-y-6">
      <div className="mb-2">
        <h1 className="text-2xl font-bold tracking-tight">
          Painel Financeiro
        </h1>
        <p className="text-sm text-muted-foreground">Visão geral das suas finanças este mês</p>
      </div>

      <div className="bento-grid">
        {/* Hero Balance Card */}
        <div className="animate-slide-up col-span-7" style={{ animationDelay: "0s" }}>
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0D47A1] to-[#1565C0] p-6 text-white">
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/5" />
            <div className="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-white/5" />
            <div className="relative">
              <div className="mb-1 flex items-center gap-2 text-sm text-white/70">
                <Wallet className="h-4 w-4" />
                Saldo Disponível
              </div>
              <div className="stat-value mb-1 text-white">{formatCurrency(balance)}</div>
              <div className="mb-3 flex items-center gap-1.5 text-sm">
                {isPositive ? (
                  <span className="flex items-center gap-0.5 text-emerald-300">
                    <ArrowUpRight className="h-3.5 w-3.5" />
                    {monthly.savings_rate}% de economia
                  </span>
                ) : (
                  <span className="flex items-center gap-0.5 text-red-300">
                    <ArrowDownRight className="h-3.5 w-3.5" />
                    Gastando mais do que ganha
                  </span>
                )}
                <span className="text-white/50">• este mês</span>
              </div>
              <MonthlyMiniChart />
            </div>
          </div>
        </div>

        {/* Income / Expense / Savings Rate */}
        <div className="animate-slide-up col-span-5" style={{ animationDelay: "0.1s" }}>
          <div className="bento-card flex h-full flex-col justify-between">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Receitas vs Despesas
              </h3>
              <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-500">
                {monthly.savings_rate}% poupado
              </span>
            </div>
            <div className="mt-4 flex items-center gap-6">
              <div className="flex-1 space-y-4">
                <div>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <TrendingUp className="h-3 w-3 text-emerald-500" />
                      Receitas
                    </span>
                    <span className="font-bold text-emerald-500">{formatCurrency(monthly.income)}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-emerald-500 transition-all duration-1000"
                      style={{ width: `${Math.min((monthly.income / (monthly.income || 1)) * 100, 100)}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <TrendingDown className="h-3 w-3 text-rose-500" />
                      Despesas
                    </span>
                    <span className="font-bold text-rose-500">{formatCurrency(monthly.expense)}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-rose-500 transition-all duration-1000"
                      style={{ width: `${Math.min((monthly.expense / (monthly.income || 1)) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
              <div className="h-20 w-20 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="70%"
                    outerRadius="100%"
                    barSize={8}
                    data={[{ name: "rate", value: monthly.savings_rate, fill: "#22C55E" }]}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <RadialBar background dataKey="value" cornerRadius={4} />
                    <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fill="var(--text-primary, #1A1A1A)" fontSize={12} fontWeight={700}>
                      {monthly.savings_rate}%
                    </text>
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="animate-slide-up col-span-4" style={{ animationDelay: "0.15s" }}>
          <div className="bento-card h-full">
            <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Gastos por Categoria
            </h3>
            <div className="space-y-3">
              {category_breakdown.length === 0 ? (
                <p className="py-6 text-center text-xs text-muted-foreground">Nenhum gasto registrado este mês</p>
              ) : (
                category_breakdown.slice(0, 6).map((cat, i) => (
                  <div key={cat.category}>
                    <div className="mb-1 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span
                          className="h-2 w-2 rounded-full"
                          style={{ backgroundColor: categoryColors[cat.group] || COLORS[i % COLORS.length] }}
                        />
                        <span className="font-medium">{cat.category}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold">{formatCurrency(cat.amount)}</span>
                        <span className="text-muted-foreground">{cat.percentage}%</span>
                      </div>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${cat.percentage}%`,
                          backgroundColor: categoryColors[cat.group] || COLORS[i % COLORS.length],
                        }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
            {category_breakdown.length > 6 && (
              <p className="mt-3 text-center text-[10px] text-muted-foreground">
                +{category_breakdown.length - 6} outras categorias
              </p>
            )}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="animate-slide-up col-span-4" style={{ animationDelay: "0.2s" }}>
          <div className="bento-card h-full">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Transações Recentes
              </h3>
              <a href="/transactions" className="text-[10px] font-medium text-[#0D47A1] hover:underline">
                Ver todas
              </a>
            </div>
            <div className="space-y-0.5">
              {recent_transactions.length === 0 ? (
                <p className="py-6 text-center text-xs text-muted-foreground">Nenhuma transação ainda</p>
              ) : (
                recent_transactions.slice(0, 6).map((t) => (
                  <div
                    key={t.id}
                    className="flex items-center justify-between rounded-lg px-2 py-2.5 transition-colors hover:bg-accent/30"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold ${
                          t.type === "deposit"
                            ? "bg-emerald-500/10 text-emerald-500"
                            : "bg-rose-500/10 text-rose-500"
                        }`}
                      >
                        {t.type === "deposit" ? "↑" : "↓"}
                      </div>
                      <div className="min-w-0">
                        <p className="truncate text-xs font-medium">{t.description || "Sem descrição"}</p>
                        <p className="text-[10px] text-muted-foreground">
                          {t.category || "Sem categoria"}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`shrink-0 text-xs font-bold ${
                        t.type === "deposit" ? "text-emerald-500" : "text-rose-500"
                      }`}
                    >
                      {t.type === "deposit" ? "+" : "-"}
                      {formatCurrency(t.amount)}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Budget Progress */}
        <div className="animate-slide-up col-span-4" style={{ animationDelay: "0.25s" }}>
          <div className="bento-card h-full">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Orçamento do Mês
              </h3>
              {budget_progress.length > 0 && (
                <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-500">
                  {budget_progress.filter((b) => b.progress_pct > 80).length} perto do limite
                </span>
              )}
            </div>
            <div className="space-y-3">
              {budget_progress.length === 0 ? (
                <div className="py-6 text-center">
                  <Target className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
                  <p className="text-xs text-muted-foreground">Nenhum orçamento definido</p>
                  <p className="mt-1 text-[10px] text-muted-foreground/60">
                    Crie orçamentos para acompanhar seus gastos
                  </p>
                </div>
              ) : (
                budget_progress.slice(0, 5).map((b) => {
                  const isOver = b.progress_pct > 100;
                  const isWarning = b.progress_pct > 80 && b.progress_pct <= 100;
                  return (
                    <div key={b.category_id}>
                      <div className="mb-1 flex items-center justify-between text-xs">
                        <span className="font-medium">{b.category_name}</span>
                        <div className="flex items-center gap-1.5">
                          {isOver && <AlertCircle className="h-3 w-3 text-red-500" />}
                          {isWarning && !isOver && (
                            <span className="h-2 w-2 rounded-full bg-amber-500" />
                          )}
                          <span className={isOver ? "font-bold text-red-500" : "font-bold"}>
                            {formatCurrency(b.spent)}
                          </span>
                          <span className="text-muted-foreground">
                            / {formatCurrency(b.budgeted)}
                          </span>
                        </div>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                        <div
                          className={`h-full rounded-full transition-all duration-1000 ${
                            isOver ? "bg-red-500" : isWarning ? "bg-amber-500" : "bg-emerald-500"
                          }`}
                          style={{ width: `${Math.min(b.progress_pct, 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Net Worth Chart */}
        <div className="animate-slide-up col-span-7" style={{ animationDelay: "0.3s" }}>
          <div className="bento-card h-full">
            <h3 className="mb-1 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Evolução Patrimonial
            </h3>
            <p className="mb-4 text-[10px] text-muted-foreground">Últimos 6 meses</p>
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={net_worth_history} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#22C55E" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="#22C55E" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#EF4444" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="#EF4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="month"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: "var(--text-secondary, #86868B)" }}
                    dy={8}
                  />
                  <YAxis hide />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="income"
                    name="Receitas"
                    stroke="#22C55E"
                    strokeWidth={2}
                    fill="url(#incomeGrad)"
                  />
                  <Area
                    type="monotone"
                    dataKey="expense"
                    name="Despesas"
                    stroke="#EF4444"
                    strokeWidth={2}
                    fill="url(#expenseGrad)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Savings Goals */}
        <div className="animate-slide-up col-span-5" style={{ animationDelay: "0.35s" }}>
          <div className="bento-card h-full">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Metas de Economia
              </h3>
              <a href="/fincas/micro-savings" className="text-[10px] font-medium text-[#0D47A1] hover:underline">
                Gerenciar
              </a>
            </div>
            {goals.length === 0 ? (
              <div className="py-6 text-center">
                <PiggyBank className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
                <p className="text-xs text-muted-foreground">Nenhuma meta definida</p>
                <p className="mt-1 text-[10px] text-muted-foreground/60">
                  Defina metas para acompanhar seu progresso
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {goals.slice(0, 3).map((goal, i) => {
                  const isComplete = goal.is_completed || goal.progress_pct >= 100;
                  const gradClass = `method-gradient-${(i % 8) + 1}`;
                  return (
                    <div key={goal.id}>
                      <div className="mb-1.5 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <div className={`flex h-6 w-6 items-center justify-center rounded-md ${gradClass} text-[10px] text-white`}>
                            {isComplete ? "✓" : "₿"}
                          </div>
                          <span className="font-medium">{goal.name}</span>
                        </div>
                        <div className="text-right">
                          <span className="font-bold">{formatCurrency(goal.current_amount)}</span>
                          <span className="text-muted-foreground"> / {formatCurrency(goal.target_amount)}</span>
                        </div>
                      </div>
                      <div className="relative h-2 overflow-hidden rounded-full bg-muted">
                        <div
                          className={`h-full rounded-full transition-all duration-1000 ${gradClass}`}
                          style={{ width: `${Math.min(goal.progress_pct, 100)}%` }}
                        />
                      </div>
                      <p className="mt-0.5 text-[10px] text-muted-foreground">
                        {isComplete ? "Concluída! 🎉" : `${goal.progress_pct}% concluída`}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
