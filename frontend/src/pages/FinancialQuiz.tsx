import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "motion/react";
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
  Target,
  BookOpen,
  TrendingDown,
  Percent,
  Flame,
  HeartHandshake,
  Scissors,
  Globe,
  ChevronRight,
  Loader2,
  Bot,
  Stars,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuizQuestions, useQuizRecommendation, useSaveRecommendation, type MethodScore } from "@/hooks/useFinancialQuiz";

const methodIcons: Record<string, React.ElementType> = {
  "book-open": BookOpen,
  "trending-down": TrendingDown,
  percent: Percent,
  target: Target,
  flame: Flame,
  handshake: HeartHandshake,
  scissors: Scissors,
  envelope: Globe,
};

const methodGradients: Record<string, string> = {
  kakeibo: "from-rose-500 to-pink-600",
  tsumitate: "from-emerald-500 to-teal-600",
  regra_10: "from-orange-500 to-amber-600",
  lagom: "from-blue-500 to-cyan-600",
  desafio_suico: "from-red-500 to-rose-600",
  acordo_dois: "from-violet-500 to-purple-600",
  limpeza_financeira: "from-slate-500 to-gray-600",
  envelope_pix: "from-emerald-500 to-lime-600",
};

const methodFlags: Record<string, string> = {
  kakeibo: "🇯🇵",
  tsumitate: "🇯🇵",
  regra_10: "🇳🇱",
  lagom: "🇸🇪",
  desafio_suico: "🇨🇭",
  acordo_dois: "🇳🇱",
  limpeza_financeira: "🇸🇪",
  envelope_pix: "🇧🇷",
};

function LikertOptions({
  options,
  value,
  onChange,
}: {
  options: { value: number; label: string }[];
  value?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="space-y-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`w-full rounded-xl border p-4 text-left text-sm transition-all ${
            value === opt.value
              ? "border-primary bg-primary/10 shadow-md"
              : "border-border/40 hover:border-primary/30 hover:bg-accent/30"
          }`}
        >
          <div className="flex items-center gap-3">
            <div
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                value === opt.value ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
              }`}
            >
              {opt.value}
            </div>
            <span>{opt.label}</span>
            {value === opt.value && <Check className="ml-auto h-4 w-4 text-primary" />}
          </div>
        </button>
      ))}
    </div>
  );
}

function MultipleChoiceOptions({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string }[];
  value?: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`rounded-xl border p-4 text-left text-sm transition-all ${
            value === opt.value
              ? "border-primary bg-primary/10 shadow-md"
              : "border-border/40 hover:border-primary/30 hover:bg-accent/30"
          }`}
        >
          <div className="flex items-center gap-3">
            <div
              className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs ${
                value === opt.value ? "border-primary bg-primary text-primary-foreground" : "border-muted-foreground/30"
              }`}
            >
              {value === opt.value && <Check className="h-3 w-3" />}
            </div>
            <span>{opt.label}</span>
          </div>
        </button>
      ))}
    </div>
  );
}

function ResultCard({
  method,
  rank,
  isTop,
}: {
  method: MethodScore;
  rank: number;
  isTop: boolean;
}) {
  const navigate = useNavigate();
  const saveRecommendation = useSaveRecommendation();
  const Icon = methodIcons[method.icon] || Globe;
  const routeMap: Record<string, string> = {
    kakeibo: "/fincas/kakeibo",
    tsumitate: "/fincas/micro-savings",
    lagom: "/fincas/lagom",
    regra_10: "/fincas/metodos",
    desafio_suico: "/fincas/metodos",
    acordo_dois: "/fincas/metodos",
    limpeza_financeira: "/fincas/metodos",
    envelope_pix: "/fincas/metodos",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.15 }}
      className={`rounded-xl border p-5 ${
        isTop
          ? "border-primary/40 bg-gradient-to-br from-primary/5 to-primary/10 shadow-xl"
          : "border-border/40 bg-card/50"
      }`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${
            methodGradients[method.key] || "from-primary to-primary/60"
          } text-white shadow-lg`}
        >
          <Icon className="h-6 w-6" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-lg">{methodFlags[method.key] || ""}</span>
            <h3 className="text-base font-bold">{method.name}</h3>
            {isTop && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/20 px-2 py-0.5 text-[10px] font-bold text-primary">
                <Sparkles className="h-3 w-3" /> MELHOR
              </span>
            )}
          </div>
          <p className="mt-0.5 text-xs text-muted-foreground">{method.origin}</p>
          <p className="mt-2 text-xs leading-relaxed">{method.tagline}</p>

          <div className="mt-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Compatibilidade</span>
              <span className="font-bold">{method.percentage}%</span>
            </div>
            <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-muted">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${method.percentage}%` }}
                transition={{ duration: 1, delay: rank * 0.15 + 0.3, ease: "easeOut" }}
                className={`h-full rounded-full bg-gradient-to-r ${
                  methodGradients[method.key] || "from-primary to-primary/60"
                }`}
              />
            </div>
          </div>

          {isTop && (
            <>
              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{method.description}</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {method.benefits.map((b) => (
                  <span
                    key={b}
                    className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-medium text-primary"
                  >
                    <Check className="h-2.5 w-2.5" /> {b}
                  </span>
                ))}
              </div>
              <p className="mt-3 text-xs italic text-muted-foreground">
                <strong>Ideal para:</strong> {method.best_for}
              </p>
              <Button
                size="sm"
                className="mt-4 w-full gap-2"
                onClick={() => {
                  saveRecommendation.mutate({ method_key: method.key, method_name: method.name });
                  const route = routeMap[method.key];
                  if (route) navigate(route);
                }}
              >
                Começar com {method.name} <ChevronRight className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export default function FinancialQuiz() {
  const navigate = useNavigate();
  const { data: questions, isLoading: questionsLoading } = useQuizQuestions();
  const recommend = useQuizRecommendation();

  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | number>>({});
  const [customDream, setCustomDream] = useState("");

  const totalSteps = questions ? questions.length + 1 : 1;
  const isLastQuestion = questions && step === questions.length;
  const currentQuestion = questions && questions[step];

  const progress = ((step + 1) / totalSteps) * 100;

  const handleAnswer = useCallback(
    (value: string | number) => {
      if (!currentQuestion) return;
      const newAnswers = { ...answers, [currentQuestion.id]: value };
      setAnswers(newAnswers);

      if (step < (questions?.length || 1) - 1) {
        setStep((s) => s + 1);
      } else {
        recommenderMethod(newAnswers);
      }
    },
    [answers, currentQuestion, step, questions]
  );

  const handleDreamSubmit = useCallback(() => {
    const newAnswers = { ...answers, savings_goal_dream: customDream };
    setAnswers(newAnswers);
    recommenderMethod(newAnswers);
  }, [answers, customDream]);

  const recommenderMethod = useCallback(
    (finalAnswers: Record<string, string | number>) => {
      recommend.mutate(finalAnswers);
      setStep(questions ? questions.length : 0);
    },
    [recommend, questions]
  );

  if (questionsLoading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Carregando perguntas...</p>
        </div>
      </div>
    );
  }

  const result = recommend.data;

  return (
    <div className="animate-fade-in mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Diagnóstico Financeiro</h1>
          <p className="text-sm text-muted-foreground">
            {result
              ? "Seu método ideal foi encontrado!"
              : "Responda algumas perguntas para descobrir o método ideal para você"}
          </p>
        </div>
        {!result && (
          <div className="flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-xs font-medium text-primary">
            <Sparkles className="h-3.5 w-3.5" />
            {step + 1} de {questions?.length || 0}
          </div>
        )}
      </div>

      {!result && (
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-primary to-primary/60"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.4, ease: "easeOut" }}
          />
        </div>
      )}

      {!result && questions && (
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.25 }}
            className="glass-card rounded-xl p-6"
          >
            {isLastQuestion ? (
              <div className="space-y-6">
                <div className="space-y-2">
                  <h2 className="text-lg font-bold">
                    <Stars className="mr-2 inline-block h-5 w-5 text-primary" />
                    Qual seu grande sonho?
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    Conte pra gente o que você mais deseja realizar com dinheiro. Vamos calcular o melhor caminho.
                  </p>
                </div>
                <textarea
                  value={customDream}
                  onChange={(e) => setCustomDream(e.target.value)}
                  placeholder="Ex: Viajar para o Japão em 2027, Comprar meu primeiro carro, Dar entrada num apartamento..."
                  className="min-h-[120px] w-full rounded-xl border border-border/40 bg-background/50 p-4 text-sm outline-none transition-all focus:border-primary/50 focus:ring-1 focus:ring-primary/30"
                />
                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setStep((s) => s - 1)} className="gap-2">
                    <ArrowLeft className="h-4 w-4" /> Voltar
                  </Button>
                  <Button
                    onClick={handleDreamSubmit}
                    disabled={!customDream.trim() || recommend.isPending}
                    className="flex-1 gap-2"
                  >
                    {recommend.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" /> Analisando...
                      </>
                    ) : (
                      <>
                        Descobrir Meu Método <ArrowRight className="h-4 w-4" />
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="space-y-2">
                  <h2 className="text-lg font-bold">{currentQuestion?.question}</h2>
                  <p className="text-xs text-muted-foreground">Etapa {step + 1} de {questions.length}</p>
                </div>

                {currentQuestion?.type === "likert" && (
                  <LikertOptions
                    options={(currentQuestion.options as { value: number; label: string }[]) || []}
                    value={answers[currentQuestion.id] as number | undefined}
                    onChange={handleAnswer}
                  />
                )}

                {currentQuestion?.type === "multiple_choice" && (
                  <MultipleChoiceOptions
                    options={(currentQuestion.options as { value: string; label: string }[]) || []}
                    value={answers[currentQuestion.id] as string | undefined}
                    onChange={handleAnswer}
                  />
                )}

                <div className="flex gap-3">
                  {step > 0 && (
                    <Button variant="outline" onClick={() => setStep((s) => s - 1)} className="gap-2">
                      <ArrowLeft className="h-4 w-4" /> Voltar
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    onClick={() => {
                      if (step < questions.length - 1) {
                        setStep((s) => s + 1);
                      } else {
                        setStep(questions.length - 1);
                      }
                    }}
                    className="ml-auto gap-1 text-xs text-muted-foreground"
                  >
                    Pular <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      )}

      {recommend.isPending && !result && (
        <div className="glass-card flex flex-col items-center gap-4 rounded-xl p-12">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-medium">Analisando suas respostas...</p>
          <p className="text-xs text-muted-foreground">Calculando o método ideal com base em múltiplos fatores</p>
        </div>
      )}

      {result && (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {result.dream_advice && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                className="glass-card rounded-xl border border-primary/20 p-5"
              >
                <div className="flex items-start gap-3">
                  <Bot className="mt-0.5 h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium">Conselho para seu sonho</p>
                    <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{result.dream_advice}</p>
                  </div>
                </div>
              </motion.div>
            )}

            {result.top_recommendation && (
              <ResultCard method={result.top_recommendation} rank={0} isTop />
            )}

            {result.alternatives.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium text-muted-foreground">Alternativas que também combinam com você</h3>
                </div>
                {result.alternatives.slice(0, 3).map((m, i) => (
                  <ResultCard key={m.key} method={m} rank={i + 1} isTop={false} />
                ))}
              </div>
            )}

            <div className="flex justify-center gap-3 pt-2">
              <Button
                variant="outline"
                onClick={() => navigate("/fincas")}
                className="gap-2"
              >
                <Globe className="h-4 w-4" /> Ver Todos os Métodos
              </Button>
              <Button
                onClick={() => {
                  setAnswers({});
                  setStep(0);
                  setCustomDream("");
                  recommend.reset();
                }}
                className="gap-2"
              >
                Refazer Teste <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
}
