import { motion } from "motion/react";
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
  Sparkles,
  ChevronRight,
  Zap,
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

const COLORS = ["#0D47A1", "#FF5A36", "#22C55E", "#8B5CF6", "#EC4899", "#F59E0B", "#06B6D4", "#64748B"];

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className="rounded-[18px] border border-border/40 bg-card/90 px-4 py-3 shadow-xl backdrop-blur-xl"
    >
      <p className="mb-1 text-xs font-medium text-muted-foreground">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} className="text-sm font-bold" style={{ color: p.color }}>
          {p.name}: {formatCurrency(p.value)}
        </p>
      ))}
    </motion.div>
  );
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.06,
      type: "spring" as const,
      stiffness: 80,
      damping: 18,
      mass: 0.8,
    },
  }),
};


function AnimatedCard({ children, className, delay = 0, noHover = false }: { children: React.ReactNode; className?: string; delay?: number; noHover?: boolean }) {
  return (
    <motion.div
      custom={delay}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      {...(noHover ? {} : { whileHover: { y: -3, boxShadow: "0 20px 40px rgba(0,0,0,0.08), 0 8px 16px rgba(0,0,0,0.04)", transition: { type: "spring" as const, stiffness: 300, damping: 20 } } })}
      className={`${className}`}
    >
      {children}
    </motion.div>
  );
}

function SkeletonCard({ className }: { className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`rounded-[24px] skeleton-shimmer ${className || ""}`}
    />
  );
}

export default function Dashboard() {
  const { data, isLoading } = useDashboard();

  if (isLoading || !data) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen pb-12">
        <div className="mb-8">
          <div className="mb-2 h-4 w-24 skeleton-shimmer rounded-lg" />
          <div className="mb-1 h-9 w-64 skeleton-shimmer rounded-lg" />
          <div className="h-5 w-48 skeleton-shimmer rounded-lg" />
        </div>
        <div className="grid grid-cols-12 gap-3 md:gap-5">
          <SkeletonCard className="col-span-12 md:col-span-7 h-52" />
          <SkeletonCard className="col-span-12 md:col-span-5 h-52" />
          <SkeletonCard className="col-span-12 sm:col-span-6 md:col-span-4 h-44" />
          <SkeletonCard className="col-span-12 sm:col-span-6 md:col-span-4 h-52" />
          <SkeletonCard className="col-span-12 sm:col-span-6 md:col-span-4 h-52" />
          <SkeletonCard className="col-span-12 sm:col-span-6 md:col-span-4 h-52" />
          <SkeletonCard className="col-span-12 md:col-span-8 h-64" />
          <SkeletonCard className="col-span-12 sm:col-span-6 md:col-span-4 h-64" />
        </div>
      </motion.div>
    );
  }

  const { active_method, balance, monthly, category_breakdown, recent_transactions, goals, budget_progress, net_worth_history } = data;

  const isPositive = monthly.net >= 0;
  const savingsPct = monthly.savings_rate || 0;

  const methodLabels: Record<string, { name: string; tagline: string; subtitle: string }> = {
    kakeibo: { name: "Kakeibo", tagline: "🇯🇵 Consciência plena nos gastos", subtitle: "Seu mês dividido em 4 categorias — acompanhe cada uma" },
    tsumitate: { name: "Tsumitate", tagline: "🇯🇵 Pouco a pouco, longe você chega", subtitle: "Foco em micro-poupança diária — cada centavo conta" },
    regra_10: { name: "Regra 10", tagline: "🇳🇱 10% hoje, liberdade amanhã", subtitle: "10% da sua renda reservado automaticamente" },
    lagom: { name: "Lagom", tagline: "🇸🇪 Nem muito, nem pouco — na medida certa", subtitle: "Equilíbrio entre gastar e poupar sem extremos" },
    desafio_suico: { name: "Desafio Suíço", tagline: "🇨🇭 Disciplina trimestral", subtitle: "Poupe 10% a cada 3 meses — desafio ativo" },
    acordo_dois: { name: "Acordo a Dois", tagline: "🇳🇱 Finanças que fortalecem relações", subtitle: "Metas compartilhadas — vocês dois no controle" },
    limpeza_financeira: { name: "Limpeza Financeira", tagline: "🇸🇪 Menos assinatura, mais liberdade", subtitle: "Corte gastos desnecessários e otimize" },
    envelope_pix: { name: "Envelopes Pix", tagline: "🇧🇷 Controle na palma da mão", subtitle: "Envelopes digitais — cada real tem seu lugar" },
  };

  const method = active_method ? methodLabels[active_method] : null;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen pb-12">
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
        className="mb-8"
      >
        <p className="text-sm font-medium text-accent">Visão Geral</p>
        <h1 className="text-3xl font-bold tracking-tight text-[#1D1D1F]">
          Painel Financeiro
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {method ? method.subtitle : "Seu resumo financeiro deste mês"}
        </p>
      </motion.div>

      {method && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-5 flex items-center gap-3 rounded-[20px] border border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10 px-5 py-3 shadow-sm backdrop-blur-xl"
        >
          <span className="rounded-full bg-primary/15 px-3 py-1 text-xs font-bold uppercase tracking-wider text-primary">
            {method.name}
          </span>
          <p className="text-xs text-muted-foreground">{method.tagline}</p>
        </motion.div>
      )}

      <div className="grid grid-cols-12 gap-3 md:gap-5">
        {/* Hero Balance Card */}
        <AnimatedCard delay={0} noHover className="col-span-12 md:col-span-7">
          <div className="group relative overflow-hidden rounded-[24px] md:rounded-[28px] bg-gradient-to-br from-[#0D47A1] via-[#1565C0] to-[#1A237E] p-5 text-white shadow-2xl shadow-[#0D47A1]/20 md:p-7">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", stiffness: 100 }}
              className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-white/[0.04]"
            />
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: "spring", stiffness: 100 }}
              className="absolute -bottom-12 -left-12 h-36 w-36 rounded-full bg-white/[0.03]"
            />
            <div className="absolute right-6 top-6 rounded-full bg-white/10 px-3 py-1 text-[10px] font-medium text-white/70 backdrop-blur-sm">
              Saldo Disponível
            </div>
            <div className="relative">
              <div className="mb-1 flex items-center gap-2">
                <Wallet className="h-5 w-5 text-white/60" />
              </div>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 80 }}
                className="mb-1 text-2xl font-bold tracking-tight sm:text-4xl"
              >
                {formatCurrency(balance)}
              </motion.div>
              <div className="mb-5 flex items-center gap-2 text-sm">
                {isPositive ? (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.35 }}
                    className="flex items-center gap-1 text-[#4CAF50]"
                  >
                    <ArrowUpRight className="h-4 w-4" />
                    {savingsPct}% de economia
                  </motion.span>
                ) : (
                  <span className="flex items-center gap-1 text-[#FF8A80]">
                    <ArrowDownRight className="h-4 w-4" />
                    Gastando mais do que ganha
                  </span>
                )}
                <span className="text-white/40">• este mês</span>
              </div>
              <div className="h-16">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.balance_sparkline} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                    <defs>
                      <linearGradient id="heroSpark" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#64B5F6" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#64B5F6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#64B5F6"
                      strokeWidth={2.5}
                      fill="url(#heroSpark)"
                      dot={false}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </AnimatedCard>

        {/* Income / Expense / Savings Rate */}
        <AnimatedCard delay={1} className="col-span-12 md:col-span-5">
          <div className="flex h-full flex-col rounded-[24px] md:rounded-[28px] border border-white/20 bg-white/60 p-5 shadow-lg shadow-black/5 backdrop-blur-2xl transition-shadow md:p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
                Receitas vs Despesas
              </h3>
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: "spring" }}
                className="rounded-full bg-[#22C55E]/10 px-2.5 py-0.5 text-[11px] font-semibold text-[#22C55E]"
              >
                {savingsPct}% poupado
              </motion.span>
            </div>
            <div className="mt-5 flex items-center gap-5">
              <div className="flex-1 space-y-5">
                <div>
                  <div className="mb-1.5 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-muted-foreground">
                      <TrendingUp className="h-3.5 w-3.5 text-[#22C55E]" />
                      Receitas
                    </span>
                    <span className="font-bold text-[#1D1D1F]">{formatCurrency(monthly.income)}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-[#F0F0F5]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min((monthly.income / (monthly.income || 1)) * 100, 100)}%` }}
                      transition={{ delay: 0.4, duration: 1, ease: [0.16, 1, 0.3, 1] }}
                      className="h-full rounded-full bg-gradient-to-r from-[#22C55E] to-[#4ADE80]"
                    />
                  </div>
                </div>
                <div>
                  <div className="mb-1.5 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-muted-foreground">
                      <TrendingDown className="h-3.5 w-3.5 text-[#FF5A36]" />
                      Despesas
                    </span>
                    <span className="font-bold text-[#1D1D1F]">{formatCurrency(monthly.expense)}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-[#F0F0F5]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min((monthly.expense / (monthly.income || 1)) * 100, 100)}%` }}
                      transition={{ delay: 0.5, duration: 1, ease: [0.16, 1, 0.3, 1] }}
                      className="h-full rounded-full bg-gradient-to-r from-[#FF5A36] to-[#FF8A65]"
                    />
                  </div>
                </div>
              </div>
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.5, type: "spring", stiffness: 60, damping: 12 }}
                className="h-[88px] w-[88px] shrink-0"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="70%"
                    outerRadius="100%"
                    barSize={10}
                    data={[{ name: "rate", value: savingsPct, fill: "#22C55E" }]}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <RadialBar background={{ fill: "#F0F0F5" }} dataKey="value" cornerRadius={5} />
                    <text x="50%" y="48%" textAnchor="middle" dominantBaseline="middle" fill="#1D1D1F" fontSize={16} fontWeight={800}>
                      {savingsPct}%
                    </text>
                    <text x="50%" y="62%" textAnchor="middle" dominantBaseline="middle" fill="#6F6F6F" fontSize={8} fontWeight={500}>
                      poupado
                    </text>
                  </RadialBarChart>
                </ResponsiveContainer>
              </motion.div>
            </div>
          </div>
        </AnimatedCard>

        {/* Smart Savings Milestone */}
        <AnimatedCard delay={2} noHover className="col-span-12 sm:col-span-6 md:col-span-4">
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="relative overflow-hidden rounded-[24px] md:rounded-[28px] bg-gradient-to-br from-[#FF5A36] via-[#FF6B35] to-[#FF3D00] p-5 text-white shadow-2xl shadow-[#FF5A36]/20 md:p-6"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: "spring" }}
              className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-white/10"
            />
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: "spring" }}
              className="absolute -bottom-6 -left-6 h-20 w-20 rounded-full bg-white/8"
            />
            <div className="relative">
              <div className="mb-3 flex items-center gap-2">
                <motion.div
                  initial={{ rotate: -20, scale: 0 }}
                  animate={{ rotate: 0, scale: 1 }}
                  transition={{ delay: 0.5, type: "spring" }}
                  className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/20"
                >
                  <Sparkles className="h-4 w-4" />
                </motion.div>
                <span className="text-[11px] font-medium uppercase tracking-wider text-white/70">
                  Meta Inteligente
                </span>
              </div>
              <p className="mb-1 text-2xl font-bold">R$ 2.400</p>
              <p className="text-sm text-white/80">Faltam R$ 600 para atingir sua meta mensal de economia</p>
              <motion.div
                whileHover={{ x: 4 }}
                className="mt-4 flex cursor-pointer items-center gap-2 rounded-xl bg-white/15 px-3 py-2 transition-colors hover:bg-white/25"
              >
                <Zap className="h-3.5 w-3.5" />
                <span className="text-xs font-medium">Aumente em 5% sua taxa de economia</span>
                <ChevronRight className="ml-auto h-3.5 w-3.5 text-white/60" />
              </motion.div>
            </div>
          </motion.div>
        </AnimatedCard>

        {/* Category Breakdown */}
        <AnimatedCard delay={3} className="col-span-12 sm:col-span-6 md:col-span-4">
          <div className="h-full rounded-[24px] md:rounded-[28px] border border-white/20 bg-white/60 p-5 shadow-lg shadow-black/5 backdrop-blur-2xl md:p-6">
            <h3 className="mb-5 text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
              Gastos por Categoria
            </h3>
            <div className="space-y-3.5">
              {category_breakdown.length === 0 ? (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="py-6 text-center text-xs text-muted-foreground"
                >
                  Nenhum gasto registrado este mês
                </motion.p>
              ) : (
                category_breakdown.slice(0, 5).map((cat, i) => (
                  <motion.div
                    key={cat.category}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + i * 0.06, type: "spring", stiffness: 80 }}
                  >
                    <div className="mb-1.5 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.4 + i * 0.06, type: "spring" }}
                          className="h-2.5 w-2.5 rounded-full"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        />
                        <span className="font-medium text-[#1D1D1F]">{cat.category}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[#1D1D1F]">{formatCurrency(cat.amount)}</span>
                        <span className="text-muted-foreground">{cat.percentage}%</span>
                      </div>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-[#F0F0F5]">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${cat.percentage}%` }}
                        transition={{ delay: 0.35 + i * 0.06, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                        className="h-full rounded-full"
                        style={{ backgroundColor: COLORS[i % COLORS.length] }}
                      />
                    </div>
                  </motion.div>
                ))
              )}
            </div>
            {category_breakdown.length > 5 && (
              <p className="mt-4 text-center text-[11px] text-muted-foreground">
                +{category_breakdown.length - 5} outras categorias
              </p>
            )}
          </div>
        </AnimatedCard>

        {/* Recent Transactions */}
        <AnimatedCard delay={4} className="col-span-12 sm:col-span-6 md:col-span-4">
          <div className="h-full rounded-[24px] md:rounded-[28px] border border-white/20 bg-white/60 p-5 shadow-lg shadow-black/5 backdrop-blur-2xl md:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
                Transações Recentes
              </h3>
              <motion.a
                whileHover={{ x: 2 }}
                href="/transactions"
                className="text-[11px] font-medium text-accent hover:underline"
              >
                Ver todas
              </motion.a>
            </div>
            <div className="space-y-1">
              {recent_transactions.length === 0 ? (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="py-6 text-center text-xs text-muted-foreground"
                >
                  Nenhuma transação ainda
                </motion.p>
              ) : (
                recent_transactions.slice(0, 5).map((t, i) => (
                  <motion.div
                    key={t.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + i * 0.05, type: "spring", stiffness: 80 }}
                    whileHover={{ backgroundColor: "rgba(13,71,161,0.04)", x: 4 }}
                    className="flex cursor-pointer items-center justify-between rounded-xl px-3 py-2.5 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        className={`flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold ${
                          t.type === "deposit"
                            ? "bg-[#22C55E]/10 text-[#22C55E]"
                            : "bg-[#FF5A36]/10 text-[#FF5A36]"
                        }`}
                      >
                        {t.type === "deposit" ? "↑" : "↓"}
                      </motion.div>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-[#1D1D1F]">{t.description || "Sem descrição"}</p>
                        <p className="text-[11px] text-muted-foreground">
                          {t.category || "Sem categoria"}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`shrink-0 text-sm font-bold ${
                        t.type === "deposit" ? "text-[#22C55E]" : "text-[#FF5A36]"
                      }`}
                    >
                      {t.type === "deposit" ? "+" : "-"}
                      {formatCurrency(t.amount)}
                    </span>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </AnimatedCard>

        {/* Budget Progress */}
        <AnimatedCard delay={5} className="col-span-12 sm:col-span-6 md:col-span-4">
          <div className="h-full rounded-[24px] md:rounded-[28px] border border-white/20 bg-white/60 p-5 shadow-lg shadow-black/5 backdrop-blur-2xl md:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
                Orçamento do Mês
              </h3>
              {budget_progress.length > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: "spring" }}
                  className="rounded-full bg-[#FF5A36]/10 px-2.5 py-0.5 text-[11px] font-semibold text-[#FF5A36]"
                >
                  {budget_progress.filter((b) => b.progress_pct > 80).length} no limite
                </motion.span>
              )}
            </div>
            <div className="space-y-4">
              {budget_progress.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="py-6 text-center"
                >
                  <Target className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
                  <p className="text-xs text-muted-foreground">Nenhum orçamento definido</p>
                  <p className="mt-1 text-[11px] text-muted-foreground/60">
                    Crie orçamentos para acompanhar seus gastos
                  </p>
                </motion.div>
              ) : (
                budget_progress.slice(0, 4).map((b, i) => {
                  const isOver = b.progress_pct > 100;
                  const isWarning = b.progress_pct > 80 && b.progress_pct <= 100;
                  return (
                    <motion.div
                      key={b.category_id}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + i * 0.06, type: "spring", stiffness: 80 }}
                    >
                      <div className="flex gap-3">
                        <div className="w-0.5 shrink-0 rounded-full bg-gradient-to-b from-[#22C55E] to-[#0D47A1]" />
                        <div className="min-w-0 flex-1">
                          <div className="mb-2 flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2">
                              {isOver && (
                                <span className="rounded-full bg-[#FF5A36]/10 px-2 py-0.5 text-[10px] font-semibold text-[#FF5A36]">
                                  Excedido
                                </span>
                              )}
                              {isWarning && !isOver && (
                                <span className="rounded-full bg-[#FFB300]/10 px-2 py-0.5 text-[10px] font-semibold text-[#FFB300]">
                                  Atenção
                                </span>
                              )}
                              <span className="truncate font-medium text-[#1D1D1F]">{b.category_name}</span>
                            </div>
                            <div className="flex shrink-0 items-center gap-1.5">
                              <span className={isOver ? "font-bold text-[#FF5A36]" : "font-bold text-[#1D1D1F]"}>
                                {formatCurrency(b.spent)}
                              </span>
                              <span className="text-muted-foreground">/ {formatCurrency(b.budgeted)}</span>
                            </div>
                          </div>
                          <div className="h-2 overflow-hidden rounded-full bg-[#F0F0F5]">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(b.progress_pct, 100)}%` }}
                          transition={{ delay: 0.35 + i * 0.06, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                          className={`h-full rounded-full ${
                            isOver ? "bg-[#FF5A36]" : isWarning ? "bg-[#FFB300]" : "bg-[#22C55E]"
                          }`}
                        />
                      </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>
          </div>
        </AnimatedCard>

        {/* Net Worth Chart */}
        <AnimatedCard delay={6} className="col-span-12 md:col-span-8">
          <div className="rounded-[24px] md:rounded-[28px] border border-white/20 bg-white/60 p-5 shadow-lg shadow-black/5 backdrop-blur-2xl md:p-6">
            <div className="mb-1 flex items-center justify-between">
              <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
                Evolução Patrimonial
              </h3>
              <span className="text-[11px] text-muted-foreground">Últimos 6 meses</span>
            </div>
            <div className="mt-4 h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={net_worth_history} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id="incomeGrad2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#06B6D4" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="expenseGrad2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#FF5A36" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="#FF5A36" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="month"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 11, fill: "#86868B" }}
                    dy={8}
                  />
                  <YAxis hide />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="income"
                    name="Receitas"
                    stroke="#8B5CF6"
                    strokeWidth={2.5}
                    fill="url(#incomeGrad2)"
                    dot={{ r: 3, fill: "#8B5CF6", stroke: "#fff", strokeWidth: 2 }}
                    activeDot={{ r: 5, fill: "#8B5CF6", stroke: "#fff", strokeWidth: 2 }}
                  />
                  <Area
                    type="monotone"
                    dataKey="expense"
                    name="Despesas"
                    stroke="#FF5A36"
                    strokeWidth={2.5}
                    fill="url(#expenseGrad2)"
                    dot={{ r: 3, fill: "#FF5A36", stroke: "#fff", strokeWidth: 2 }}
                    activeDot={{ r: 5, fill: "#FF5A36", stroke: "#fff", strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </AnimatedCard>

        {/* Savings Goals */}
        <AnimatedCard delay={7} className="col-span-12 sm:col-span-6 md:col-span-4">
          <div className="h-full rounded-[24px] md:rounded-[28px] border border-white/20 bg-white/60 p-5 shadow-lg shadow-black/5 backdrop-blur-2xl md:p-6">
            <div className="mb-5 flex items-center justify-between">
              <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
                Metas de Economia
              </h3>
              <motion.a
                whileHover={{ x: 2 }}
                href="/fincas/micro-savings"
                className="text-[11px] font-medium text-accent hover:underline"
              >
                Gerenciar
              </motion.a>
            </div>
            {goals.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="py-6 text-center"
              >
                <PiggyBank className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
                <p className="text-xs text-muted-foreground">Nenhuma meta definida</p>
                <p className="mt-1 text-[11px] text-muted-foreground/60">
                  Defina metas para acompanhar seu progresso
                </p>
              </motion.div>
            ) : (
              <div className="space-y-5">
                {goals.slice(0, 3).map((goal, i) => {
                  const isComplete = goal.is_completed || goal.progress_pct >= 100;
                  const gradClass = `method-gradient-${(i % 8) + 1}`;
                  return (
                    <motion.div
                      key={goal.id}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + i * 0.08, type: "spring", stiffness: 80 }}
                    >
                      <div className="mb-1.5 flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <motion.div
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            className={`flex h-7 w-7 items-center justify-center rounded-xl ${gradClass} text-[11px] text-white`}
                          >
                            {isComplete ? "✓" : "₿"}
                          </motion.div>
                          <span className="text-sm font-medium text-[#1D1D1F]">{goal.name}</span>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-[#1D1D1F]">{formatCurrency(goal.current_amount)}</span>
                          <span className="text-muted-foreground"> / {formatCurrency(goal.target_amount)}</span>
                        </div>
                      </div>
                      <div className="relative h-2.5 overflow-hidden rounded-full bg-[#F0F0F5]">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(goal.progress_pct, 100)}%` }}
                          transition={{ delay: 0.35 + i * 0.08, duration: 1, ease: [0.16, 1, 0.3, 1] }}
                          className={`h-full rounded-full ${gradClass}`}
                        />
                      </div>
                      <div className="mt-1.5 flex items-center gap-2">
                        {isComplete ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-[#22C55E]/10 px-2.5 py-0.5 text-[10px] font-semibold text-[#22C55E]">
                            <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E]" />
                            Concluída
                          </span>
                        ) : (
                          <span className="rounded-full bg-[#0D47A1]/10 px-2.5 py-0.5 text-[10px] font-semibold text-[#0D47A1]">
                            {goal.progress_pct}% concluída
                          </span>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </div>
        </AnimatedCard>
      </div>
    </motion.div>
  );
}