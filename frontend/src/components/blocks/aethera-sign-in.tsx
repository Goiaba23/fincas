import { memo, useState, useRef, useCallback, ChangeEvent, FormEvent, forwardRef } from "react";
import { motion, AnimatePresence, useMotionTemplate, useMotionValue } from "motion/react";
import { Eye, EyeOff, ArrowRight, Check, ChevronLeft, Shield, TrendingDown, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePrefersDarkMode } from "@/hooks/usePrefersDarkMode";

const Input = memo(
  forwardRef(function Input(
    { className, type, status, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { status?: "default" | "success" | "error" },
    ref: React.ForwardedRef<HTMLInputElement>
  ) {
    const [visible, setVisible] = useState(false);
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const borderColor = status === "error" ? "border-red-500/50" : "border-[var(--border)]";
    const ringColor = status === "error" ? "focus-visible:ring-red-500/20 focus-visible:border-red-500/30" : "focus-visible:border-[var(--accent)]/30 focus-visible:ring-[var(--accent)]/20";

    function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent<HTMLDivElement>) {
      const { left, top } = currentTarget.getBoundingClientRect();
      mouseX.set(clientX - left);
      mouseY.set(clientY - top);
    }

    return (
      <motion.div
        style={{
          background: useMotionTemplate`radial-gradient(${visible ? "80px" : "0px"} circle at ${mouseX}px ${mouseY}px, rgba(13,71,161,0.08), transparent 70%)`,
        }}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        className="group/input rounded-xl p-[2px] transition duration-200"
      >
        <input
          type={type}
          className={cn(
            "flex h-12 w-full rounded-xl border bg-[var(--input-bg)] px-4 py-2 text-sm text-[var(--text-primary)] transition-all duration-200 group-hover/input:border-[var(--accent)]/30 placeholder:text-[var(--placeholder)]/50 focus-visible:ring-[2px] focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
            borderColor,
            ringColor,
            className
          )}
          ref={ref}
          {...props}
        />
      </motion.div>
    );
  })
);

Input.displayName = "Input";

const BottomGradient = () => (
  <>
    <span className="group-hover/btn:opacity-100 block transition duration-500 opacity-0 absolute h-px w-full -bottom-px inset-x-0 bg-gradient-to-r from-transparent via-white/60 to-transparent" />
    <span className="group-hover/btn:opacity-100 blur-sm block transition duration-500 opacity-0 absolute h-px w-1/2 mx-auto -bottom-px inset-x-10 bg-gradient-to-r from-transparent via-white/40 to-transparent" />
  </>
);

/* ─── Desktop Components (unchanged) ─── */

function DashboardMockup() {
  return (
    <motion.div
      className="w-full rounded-2xl bg-[var(--dash-card)] shadow-2xl shadow-black/10 will-change-transform"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.25, ease: [0.34, 1.56, 0.64, 1] }}
    >
      <div className="flex items-center justify-between border-b border-[var(--dash-border)] px-5 py-3">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#0D47A1] text-[10px] font-bold text-white">A</div>
          <span className="text-xs font-semibold text-[var(--text-primary)]">Aethera</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-green-400" />
          <span className="text-[10px] text-[var(--text-secondary)]">R$ 12.450,00</span>
        </div>
      </div>
      <div className="p-5 space-y-4">
        <div className="grid grid-cols-3 gap-2">
          {[
            { label: "Gastos", value: "R$ 2.340", bg: "var(--stat-expense-bg)", color: "var(--stat-expense-text)" },
            { label: "Receitas", value: "R$ 5.800", bg: "var(--stat-income-bg)", color: "var(--stat-income-text)" },
            { label: "Poupança", value: "R$ 3.460", bg: "var(--stat-savings-bg)", color: "var(--stat-savings-text)" },
          ].map((item) => (
            <div key={item.label} className="rounded-lg px-3 py-2" style={{ background: item.bg, color: item.color }}>
              <p className="text-[9px] font-medium opacity-60">{item.label}</p>
              <p className="text-xs font-bold">{item.value}</p>
            </div>
          ))}
        </div>
        <div className="rounded-lg border border-[var(--dash-border)] p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-[var(--text-primary)]">Evolução Patrimonial</span>
            <span className="text-[9px] text-green-500">+12.5%</span>
          </div>
          <svg viewBox="0 0 240 60" className="w-full h-10">
            <path d="M0 50 Q20 45 40 48 T80 35 T120 25 T160 18 T200 12 T240 8" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" />
            <defs>
              <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.15" />
                <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path d="M0 50 Q20 45 40 48 T80 35 T120 25 T160 18 T200 12 T240 8 L240 60 L0 60 Z" fill="url(#grad)" />
            <circle cx="240" cy="8" r="3" fill="var(--accent)" stroke="white" strokeWidth="2" />
          </svg>
        </div>
        <div>
          <span className="text-[10px] font-semibold text-[var(--text-primary)] mb-2 block">Transferências Automáticas</span>
          <div className="space-y-1.5">
            {[
              { name: "Kakeibo", value: "R$ 800", status: "Concluído" },
              { name: "Tsumitate", value: "R$ 500", status: "Pendente" },
              { name: "Micro-Poupança", value: "R$ 50", status: "Concluído" },
            ].map((t) => (
              <div key={t.name} className="flex items-center justify-between rounded-lg bg-[var(--dash-item)] px-3 py-2">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-[var(--accent)]" />
                  <span className="text-[10px] text-[var(--text-primary)]">{t.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold text-[var(--text-primary)]">{t.value}</span>
                  <span className={`text-[8px] px-1.5 py-0.5 rounded ${t.status === "Concluído" ? "bg-green-50 text-green-600" : "bg-yellow-50 text-yellow-600"}`}>{t.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="flex gap-2">
          <div className="flex-1 rounded-lg border border-[var(--dash-border)] px-3 py-2">
            <p className="text-[9px] text-[var(--text-secondary)]">Meta do Mês</p>
            <p className="text-xs font-bold text-[var(--text-primary)]">R$ 4.000</p>
          </div>
          <div className="flex-1 rounded-lg border border-[var(--dash-border)] px-3 py-2">
            <p className="text-[9px] text-[var(--text-secondary)]">Progresso</p>
            <p className="text-xs font-bold text-[var(--accent)]">87%</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function SecurityBadges() {
  return (
    <motion.div
      className="flex items-center justify-center gap-6"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.45, ease: "easeOut" }}
    >
      {[
        { name: "Stripe", color: "#6772E5" },
        { name: "Plaid", color: "#00C3E5" },
      ].map((b) => (
        <div key={b.name} className="flex items-center gap-1.5 text-white/40">
          <div className="h-5 w-5 rounded-full" style={{ background: b.color, opacity: 0.6 }} />
          <span className="text-[11px] font-medium tracking-wider">{b.name}</span>
        </div>
      ))}
      <div className="flex items-center gap-1.5 text-white/40">
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <span className="text-[11px] font-medium tracking-wider">Criptografia</span>
      </div>
    </motion.div>
  );
}

/* ─── Desktop Layout ─── */

function DesktopLayout({ isRegister, onToggleMode, error, onSubmit, email, onEmailChange, password, onPasswordChange, name, onNameChange, loading, success }: {
  isRegister: boolean; onSubmit: (e: FormEvent<HTMLFormElement>) => void; onToggleMode: () => void; error?: string;
  email: string; onEmailChange: (e: ChangeEvent<HTMLInputElement>) => void; password: string; onPasswordChange: (e: ChangeEvent<HTMLInputElement>) => void; name?: string; onNameChange?: (e: ChangeEvent<HTMLInputElement>) => void;
  loading?: boolean; success?: boolean;
}) {
  const [pwVisible, setPwVisible] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [submitted, setSubmitted] = useState(false);

  const touch = (field: string) => setTouched((p) => ({ ...p, [field]: true }));

  const fieldStatus = (name: string) => {
    if (!touched[name] && !submitted) return "default";
    return formErrors[name] ? "error" : "default";
  };

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!email) errs.email = "Email é obrigatório";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Email inválido";
    if (!password) errs.password = "Senha é obrigatória";
    else if (password.length < 6) errs.password = "Mínimo 6 caracteres";
    if (isRegister && !name) errs.name = "Nome é obrigatório";
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitted(true);
    if (validate()) onSubmit(e);
  };

  const easeSpring = [0.34, 1.56, 0.64, 1] as const;

  if (success) {
    return (
      <motion.div
        className="flex w-full max-w-md items-center justify-center rounded-[24px] bg-[var(--card-bg)] px-8 py-20"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ boxShadow: "var(--card-shadow)" }}
      >
        <motion.div className="text-center" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200, damping: 15 }}>
          <motion.div
            className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500"
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.1 }}
          >
            <Check className="h-8 w-8 text-white" />
          </motion.div>
          <h2 className="text-xl font-bold text-[var(--text-primary)]">{isRegister ? "Conta criada!" : "Bem-vindo de volta!"}</h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">Redirecionando para seu dashboard...</p>
        </motion.div>
      </motion.div>
    );
  }
  const formVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: easeSpring } },
  };

  return (
    <motion.div
      className="flex w-full max-w-5xl overflow-hidden rounded-[24px] bg-[var(--card-bg)]"
      initial={{ opacity: 0, scale: 0.97, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      style={{ boxShadow: "var(--card-shadow)" }}
    >
      {/* Left Panel */}
      <div className="flex w-full items-center justify-center p-8 md:w-3/5">
        <div className="w-full max-w-sm">
          <motion.div
            className="mb-10"
            initial={{ opacity: 0, rotateX: 8, y: -12 }}
            animate={{ opacity: 1, rotateX: 0, y: 0 }}
            transition={{ duration: 0.5, delay: 0.08, ease: [0.34, 1.56, 0.64, 1] }}
            style={{ perspective: 800 }}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#0D47A1] text-xs font-bold text-white">A</div>
          </motion.div>
          <motion.div className="mb-8" key={isRegister ? "h1" : "h2"} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
            <h1 className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">{isRegister ? "Criar sua conta" : "Comece agora"}</h1>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">{isRegister ? "Grátis por 7 dias. Depois R$ 24,90/mês." : "Configure seu dashboard de poupança automatizada."}</p>
          </motion.div>
          <motion.div className="mb-6 flex gap-3" key={isRegister ? "social2" : "social1"} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.15 }}>
            <motion.button
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-[var(--border)] py-2.5 text-sm font-medium text-[var(--text-secondary)] transition-colors hover:border-[var(--hover-border)] hover:bg-[var(--hover-bg)]"
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.97 }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              Google
            </motion.button>
            <motion.button
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-[var(--border)] py-2.5 text-sm font-medium text-[var(--text-secondary)] transition-colors hover:border-[var(--hover-border)] hover:bg-[var(--hover-bg)]"
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.97 }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
              Apple
            </motion.button>
          </motion.div>
          <div className="mb-6 flex items-center gap-3">
            <div className="h-px flex-1 bg-[var(--divider)]" />
            <span className="text-[11px] font-medium uppercase tracking-[0.12em] text-[var(--divider-text)]">ou email</span>
            <div className="h-px flex-1 bg-[var(--divider)]" />
          </div>
          <div className="mb-6 flex rounded-xl bg-[var(--toggle-bg)] p-1">
            <button
              className="relative flex-1 rounded-lg px-4 py-2.5 text-sm font-medium"
              onClick={() => { if (isRegister) { onToggleMode(); setFormErrors({}); } }}
            >
              <AnimatePresence>
                {!isRegister && (
                  <motion.div
                    className="absolute inset-0 rounded-lg bg-[var(--toggle-thumb)] shadow-sm"
                    initial={{ opacity: 0, scale: 0.92 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.92 }}
                    transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
                  />
                )}
              </AnimatePresence>
              <span className={`relative z-10 transition-colors duration-200 ${!isRegister ? "text-[var(--toggle-text)]" : "text-[var(--text-secondary)]"}`}>Entrar</span>
            </button>
            <button
              className="relative flex-1 rounded-lg px-4 py-2.5 text-sm font-medium"
              onClick={() => { if (!isRegister) { onToggleMode(); setFormErrors({}); } }}
            >
              <AnimatePresence>
                {isRegister && (
                  <motion.div
                    className="absolute inset-0 rounded-lg bg-[var(--toggle-thumb)] shadow-sm"
                    initial={{ opacity: 0, scale: 0.92 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.92 }}
                    transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
                  />
                )}
              </AnimatePresence>
              <span className={`relative z-10 transition-colors duration-200 ${isRegister ? "text-[var(--toggle-text)]" : "text-[var(--text-secondary)]"}`}>Cadastrar</span>
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <motion.div className="space-y-4" variants={formVariants} initial="hidden" animate="visible">
              <AnimatePresence mode="wait">
                {isRegister && (
                  <motion.div
                    key="name-field"
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: "auto", marginBottom: 16 }}
                    exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                    transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
                    className="overflow-hidden"
                  >
                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-[var(--text-label)]/80">Nome completo</label>
                      <Input type="text" placeholder="Seu nome" value={name} onChange={onNameChange} onBlur={() => touch("name")} status={fieldStatus("name")} />
                      {formErrors.name && <p className="mt-1 text-xs text-red-500">{formErrors.name}</p>}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <motion.div variants={itemVariants}>
                <label className="mb-1.5 block text-sm font-medium text-[var(--text-label)]/80">Email</label>
                <Input type="email" placeholder="seu@email.com" value={email} onChange={onEmailChange} onBlur={() => touch("email")} status={fieldStatus("email")} />
                {(formErrors.email || (error && !isRegister)) && <p className="mt-1 text-xs text-red-500">{formErrors.email || error}</p>}
              </motion.div>
              <motion.div variants={itemVariants}>
                <div className="mb-1.5 flex items-center justify-between">
                  <label className="text-sm font-medium text-[var(--text-label)]/80">Senha</label>
                  {!isRegister && <a href="#" className="text-xs font-medium text-[var(--link)] transition-colors hover:text-[var(--link)]/80">Esqueceu a senha?</a>}
                </div>
                <div className="relative">
                  <Input type={pwVisible ? "text" : "password"} placeholder="Mínimo 6 caracteres" value={password} onChange={onPasswordChange} onBlur={() => touch("password")} status={fieldStatus("password")} />
                  <button type="button" onClick={() => setPwVisible(!pwVisible)} className="absolute inset-y-0 right-0 flex items-center pr-4 text-sm text-[var(--text-secondary)]">
                    {pwVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {formErrors.password && <p className="mt-1 text-xs text-red-500">{formErrors.password}</p>}
                {error && isRegister && <p className="mt-1 text-xs text-red-500">{error}</p>}
              </motion.div>
              <motion.div variants={itemVariants}>
                <motion.button
                  type="submit"
                  disabled={loading}
                  className="group/btn relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-[var(--accent)] py-3 text-sm font-semibold text-white shadow-lg shadow-[var(--accent)]/30 transition-opacity disabled:opacity-60"
                  whileHover={loading ? {} : { scale: 1.02 }}
                  whileTap={loading ? {} : { scale: 0.97 }}
                >
                  {loading ? (
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  ) : (
                    <>
                      {isRegister ? "Criar conta grátis" : "Entrar"}
                      <motion.span
                        animate={{ x: [0, 4, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                      >
                        <ArrowRight className="h-4 w-4" />
                      </motion.span>
                    </>
                  )}
                  <BottomGradient />
                </motion.button>
              </motion.div>
            </motion.div>
          </form>
        </div>
      </div>
      {/* Right Panel */}
      <div className="relative hidden md:flex md:w-2/5 flex-col items-center px-8 py-8 gap-5 min-h-0" style={{ background: "#0D47A1" }}>
        <motion.div
          className="text-center shrink-0"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <h2 className="text-xl font-bold leading-tight text-white">A maneira mais simples<br />de gerenciar seu fluxo de caixa.</h2>
          <p className="mt-2 text-xs leading-relaxed text-white/60 max-w-xs mx-auto">Dashboard inteligente com automações, métricas em tempo real e integração com seus bancos.</p>
        </motion.div>
        <div className="w-full max-w-sm flex-1 min-h-0 flex items-center">
          <DashboardMockup />
        </div>
        <SecurityBadges />
      </div>
    </motion.div>
  );
}

/* ─── Mobile Flow ─── */

const goals = [
  { id: "emergency", icon: Shield, label: "Fundo de Emergência", desc: "Proteção contra imprevistos" },
  { id: "debt", icon: TrendingDown, label: "Redução de Dívidas", desc: "Quite suas pendências mais rápido" },
  { id: "investment", icon: TrendingUp, label: "Crescimento", desc: "Invista e veja seu patrimônio crescer" },
];

type Step = 1 | 2 | 3 | 4;

function SplashScreen({ onGetStarted, onHaveAccount }: { onGetStarted: () => void; onHaveAccount: () => void }) {
  return (
    <div className="relative flex h-full flex-col items-center justify-between overflow-hidden px-8 pb-10 pt-16" style={{ background: "#0D47A1" }}>
      {/* Decorative blobs */}
      <div className="absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/5 blur-3xl" />
      <div className="absolute -right-32 bottom-1/4 h-80 w-80 rounded-full bg-blue-400/10 blur-3xl" />
      <div className="absolute left-1/3 top-1/3 h-32 w-32 rounded-full bg-white/[0.03] blur-2xl" />

      {/* Logo at top */}
      <motion.div className="relative" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
          <span className="text-xl font-bold text-white">A</span>
        </div>
      </motion.div>

      {/* Center content */}
      <motion.div className="relative text-center" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.6, delay: 0.15, ease: [0.34, 1.56, 0.64, 1] }}>
        <div className="mb-4 flex justify-center gap-3">
          <div className="h-1.5 w-12 rounded-full bg-white/20" />
          <div className="h-1.5 w-4 rounded-full bg-white/40" />
        </div>
        <p className="text-[22px] font-bold leading-snug tracking-tight text-white">
          Better Habits.<br />Smarter Savings.
        </p>
        <p className="mt-3 text-sm text-white/50 max-w-[240px] mx-auto">
          Sua jornada financeira começa aqui.
        </p>
      </motion.div>

      {/* Bottom */}
      <motion.div className="relative w-full space-y-4" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5, delay: 0.3 }}>
        <motion.button onClick={onGetStarted} className="w-full rounded-2xl bg-white py-4 text-sm font-bold text-[var(--accent)] shadow-xl shadow-black/10" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>
          Get Started
        </motion.button>

        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-white/10" />
          <span className="text-[11px] font-medium uppercase tracking-[0.12em] text-white/30">ou</span>
          <div className="h-px flex-1 bg-white/10" />
        </div>

        <div className="flex gap-3">
          <button className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-white/20 py-3 text-sm font-medium text-white/70 transition-colors hover:border-white/40 hover:text-white/90">
            <svg width="16" height="16" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Google
          </button>
          <button className="flex flex-1 items-center justify-center gap-2 rounded-2xl border border-white/20 py-3 text-sm font-medium text-white/70 transition-colors hover:border-white/40 hover:text-white/90">
            <svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
            Apple
          </button>
        </div>

        <button onClick={onHaveAccount} className="w-full text-center text-sm font-medium text-white/50 transition-colors py-1 hover:text-white/80">
          I already have an account
        </button>
      </motion.div>
    </div>
  );
}

function EmailScreen({ email, onChange, onNext, onBack }: { email: string; onChange: (v: string) => void; onNext: () => void; onBack: () => void }) {
  const valid = /\S+@\S+\.\S+/.test(email);

  return (
    <div className="flex h-full flex-col bg-[var(--card-bg)]">
      {/* Top bar */}
      <div className="flex items-center gap-3 px-6 pt-12 pb-4">
        <button onClick={onBack} className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--input-bg)] text-[var(--text-primary)]">
          <ChevronLeft className="h-5 w-5" />
        </button>
        <span className="text-sm font-semibold text-[var(--text-primary)]">Voltar</span>
      </div>

      {/* Content */}
      <div className="flex-1 px-6 pt-4">
        <motion.h2 className="text-2xl font-bold text-[var(--text-primary)]" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          Qual seu email?
        </motion.h2>
        <motion.p className="mt-1 text-sm text-[var(--text-secondary)]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
          Enviaremos um código de verificação.
        </motion.p>

        <motion.div className="mt-8" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <label className="mb-2 text-xs font-medium text-[var(--text-label)]/60">Endereço de email</label>
            <div className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--input-bg)] px-4 py-3 transition-colors focus-within:border-[var(--accent)]/30 focus-within:ring-2 focus-within:ring-[var(--accent)]/20">
            <svg className="h-4 w-4 shrink-0 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            <input
              type="email"
              value={email}
              onChange={(e) => onChange(e.target.value)}
              placeholder="seu@email.com"
              autoFocus
              className="flex-1 bg-transparent text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--placeholder)]/40"
            />
          </div>
        </motion.div>
      </div>

      {/* Bottom */}
      <div className="px-6 pb-8">
        <motion.button
          onClick={onNext}
          disabled={!valid}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[var(--accent)] py-3.5 text-sm font-bold text-white shadow-lg shadow-[var(--accent)]/30 transition-opacity disabled:opacity-40"
          whileHover={valid ? { scale: 1.02 } : {}}
          whileTap={valid ? { scale: 0.97 } : {}}
        >
          Continue
          <ArrowRight className="h-4 w-4" />
        </motion.button>
      </div>
    </div>
  );
}

function PinScreen({ pin, onPinChange, onNext, onBack }: { pin: string; onPinChange: (v: string) => void; onNext: () => void; onBack: () => void }) {
  const maxLen = 8;
  const hasLetter = /[a-zA-Z]/.test(pin);
  const hasNumber = /\d/.test(pin);
  const valid = pin.length >= 6 && hasLetter && hasNumber;

  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="flex h-full flex-col bg-[var(--card-bg)]">
      {/* Top bar */}
      <div className="flex items-center gap-3 px-6 pt-12 pb-4">
        <button onClick={onBack} className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--input-bg)] text-[var(--text-primary)]">
          <ChevronLeft className="h-5 w-5" />
        </button>
        <span className="text-sm font-semibold text-[var(--text-primary)]">Voltar</span>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 -mt-8">
        <motion.h2 className="text-2xl font-bold text-[var(--text-primary)]" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          Crie sua senha
        </motion.h2>
        <motion.p className="mt-1 text-sm text-[var(--text-secondary)]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
          Mínimo 6 caracteres, letras e números.
        </motion.p>

        {/* Dots */}
        <motion.div className="mt-10 flex items-center gap-3" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          {Array.from({ length: maxLen }).map((_, i) => (
            <motion.div
              key={i}
              className={`h-3 w-3 rounded-full border-2 transition-colors ${pin.length > i ? "border-[var(--accent)] bg-[var(--accent)]" : pin.length === i ? "border-[var(--accent)]/40" : "border-[var(--border)]"}`}
              animate={pin.length > i ? { scale: [1, 1.3, 1] } : {}}
              transition={{ duration: 0.2 }}
            />
          ))}
        </motion.div>

        {/* Password input */}
        <div className="mt-6 w-full max-w-xs" onClick={() => inputRef.current?.focus()}>
          <input
            ref={inputRef}
            type="password"
            value={pin}
            onChange={(e) => {
              if (e.target.value.length <= maxLen) onPinChange(e.target.value);
            }}
            placeholder="• • • • • •"
            autoFocus
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--input-bg)] px-4 py-3 text-center text-sm tracking-[0.3em] text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--accent)]/30 focus:ring-2 focus:ring-[var(--accent)]/20 placeholder:text-[var(--placeholder)]/30"
          />
        </div>

        {/* Strength indicator */}
        {pin.length > 0 && (
          <motion.div className="mt-3 flex items-center gap-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className={`h-1.5 rounded-full transition-all ${hasLetter && hasNumber ? "w-12 bg-green-400" : pin.length >= 3 ? "w-8 bg-yellow-400" : "w-4 bg-red-400"}`} />
            <span className={`text-[11px] ${hasLetter && hasNumber ? "text-green-500" : pin.length >= 3 ? "text-yellow-500" : "text-red-400"}`}>
              {hasLetter && hasNumber ? "Forte" : pin.length >= 3 ? "Média" : "Fraca"}
            </span>
          </motion.div>
        )}
      </div>

      {/* Bottom */}
      <div className="px-6 pb-8">
        <motion.button
          onClick={onNext}
          disabled={!valid}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[var(--accent)] py-3.5 text-sm font-bold text-white shadow-lg shadow-[var(--accent)]/30 transition-opacity disabled:opacity-40"
          whileHover={valid ? { scale: 1.02 } : {}}
          whileTap={valid ? { scale: 0.97 } : {}}
        >
          Confirmar
          <Check className="h-4 w-4" />
        </motion.button>
      </div>
    </div>
  );
}

function GoalsScreen({ selected, onSelect, onFinish }: { selected: string | null; onSelect: (id: string) => void; onFinish: () => void }) {
  return (
    <div className="flex h-full flex-col bg-[var(--goals-page)]">
      <div className="px-6 pt-16 pb-6">
        <motion.h2 className="text-2xl font-bold text-[var(--text-primary)]" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          Qual seu objetivo?
        </motion.h2>
        <motion.p className="mt-1 text-sm text-[var(--text-secondary)]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
          Escolha seu foco principal de economia.
        </motion.p>
      </div>

      <div className="flex-1 px-6 space-y-3">
        {goals.map((g, i) => {
          const Icon = g.icon;
          const isSelected = selected === g.id;
          return (
            <motion.button
              key={g.id}
              onClick={() => onSelect(g.id)}
              className={`flex w-full items-center gap-4 rounded-2xl border-2 p-4 text-left transition-all ${isSelected ? "border-[var(--accent)] bg-[var(--goal-card)] shadow-md" : "border-transparent bg-[var(--goal-card)] shadow-sm"}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.08 }}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${isSelected ? "bg-[var(--accent)] text-white" : "bg-[var(--goal-icon-bg)] text-[var(--goal-icon-color)]"}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-[var(--text-primary)]">{g.label}</p>
                <p className="text-xs text-[var(--text-secondary)]">{g.desc}</p>
              </div>
              {isSelected && (
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 400, damping: 20 }}>
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--accent)]">
                    <Check className="h-3.5 w-3.5 text-white" />
                  </div>
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </div>

      <div className="px-6 pb-8 pt-4">
        <motion.button
          onClick={onFinish}
          disabled={!selected}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[var(--accent)] py-3.5 text-sm font-bold text-white shadow-lg shadow-[var(--accent)]/30 transition-opacity disabled:opacity-40"
          whileHover={selected ? { scale: 1.02 } : {}}
          whileTap={selected ? { scale: 0.97 } : {}}
        >
          Finalizar
          <Check className="h-4 w-4" />
        </motion.button>
      </div>
    </div>
  );
}

function MobileSignInFlow({ isDark, onSubmit, onEmailChange, onPasswordChange, onNameChange, email, isRegister: initialIsRegister, loading, success }: {
  isDark: boolean;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  onEmailChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onPasswordChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onNameChange?: (e: ChangeEvent<HTMLInputElement>) => void;
  email: string;
  isRegister: boolean;
  loading?: boolean;
  success?: boolean;
}) {
  const [step, setStep] = useState<Step>(1);
  const [pin, setPin] = useState("");
  const [goal, setGoal] = useState<string | null>(null);
  const [isRegister, setIsRegister] = useState(initialIsRegister);
  const [direction, setDirection] = useState(1);

  const handleEmailChange = (v: string) => {
    onEmailChange({ target: { value: v } } as ChangeEvent<HTMLInputElement>);
  };

  const handlePinComplete = (p: string) => {
    onPasswordChange({ target: { value: p } } as ChangeEvent<HTMLInputElement>);
  };

  const goForward = useCallback((s: Step) => { setDirection(1); setStep(s); }, []);
  const goBack = useCallback((s: Step) => { setDirection(-1); setStep(s); }, []);

  const handleFinish = () => {
    handlePinComplete(pin);
    if (isRegister && onNameChange && email.includes("@")) {
      onNameChange({ target: { value: email.split("@")[0] } } as ChangeEvent<HTMLInputElement>);
    }
    const form = document.createElement("form");
    const event = { preventDefault: () => {}, target: form, currentTarget: form } as unknown as FormEvent<HTMLFormElement>;
    onSubmit(event);
  };

  const slideVariants = {
    enter: (dir: number) => ({ x: dir > 0 ? 120 : -120, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit: (dir: number) => ({ x: dir > 0 ? -120 : 120, opacity: 0 }),
  };

  const renderScreen = () => {
    switch (step) {
      case 1: return <SplashScreen onGetStarted={() => goForward(2)} onHaveAccount={() => { setIsRegister(false); goForward(2); }} />;
      case 2: return <EmailScreen email={email} onChange={handleEmailChange} onNext={() => goForward(3)} onBack={() => goBack(1)} />;
      case 3: return <PinScreen pin={pin} onPinChange={setPin} onNext={() => { handlePinComplete(pin); isRegister ? goForward(4) : handleFinish(); }} onBack={() => goBack(2)} />;
      case 4: return <GoalsScreen selected={goal} onSelect={setGoal} onFinish={handleFinish} />;
    }
  };

  if (success) {
    return (
      <div className="flex h-dvh w-full flex-col items-center justify-center overflow-hidden bg-[var(--card-bg)]" data-theme={isDark ? "dark" : "light"}>
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200, damping: 15 }}>
          <motion.div
            className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500"
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.1 }}
          >
            <Check className="h-8 w-8 text-white" />
          </motion.div>
          <h2 className="text-xl font-bold text-center text-[var(--text-primary)]">{isRegister ? "Conta criada!" : "Bem-vindo de volta!"}</h2>
          <p className="mt-1 text-sm text-center text-[var(--text-secondary)]">Redirecionando para seu dashboard...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex h-dvh w-full flex-col overflow-hidden" data-theme={isDark ? "dark" : "light"}>
      {/* Loading overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div
            className="absolute inset-0 z-[100] flex items-center justify-center bg-black/20 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div
              className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-lg"
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
            >
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--accent)] border-t-transparent" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress bar */}
      <div className="absolute top-0 left-0 right-0 z-50 flex gap-1 px-4 pt-3">
        {[1, 2, 3, 4].map((s) => (
          <div key={s} className={`h-1 flex-1 rounded-full transition-colors duration-500 ${step >= s ? (step === 1 ? "bg-white" : "bg-[var(--accent)]") : (step === 1 ? "bg-white/30" : "bg-[var(--progress-bg)]")}`} />
        ))}
      </div>
      <AnimatePresence mode="wait" custom={direction}>
        <motion.div
          key={step}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="flex-1"
        >
          {renderScreen()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

/* ─── Main Export ─── */

export function AetheraSignIn({
  isRegister,
  onSubmit,
  onToggleMode,
  error,
  email,
  onEmailChange,
  password,
  onPasswordChange,
  name,
  onNameChange,
  loading,
  success,
}: {
  isRegister: boolean;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  onToggleMode: () => void;
  error?: string;
  email: string;
  onEmailChange: (e: ChangeEvent<HTMLInputElement>) => void;
  password: string;
  onPasswordChange: (e: ChangeEvent<HTMLInputElement>) => void;
  name?: string;
  onNameChange?: (e: ChangeEvent<HTMLInputElement>) => void;
  loading?: boolean;
  success?: boolean;
}) {
  const isDark = usePrefersDarkMode();

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--page-bg)]" data-theme={isDark ? "dark" : "light"}>
      {/* Mobile: hidden on md+ */}
      <div className="w-full h-full md:hidden">
        <MobileSignInFlow isDark={isDark} onSubmit={onSubmit} onEmailChange={onEmailChange} onPasswordChange={onPasswordChange} onNameChange={onNameChange} email={email} isRegister={isRegister} loading={loading} success={success} />
      </div>
      {/* Desktop: hidden below md */}
      <div className="hidden md:flex w-full items-center justify-center p-4">
        <DesktopLayout
          isRegister={isRegister}
          onSubmit={onSubmit}
          onToggleMode={onToggleMode}
          error={error}
          email={email}
          onEmailChange={onEmailChange}
          password={password}
          onPasswordChange={onPasswordChange}
          name={name}
          onNameChange={onNameChange}
          loading={loading}
          success={success}
        />
      </div>
    </div>
  );
}

