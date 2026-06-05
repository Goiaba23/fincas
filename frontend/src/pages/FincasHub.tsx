import { createElement } from "react";
import { useNavigate } from "react-router-dom";
import { PiggyBank, TrendingDown, Target, ShieldCheck, Flame, HeartHandshake, Scissors, Globe, ArrowRight, Sparkles } from "lucide-react";

const methods = [
  { id: "kakeibo", icon: PiggyBank, gradient: "method-gradient-1", flag: "🇯🇵", origin: "Japão", benefit: "Reduz gastos 25-35%", subtitle: "4 perguntas que transformam sua relação com o dinheiro", route: "/fincas/kakeibo" },
  { id: "tsumitate", icon: TrendingDown, gradient: "method-gradient-2", flag: "🇯🇵", origin: "Japão", benefit: "Poupe sem perceber", subtitle: "Micro-poupança automática estilo Tsumitate NISA", route: "/fincas/micro-savings" },
  { id: "lagom", icon: Target, gradient: "method-gradient-3", flag: "🇸🇪", origin: "Suécia", benefit: "Não sobra nem falta", subtitle: "Gastômetro que mede seu ritmo de gastos contra o ideal", route: "/fincas/lagom" },
  { id: "regra10", icon: ShieldCheck, gradient: "method-gradient-4", flag: "🇳🇱", origin: "Holanda", benefit: "85% dos holandeses poupam", subtitle: "10% automático antes de qualquer gasto", route: "/fincas/metodos" },
  { id: "desafio-suico", icon: Flame, gradient: "method-gradient-5", flag: "🇨🇭", origin: "Suíça", benefit: "Economize R$ 8.000+", subtitle: "Streak de pagar 100% da fatura todo mês", route: "/fincas/metodos" },
  { id: "acordo-dois", icon: HeartHandshake, gradient: "method-gradient-6", flag: "🇳🇱", origin: "Holanda", benefit: "0 brigas por dinheiro", subtitle: "Orçamento compartilhado justo para casais", route: "/fincas/metodos" },
  { id: "limpeza", icon: Scissors, gradient: "method-gradient-7", flag: "🇸🇪", origin: "Suécia", benefit: "Economia R$ 2.400/ano", subtitle: "Auditoria de assinaturas e gastos esquecidos", route: "/fincas/metodos" },
  { id: "envelopes", icon: Globe, gradient: "method-gradient-8", flag: "🇧🇷", origin: "Brasil", benefit: "Cada real tem propósito", subtitle: "Orçamento envelope digital com Pix e caixinhas", route: "/fincas/metodos" },
];

export default function FincasHub() {
  const navigate = useNavigate();

  return (
    <div className="animate-fade-in space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Métodos Financeiros</h1>
          <p className="text-sm text-muted-foreground">Seu dinheiro merece sabedoria global — 8 métodos de 5 países</p>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-xs font-medium text-primary">
          <Sparkles className="h-3.5 w-3.5" />
          Ativo
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {methods.map((m, i) => {
          const Icon = m.icon;
          return (
            <button
              key={m.id}
              onClick={() => navigate(m.route)}
              className="group glass-card flex flex-col rounded-xl p-5 text-left animate-slide-up"
              style={{ animationDelay: `${i * 0.08}s` }}
            >
              <div className="flex items-start justify-between">
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${m.gradient} text-white shadow-lg`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-2xl">{m.flag}</span>
              </div>
              <div className="mt-4 flex-1 space-y-1">
                <h3 className="text-sm font-bold group-hover:text-primary transition-colors">{m.origin}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{m.subtitle}</p>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-semibold text-primary">
                  {m.benefit}
                </span>
                <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 transition-all group-hover:opacity-100 group-hover:translate-x-0.5" />
              </div>
            </button>
          );
        })}
      </div>

      <div className="glass-card rounded-xl overflow-hidden animate-slide-up" style={{ animationDelay: "0.6s" }}>
        <div className="border-b border-border/50 px-6 py-4">
          <h3 className="text-sm font-bold">🗺️ Mapa dos Métodos</h3>
          <p className="text-xs text-muted-foreground mt-0.5">Métodos ativos e descobertas nos próximos meses</p>
        </div>
        <div className="grid gap-3 p-5 sm:grid-cols-2 lg:grid-cols-4">
          {methods.slice(0, 4).map((m) => (
            <button
              key={m.id}
              onClick={() => navigate(m.route)}
              className="group flex items-center gap-3 rounded-lg border border-border/40 p-3 transition-all hover:bg-accent/30 hover:border-primary/20"
            >
              <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${m.gradient} text-white`}>
                {createElement(m.icon, { className: "h-4 w-4" })}
              </div>
              <div className="min-w-0 text-left">
                <p className="truncate text-xs font-medium">{m.flag} {m.origin}</p>
                <p className="text-[10px] text-muted-foreground">{m.benefit}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
