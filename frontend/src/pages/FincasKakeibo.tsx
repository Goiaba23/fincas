import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatCurrency } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useKakeiboReport, useKakeiboStreak, useCreateKakeiboEntry } from "@/hooks/useFincas";
import {
  PiggyBank,
  Flame,
  TrendingUp,
  TrendingDown,
  BookOpen,
  CheckCircle2,
  HelpCircle,
  ArrowLeft,
  Send,
} from "lucide-react";

const kakeiboCategories = [
  { id: "essential", label: "Essencial", desc: "Moradia, alimentação, transporte", color: "text-blue-500", emoji: "🏠" },
  { id: "wants", label: "Desejos", desc: "Lazer, restaurantes, hobbies", color: "text-rose-500", emoji: "🎮" },
  { id: "culture", label: "Cultura", desc: "Cursos, livros, eventos", color: "text-violet-500", emoji: "📚" },
  { id: "unexpected", label: "Imprevistos", desc: "Emergências, reparos", color: "text-amber-500", emoji: "⚠️" },
];

const questions = [
  { id: "saved", label: "Quanto você conseguiu poupar esta semana?", hint: "Valor que sobrou após todos os gastos" },
  { id: "wanted", label: "Quanto você queria ter poupado?", hint: "Sua meta ideal de poupança semanal" },
  { id: "went_well", label: "O que deu certo?", hint: "Um gasto que valeu a pena ou um hábito positivo" },
  { id: "improve", label: "O que pode melhorar?", hint: "Um gasto desnecessário ou um hábito a mudar" },
];

export default function FincasKakeibo() {
  const { user } = useAuth();
  const workspaceId = user?.workspace_id;
  const { data: report, isLoading: loadingReport } = useKakeiboReport(workspaceId);
  const { data: streakData } = useKakeiboStreak(workspaceId);
  const createEntry = useCreateKakeiboEntry();

  const [weekAnswers, setWeekAnswers] = useState<Record<string, string>>({});
  const [showCheckIn, setShowCheckIn] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const weekExpenses = report?.weekly_summary;

  const handleSubmit = async () => {
    try {
      await createEntry.mutateAsync({
        workspace_id: workspaceId,
        week_start: new Date().toISOString().split("T")[0],
        amount_saved: parseFloat(weekAnswers.saved || "0"),
        wanted_saved: parseFloat(weekAnswers.wanted || "0"),
        went_well: weekAnswers.went_well,
        improvement: weekAnswers.improve,
      });
      setSubmitted(true);
    } catch {}
  };

  if (!showCheckIn) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight">Kakeibo</h1>
              <span className="text-xl">🇯🇵</span>
            </div>
            <p className="text-sm text-muted-foreground">O método japonês de 120 anos para dominar suas finanças</p>
          </div>
          <Button onClick={() => setShowCheckIn(true)} className="gap-2 animate-slide-down">
            <BookOpen className="h-4 w-4" />
            Check-in Semanal
          </Button>
        </div>

        <div className="bento-grid">
          <div className="col-span-3 animate-slide-up" style={{ animationDelay: "0.1s" }}>
            <div className="glass-card rounded-xl p-6 text-center">
              <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500/20 to-rose-500/10">
                <Flame className={`h-7 w-7 ${streakData?.streak > 0 ? "text-orange-500" : "text-muted-foreground"}`} />
              </div>
              <p className="stat-value">{streakData?.streak ?? 0}</p>
              <p className="text-xs text-muted-foreground">semanas seguidas</p>
              {streakData?.streak > 0 && (
                <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500">
                  🔥 Streak ativo!
                </span>
              )}
            </div>
          </div>

          {kakeiboCategories.map((cat, i) => {
            const total = weekExpenses?.[cat.id] ?? 0;
            return (
              <div key={cat.id} className="col-span-3 animate-slide-up" style={{ animationDelay: `${0.15 + i * 0.08}s` }}>
                <div className="glass-card rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xl">{cat.emoji}</span>
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${cat.color}`}>{cat.label}</span>
                  </div>
                  <p className="stat-value">{formatCurrency(total)}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{cat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="glass-card rounded-xl overflow-hidden animate-slide-up" style={{ animationDelay: "0.5s" }}>
          <div className="border-b border-border/50 px-6 py-4">
            <h3 className="text-sm font-bold">📊 Resumo da Semana</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Baseado nas suas transações e check-ins</p>
          </div>
          <div className="p-5">
            {loadingReport ? (
              <div className="flex items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            ) : weekExpenses ? (
              <div className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/10 p-4">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                      <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
                      Receitas
                    </div>
                    <p className="text-xl font-bold text-emerald-500">{formatCurrency(weekExpenses.actual_income ?? 0)}</p>
                  </div>
                  <div className="rounded-xl bg-red-500/5 border border-red-500/10 p-4">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                      <TrendingDown className="h-3.5 w-3.5 text-red-500" />
                      Despesas
                    </div>
                    <p className="text-xl font-bold text-red-500">{formatCurrency(weekExpenses.actual_expenses ?? 0)}</p>
                  </div>
                </div>
                <div className="rounded-xl bg-primary/5 border border-primary/10 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Taxa de Poupança</p>
                      <p className="text-xs text-muted-foreground">vs. sua média histórica</p>
                    </div>
                    <p className={`text-xl font-bold ${(weekExpenses.savings_rate ?? 0) >= 20 ? "text-emerald-500" : "text-amber-500"}`}>
                      {weekExpenses.savings_rate?.toFixed(1) ?? 0}%
                    </p>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className={`h-full rounded-full transition-all ${(weekExpenses.savings_rate ?? 0) >= 20 ? "bg-emerald-500" : "bg-amber-500"}`}
                      style={{ width: `${Math.min((weekExpenses.savings_rate ?? 0) * 2, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center">
                <PiggyBank className="mx-auto mb-3 h-12 w-12 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Nenhum dado ainda. Faça seu primeiro check-in semanal!</p>
              </div>
            )}
          </div>
        </div>

        <div className="glass-card rounded-xl p-5 animate-slide-up" style={{ animationDelay: "0.6s" }}>
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/10">
              <HelpCircle className="h-5 w-5 text-amber-500" />
            </div>
            <div>
              <h3 className="text-sm font-bold">Os 4 Pilares do Kakeibo</h3>
              <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                O Kakeibo divide seus gastos em 4 categorias. O segredo não é cortar tudo, mas equilibrar: essencial sustenta, desejos alegram, cultura desenvolve, imprevistos protegem.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-bold">Check-in Semanal</h1>
          </div>
          <p className="text-sm text-muted-foreground">Responda as 4 perguntas do Kakeibo</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setShowCheckIn(false)}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Voltar
        </Button>
      </div>

      {submitted ? (
        <div className="glass-card rounded-xl p-10 text-center animate-scale-in">
          <CheckCircle2 className="mx-auto mb-4 h-14 w-14 text-emerald-500" />
          <h2 className="text-xl font-bold mb-2">Check-in registrado!</h2>
          <p className="mb-6 text-sm text-muted-foreground">Semana registrada com sucesso. Continue o hábito!</p>
          <Button onClick={() => { setShowCheckIn(false); setSubmitted(false); setWeekAnswers({}); }}>
            Ver relatório
          </Button>
        </div>
      ) : (
        <>
          <div className="glass-card rounded-xl overflow-hidden">
            <div className="border-b border-border/50 px-6 py-4">
              <h3 className="text-sm font-bold">💰 Pergunta 1: Poupança</h3>
              <p className="text-xs text-muted-foreground mt-0.5">{questions[0].hint}</p>
            </div>
            <div className="p-5">
              <div className="grid gap-4 sm:grid-cols-2">
                {questions.slice(0, 2).map((q) => (
                  <div key={q.id}>
                    <label className="mb-1.5 block text-xs font-medium">{q.label}</label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="R$ 0,00"
                      value={weekAnswers[q.id] ?? ""}
                      onChange={(e) => setWeekAnswers((p) => ({ ...p, [q.id]: e.target.value }))}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl overflow-hidden">
            <div className="border-b border-border/50 px-6 py-4">
              <h3 className="text-sm font-bold">💭 Pergunta 2: Reflexão</h3>
              <p className="text-xs text-muted-foreground mt-0.5">O que funcionou e o que pode melhorar</p>
            </div>
            <div className="space-y-4 p-5">
              {questions.slice(2).map((q) => (
                <div key={q.id}>
                  <label className="mb-1.5 block text-xs font-medium">{q.label}</label>
                  <textarea
                    className="glass-input flex min-h-[80px] w-full rounded-lg px-3 py-2 text-sm outline-none placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring"
                    placeholder={q.hint}
                    value={weekAnswers[q.id] ?? ""}
                    onChange={(e) => setWeekAnswers((p) => ({ ...p, [q.id]: e.target.value }))}
                  />
                </div>
              ))}
            </div>
          </div>

          <Button onClick={handleSubmit} className="w-full gap-2" size="lg" disabled={createEntry.isPending}>
            {createEntry.isPending ? (
              "Registrando..."
            ) : (
              <>
                <Send className="h-4 w-4" />
                Concluir Check-in Semanal
              </>
            )}
          </Button>
        </>
      )}
    </div>
  );
}
