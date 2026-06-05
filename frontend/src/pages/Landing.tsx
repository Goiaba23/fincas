import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Star, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence, useInView } from "motion/react";
import { BankCard, bankCardStyles } from "@/components/BankCard";
import { MagneticButton } from "@/components/MagneticButton";
import { ContentReveal } from "@/components/SkeletonShimmer";
import { PricingSection } from "@/components/ui/pricing";
import { BackgroundGlow } from "@/components/ui/background-components";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const navItems = [
  { label: "Home", active: true },
  { label: "Métodos" },
  { label: "Preços" },
  { label: "FAQ" },
];

const testimonials = [
  {
    name: "Carlos Mendes",
    role: "Engenheiro, RJ",
    avatar: "CM",
    avatarImg: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=96&h=96&fit=crop&crop=face",
    stars: 5,
    text: "O método Lagom me salvou de estourar o orçamento todo mês. Os alerts de zona vermelha são geniais.",
  },
  {
    name: "Juliana Costa",
    role: "CEO, Fintech SP",
    avatar: "JC",
    avatarImg: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=96&h=96&fit=crop&crop=face",
    stars: 4,
    text: "Uso os 8 métodos simultaneamente. Ter 5 países num só app é o futuro da educação financeira.",
  },
  {
    name: "Rafael Oliveira",
    role: "Product Manager, Campinas",
    avatar: "RO",
    avatarImg: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=96&h=96&fit=crop&crop=face",
    stars: 5,
    text: "A Micro-Poupança automática já guardou mais de R$ 2.000 sem eu perceber. Funciona como mágica.",
  },
];

const faq = [
  { q: "O que é o Aethera?", a: "É uma plataforma que reúne 8 métodos financeiros de 5 países (Japão, Suécia, Holanda, Suíça e Brasil) em um só lugar. Você usa Kakeibo, Lagom, Tsumitate e mais — tudo com dashboards inteligentes." },
  { q: "Preciso ter experiência em finanças?", a: "Não. Cada método foi projetado para ser intuitivo. O Kakeibo, por exemplo, são apenas 4 perguntas por semana. O próprio app guia você." },
  { q: "Como funciona o período de trial?", a: "São 7 dias gratuitos com acesso a todos os métodos e funcionalidades. Seu cartão só é cobrado após o período. Cancele quando quiser sem multa." },
  { q: "Meus dados bancários estão seguros?", a: "Sim. Usamos criptografia AES-256, conformidade com a LGPD e integração via Open Finance. Seus dados nunca são compartilhados sem autorização." },
  { q: "Posso usar em mais de um dispositivo?", a: "Sim. O Aethera funciona no navegador (desktop e mobile). Basta fazer login na sua conta." },
  { q: "Quais métodos estão disponíveis?", a: "Kakeibo (Japão), Lagom (Suécia), Tsumitate (Holanda), Desafio Suíço (Suíça), Regra 50/30/20 (Brasil), Método de Pagamentos, Micro-Poupança e o Hub Central com visão 360°." },
];

function CountUp({ value, suffix = "" }: { value: string; suffix?: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  const num = parseFloat(value.replace(/[^\d.]/g, ""));
  const prefix = value.startsWith("R$") ? "R$ " : "";
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const duration = 1500;
    const step = Math.max(1, Math.floor(num / 60));
    const interval = setInterval(() => {
      start += step;
      if (start >= num) { start = num; clearInterval(interval); }
      setCount(start);
    }, duration / (num / step));
    return () => clearInterval(interval);
  }, [isInView, num]);

  return <span ref={ref}>{prefix}{isInView ? count : 0}{suffix}</span>;
}

const stats = [
  { value: "8", label: "Métodos financeiros", sub: "de 5 países" },
  { value: "7", label: "Dias grátis", sub: "sem compromisso" },
  { value: "R$ 0", label: "Taxas ocultas", sub: "zero anuidade" },
  { value: "100%", label: "Digital", sub: "100% online" },
];

const PLANS = [
  {
    name: "Trial",
    info: "7 dias grátis sem compromisso",
    price: { monthly: 0, yearly: 0 },
    features: [
      { text: "Todos os 8 métodos financeiros" },
      { text: "Dashboards completos" },
      { text: "Check-in semanal" },
      { text: "Micro-Poupança automática" },
    ],
    btn: { text: "Começar Trial", href: "/login" },
  },
  {
    highlighted: true,
    name: "Premium",
    info: "Acesso completo à plataforma",
    price: { monthly: 24.9, yearly: 199 },
    originalPrice: { monthly: 59.9, yearly: 479 },
    features: [
      { text: "Tudo do Trial" },
      { text: "Open Finance integrado" },
      { text: "IA Assistente Financeira" },
      { text: "Exportação de relatórios" },
      { text: "Suporte prioritário", tooltip: "Atendimento 24h por chat e e-mail" },
    ],
    btn: { text: "Assinar Agora", href: "/login" },
  },
];



export default function Landing() {
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [radius, setRadius] = useState(380);

  useEffect(() => {
    const update = () => setRadius(window.innerWidth < 768 ? 140 : 380);
    update();
    addEventListener("resize", update);
    return () => removeEventListener("resize", update);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 800);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("opacity-100", "translate-y-0");
            entry.target.classList.remove("opacity-0", "translate-y-8");
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const total = bankCardStyles.length;
  const totalAngle = 140;
  const stepAngle = totalAngle / (total - 1);
  const startAngle = -totalAngle / 2;

  return (
    <ContentReveal loadDelay={1200} shimmerDuration={3.1}>
    <div className="font-sans-body">
      {/* === HOOK: Antiga versão criativa === */}
      <BackgroundGlow className="relative overflow-hidden">
        {/* Video Background removido — substituído pelo BackgroundGlow */}

        {/* Navbar */}
        <nav className="relative z-10 mx-auto max-w-7xl px-6 py-5 md:px-8 md:py-6">
          <div className="flex items-center justify-between">
            <span className="font-serif-display text-2xl tracking-tight text-black md:text-3xl">
              Aethera<sup className="text-xs align-super">®</sup>
            </span>
            <div className="hidden items-center gap-8 md:flex">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href="#"
                  className={`text-sm transition-colors hover:text-black ${item.active ? "text-black" : "text-[#6F6F6F]"}`}
                >
                  {item.label}
                </a>
              ))}
              <button
                onClick={() => navigate("/login")}
                className="rounded-full bg-black px-6 py-2.5 text-sm text-white transition-transform hover:scale-105"
              >
                Começar grátis
              </button>
            </div>
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="relative z-20 flex md:hidden flex-col gap-1.5 p-2">
              <span className={`block h-0.5 w-5 bg-black transition-all duration-300 ${mobileMenuOpen ? "translate-y-2 rotate-45" : ""}`} />
              <span className={`block h-0.5 w-5 bg-black transition-all duration-300 ${mobileMenuOpen ? "opacity-0" : ""}`} />
              <span className={`block h-0.5 w-5 bg-black transition-all duration-300 ${mobileMenuOpen ? "-translate-y-2 -rotate-45" : ""}`} />
            </button>
          </div>
          {/* Mobile menu */}
          <motion.div
            className="absolute inset-x-0 top-0 z-10 overflow-hidden md:hidden"
            initial={false}
            animate={{ height: mobileMenuOpen ? "auto" : 0 }}
            transition={{ duration: 0.35, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <div className="flex flex-col gap-4 bg-white/90 backdrop-blur-2xl px-6 pb-8 pt-20">
              {navItems.map((item) => (
                <a key={item.label} href="#" className="text-lg font-medium text-[#1D1D1F]" onClick={() => setMobileMenuOpen(false)}>{item.label}</a>
              ))}
              <button
                onClick={() => { setMobileMenuOpen(false); navigate("/login"); }}
                className="mt-2 rounded-full bg-black px-6 py-3 text-sm text-white"
              >
                Começar grátis
              </button>
            </div>
          </motion.div>
        </nav>

        {/* Hero */}
        <section
          className="relative z-20 flex flex-col items-center justify-center px-6 pb-[120px] md:pb-[240px] text-center"
          style={{ paddingTop: "calc(8rem - 75px)" }}
        >
          <h1 className="animate-fade-rise max-w-7xl text-4xl font-bold leading-[1.05] tracking-[-0.03em] text-black sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl">
            O hub financeiro<br />
            <span className="bg-gradient-to-r from-[#22c55e] via-[#14b8a6] to-[#3b82f6] bg-clip-text text-transparent">que unifica tudo.</span>
          </h1>
          <p className="animate-fade-rise-delay mt-6 max-w-2xl text-base leading-relaxed text-[#6F6F6F] sm:text-lg">
            8 métodos de 5 países. Open Finance. IA. Um só painel com visual limpo e experiência nativa.
          </p>
          <div className="animate-fade-rise-delay-2 mt-10">
            <MagneticButton
              onClick={() => navigate("/login")}
              className="rounded-full bg-black px-14 py-4 text-sm font-semibold text-white shadow-lg shadow-black/10"
            >
              Começar grátis
            </MagneticButton>
          </div>
        </section>

        {/* Cards - Semi-circular fan */}
        <div className="absolute bottom-0 left-0 right-0 z-10 flex h-[400px] items-end justify-center overflow-hidden">
          <div className="relative mx-auto w-full max-w-6xl">
            <div className="absolute bottom-16 left-1/2 h-40 w-80 -translate-x-1/2 rounded-full bg-black/[0.03] blur-3xl" />
            {bankCardStyles.map((card, i) => {
              const angleDeg = startAngle + i * stepAngle;
              const angleRad = (angleDeg * Math.PI) / 180;
              const x = Math.sin(angleRad) * radius;
              const y = (1 - Math.cos(angleRad)) * radius * 0.45;
              const zIdx = Math.floor((i / (total - 1)) * 10);
              return (
                <div
                  key={card.id}
                  className="absolute bottom-0 left-1/2"
                  style={{
                    transform: `translateX(calc(-50% + ${x}px)) translateY(${visible ? -y : 100}px)`,
                    zIndex: zIdx,
                    transition: `transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1) ${0.12 + i * 0.06}s, opacity 0.8s ease ${0.1 + i * 0.06}s`,
                    opacity: visible ? 1 : 0,
                  }}
                >
                  <div
                    style={{
                      transform: `rotate(${visible ? angleDeg * 0.12 : 0}deg)`,
                      transition: `transform 1s cubic-bezier(0.34, 1.56, 0.64, 1) ${0.15 + i * 0.06}s`,
                    }}
                  >
                    <BankCard {...card} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </BackgroundGlow>

      {/* === SEÇÕES APPLE/iOS + THEYDO === */}
      <div className="bg-[#F5F5F7] text-[#1D1D1F] font-sans-body">

        {/* 1. Features/Value Proposition — Asymmetric Split */}
        <section className="px-6 py-28 md:py-36">
          <div className="mx-auto max-w-7xl">
            <div className="reveal flex flex-col items-center gap-16 opacity-0 transition-all duration-1000 md:flex-row">
              <div className="sticky md:top-32 flex-1 self-start space-y-6">
                <div className="inline-flex items-center gap-2 rounded-full bg-[#0052FF]/10 px-4 py-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#0052FF]" />
                  <span className="text-[11px] font-semibold uppercase tracking-widest text-[#0052FF]">AI · Open Finance · 8 Métodos</span>
                </div>
                <h2 className="text-4xl font-bold leading-[1.1] tracking-[-0.02em] md:text-5xl lg:text-6xl">
                  Planos de Economia<br />
                  <span className="text-gray-400 font-normal">personalizados pra você.</span>
                </h2>
                <p className="max-w-md text-base leading-relaxed text-gray-500">
                  A IA analisa seus gastos, define seu perfil e monta um plano sob medida com base no melhor método — seja Kakeibo, Lagom ou Tsumitate. Tudo automático.
                </p>
                <button onClick={() => navigate("/login")} className="rounded-full bg-black px-8 py-3.5 text-sm font-semibold text-white transition-all hover:bg-black/80 active:scale-[0.97]">
                  Ver planos
                </button>
              </div>
              <div className="flex-1">
                <div className="ios-card relative mx-auto w-full max-w-sm overflow-hidden" style={{ background: "#fff", borderRadius: "32px", boxShadow: "0 24px 80px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.02)" }}>
                  {/* App mockup header */}
                  <div className="flex items-center justify-between px-6 pt-6 pb-4">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black text-[10px] font-bold text-white">A</div>
                      <div>
                        <p className="text-[11px] font-semibold text-[#1D1D1F]">Resumo Financeiro</p>
                        <p className="text-[10px] text-gray-400">Atualizado há 2 min</p>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <div className="h-2 w-2 rounded-full bg-[#22c55e]" />
                      <div className="h-2 w-2 rounded-full bg-gray-200" />
                    </div>
                  </div>
                  {/* Savings tracker graph */}
                  <div className="mx-6 mb-4 rounded-2xl bg-[#F5F5F7] p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-gray-400">Evolução da Economia</span>
                      <span className="text-lg font-bold tracking-tight text-[#0052FF]">R$ 4.280</span>
                    </div>
                    <svg viewBox="0 0 280 100" className="w-full" preserveAspectRatio="none">
                      <defs>
                        <linearGradient id="graphGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#0052FF" stopOpacity="0.25" />
                          <stop offset="100%" stopColor="#0052FF" stopOpacity="0" />
                        </linearGradient>
                      </defs>
                      <path d="M0,80 Q20,78 40,70 T80,55 T120,50 T160,35 T200,30 T240,25 T280,20 L280,100 L0,100 Z" fill="url(#graphGrad)" />
                      <path d="M0,80 Q20,78 40,70 T80,55 T120,50 T160,35 T200,30 T240,25 T280,20" fill="none" stroke="#0052FF" strokeWidth="2.5" strokeLinecap="round" />
                      <circle cx="280" cy="20" r="3.5" fill="#0052FF" stroke="#fff" strokeWidth="2" />
                    </svg>
                    <div className="mt-2 flex justify-between text-[9px] text-gray-400">
                      <span>Jan</span><span>Fev</span><span>Mar</span><span>Abr</span><span>Mai</span><span>Jun</span>
                    </div>
                  </div>
                  {/* Micro-cards */}
                  <div className="mx-6 mb-6 grid grid-cols-2 gap-3">
                    <div className="rounded-xl bg-[#F5F5F7] p-3.5">
                      <p className="text-[10px] text-gray-400">Cashback</p>
                      <p className="text-sm font-bold text-[#1D1D1F]">R$ 187</p>
                      <div className="mt-1.5 h-1.5 w-full rounded-full bg-gray-200"><div className="h-full w-3/4 rounded-full bg-[#0052FF]" /></div>
                    </div>
                    <div className="rounded-xl bg-[#F5F5F7] p-3.5">
                      <p className="text-[10px] text-gray-400">Meta</p>
                      <p className="text-sm font-bold text-[#1D1D1F]">72%</p>
                      <div className="mt-1.5 h-1.5 w-full rounded-full bg-gray-200"><div className="h-full w-[72%] rounded-full bg-[#22c55e]" /></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Z-Pattern Connector line */}
        <div className="mx-auto h-px max-w-5xl bg-gradient-to-r from-transparent via-gray-200 to-transparent" />

        {/* 2. Immersive Editorial Banner — High-Contrast Dark Block */}
        <section className="px-6">
          <div className="mx-auto max-w-7xl">
            <div className="reveal relative overflow-hidden opacity-0 transition-all duration-1000" style={{ borderRadius: "36px", background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)", minHeight: "520px" }}>
              {/* Dark overlay + background pattern */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" style={{ backgroundImage: "radial-gradient(circle at 30% 50%, rgba(0,82,255,0.08) 0%, transparent 60%)" }} />
              {/* Content */}
              <div className="relative z-10 flex flex-col items-center justify-center px-8 py-24 md:py-32">
                <div className="mb-16 max-w-2xl text-center">
                  <span className="inline-block rounded-full bg-white/10 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-widest text-white/60">Resultados Reais</span>
                  <h2 className="mt-6 text-4xl font-bold leading-[1.1] tracking-[-0.02em] text-white md:text-5xl lg:text-6xl">
                    Sua saúde financeira<br />
                    <span className="text-white/40 font-normal">em números reais.</span>
                  </h2>
                  <p className="mx-auto mt-4 max-w-lg text-base leading-relaxed text-white/40">
                    Usuários Aethera reduzem dívidas em média 40% nos primeiros 90 dias. A IA monitora, ajusta e te avisa antes de qualquer deslize.
                  </p>
                </div>
                {/* Glassmorphism widgets */}
                <div className="flex flex-wrap justify-center gap-4">
                  <div className="rounded-2xl border border-white/10 p-5 backdrop-blur-2xl" style={{ background: "rgba(255,255,255,0.06)", minWidth: "200px" }}>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-white/40">Dívidas Pagas</span>
                      <svg width="36" height="36" viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3" />
                        <circle cx="18" cy="18" r="15.5" fill="none" stroke="#22c55e" strokeWidth="3" strokeDasharray="97.4" strokeDashoffset={97.4 * 0.0} strokeLinecap="round" transform="rotate(-90 18 18)" />
                      </svg>
                    </div>
                    <p className="mt-2 text-2xl font-bold text-white">100%</p>
                    <p className="text-xs text-white/40">taxa de sucesso</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 p-5 backdrop-blur-2xl" style={{ background: "rgba(255,255,255,0.06)", minWidth: "200px" }}>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-white/40">Despesas Fixas</span>
                      <span className="text-2xl font-bold text-[#22c55e]">25%</span>
                    </div>
                    <p className="mt-2 text-2xl font-bold text-white">Reduzidas</p>
                    <p className="text-xs text-white/40">em média nos primeiros 3 meses</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 p-5 backdrop-blur-2xl" style={{ background: "rgba(255,255,255,0.06)", minWidth: "200px" }}>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-white/40">Economia Gerada</span>
                    </div>
                    <p className="mt-2 text-2xl font-bold text-white">R$ 2.300</p>
                    <p className="text-xs text-white/40">em média por usuário ativo</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Bar — iOS-style */}
        <section className="border-y border-gray-200/60 bg-white/40 px-6 py-16">
          <div className="mx-auto max-w-6xl">
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
              {stats.map((s, i) => (
                <div key={i} className={`reveal text-center opacity-0 transition-all duration-1000`} style={{ transitionDelay: `${i * 150}ms` }}>
                  <p className="text-5xl font-bold tracking-tight text-[#1D1D1F] md:text-6xl lg:text-7xl">
                    <CountUp value={s.value} />
                  </p>
                  <p className="mt-1 text-sm font-semibold text-gray-600">{s.label}</p>
                  <p className="text-xs text-gray-400">{s.sub}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 3. 3-Card Grid System — How It Works */}
        <section className="px-6 py-28">
          <div className="mx-auto max-w-7xl">
            <div className="reveal mb-14 text-center opacity-0 transition-all duration-1000">
              <span className="inline-block rounded-full bg-[#0052FF]/10 px-4 py-1.5 text-[11px] font-semibold uppercase tracking-widest text-[#0052FF]">Como Funciona</span>
              <h2 className="mt-4 text-4xl font-bold leading-[1.1] tracking-[-0.02em] md:text-5xl lg:text-6xl">
                Seu advisor em<br />
                <span className="text-gray-400 font-normal">3 passos.</span>
              </h2>
            </div>
            <div className="reveal grid grid-cols-1 gap-8 opacity-0 transition-all duration-1000 delay-200 md:grid-cols-3">
              {/* Card 1 - Assessment */}
              <div className="group rounded-3xl border border-gray-200/40 bg-white/60 p-6 transition-all hover:shadow-xl" style={{ backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)" }}>
                <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0052FF]/10 text-[#0052FF]">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 4-6"/></svg>
                </div>
                <h3 className="text-lg font-bold text-[#1D1D1F]">Diagnóstico Financeiro</h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-500">
                  Conecte suas contas via Open Finance. Nossa IA analisa seu extrato, identifica padrões e mapeia seu perfil de gastos em minutos.
                </p>
              </div>
              {/* Card 2 - Strategy */}
              <div className="group rounded-3xl border border-gray-200/40 bg-white/60 p-6 transition-all hover:shadow-xl" style={{ backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)" }}>
                <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0052FF]/10 text-[#0052FF]">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                </div>
                <h3 className="text-lg font-bold text-[#1D1D1F]">Estratégia Sob Medida</h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-500">
                  O algoritmo escolhe o método ideal (Kakeibo, Lagom, Tsumitate ou a combinação deles) e monta um plano de ação semanal pra você.
                </p>
              </div>
              {/* Card 3 - Execution */}
              <div className="group rounded-3xl border border-gray-200/40 bg-white/60 p-6 transition-all hover:shadow-xl" style={{ backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)" }}>
                <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0052FF]/10 text-[#0052FF]">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
                </div>
                <h3 className="text-lg font-bold text-[#1D1D1F]">Economia Automática</h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-500">
                  Ative a Micro-Poupança e o app começa a guardar pequenos valores automaticamente. Você nem percebe, mas sua conta cresce todo mês.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* D. Testimonials — Card Grid */}
        <section className="px-6 py-28">
          <div className="mx-auto w-full max-w-5xl">
            <div className="reveal mb-14 text-center opacity-0 transition-all duration-1000">
              <h2 className="text-4xl font-bold tracking-[-0.02em] md:text-5xl lg:text-6xl">
                Quem já usa{" "}
                <span className="text-gray-400 font-normal">recomenda.</span>
              </h2>
            </div>
            <div className="reveal grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 opacity-0 transition-all duration-1000 delay-200">
              {testimonials.map((t, index) => (
                <div key={index} className="rounded-2xl border border-transparent bg-white/60 p-4 ring-1 ring-gray-200/40" style={{ backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)" }}>
                  <div className="flex gap-1" aria-label={`${t.stars || 5} out of 5 stars`}>
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={cn(
                          "size-4",
                          i < (t.stars || 5)
                            ? "fill-[#f59e0b] stroke-[#f59e0b]"
                            : "fill-gray-200 stroke-transparent"
                        )}
                      />
                    ))}
                  </div>
                  <p className="text-foreground my-4 text-sm leading-relaxed text-gray-500">{t.text}</p>
                  <div className="flex items-center gap-2">
                    <Avatar className="size-8 border border-transparent shadow ring-1 ring-gray-200/40">
                      <AvatarImage src={t.avatarImg} alt={t.name} />
                      <AvatarFallback>{t.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <span className="text-sm font-medium text-[#1D1D1F]">{t.name}</span>
                    <span aria-hidden className="size-1 rounded-full bg-gray-300" />
                    <span className="text-sm text-gray-400">{t.role}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* E. Pricing — Cards */}
        <section className="px-6 py-28">
          <PricingSection
            plans={PLANS}
            heading={<>Preço <span className="text-gray-400 font-normal">simples.</span></>}
            description="7 dias grátis. Depois, R$24,90/mês."
          />
        </section>

        {/* FAQ — iOS-style accordion */}
        <section className="border-y border-gray-200/60 px-6 py-28">
          <div className="mx-auto max-w-3xl">
            <div className="reveal mb-12 text-center opacity-0 transition-all duration-1000">
              <h2 className="text-4xl font-bold tracking-[-0.02em] md:text-5xl lg:text-6xl">
                Perguntas <span className="text-gray-400 font-normal">frequentes.</span>
              </h2>
            </div>
            <div className="space-y-2">
              {faq.map((item, i) => (
                <motion.div
                  key={i}
                  layout
                  className={`reveal overflow-hidden rounded-2xl border border-white/20 bg-white/50 opacity-0 transition-all duration-1000`}
                  style={{ borderRadius: "20px", backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)", transitionDelay: `${i * 100}ms` }}
                >
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="flex w-full items-center justify-between px-6 py-5 text-left"
                  >
                    <span className="text-sm font-medium text-[#1D1D1F]">{item.q}</span>
                    <motion.div
                      animate={{ rotate: openFaq === i ? 180 : 0 }}
                      transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
                    >
                      <ChevronDown className="h-4 w-4 text-gray-300" />
                    </motion.div>
                  </button>
                  <AnimatePresence initial={false}>
                    {openFaq === i && (
                      <motion.div
                        key="content"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.35, ease: [0.34, 1.56, 0.64, 1] }}
                      >
                        <div className="border-t border-gray-200/40 px-6 pb-5 pt-3">
                          <p className="text-sm leading-relaxed text-gray-500">{item.a}</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* 4. High-Contrast Footer & Final CTA */}
        <section className="px-6">
          <div className="mx-auto max-w-7xl">
            <div className="reveal relative overflow-hidden opacity-0 transition-all duration-1000" style={{ borderRadius: "36px 36px 0 0", background: "#111" }}>
              {/* Large CTA */}
              <div className="relative z-10 px-8 pb-8 pt-24 text-center md:pt-32">
                <h2 className="text-4xl font-bold leading-[1.1] tracking-[-0.02em] text-white md:text-5xl lg:text-7xl">
                  Vamos organizar<br />
                  <span className="text-white/40 font-normal">suas finanças. Juntos.</span>
                </h2>
                <p className="mx-auto mt-4 max-w-md text-base leading-relaxed text-white/30">
                  7 dias grátis. Sem compromisso. Cancele quando quiser.
                </p>
                <div className="mt-10">
                  <button onClick={() => navigate("/login")} className="rounded-full bg-white px-10 py-3.5 text-sm font-semibold text-[#111] shadow-lg transition-all hover:bg-white/90 active:scale-[0.97]">
                    Começar Agora
                  </button>
                </div>
              </div>
              {/* Divider */}
              <div className="relative z-10 mx-auto h-px max-w-6xl bg-gradient-to-r from-transparent via-white/10 to-transparent" />
              {/* Footer links */}
              <footer className="relative z-10 mx-auto max-w-7xl px-8 pb-12 pt-12">
                <div className="grid gap-10 md:grid-cols-4">
                  <div>
                    <span className="text-sm font-semibold tracking-tight text-white">
                      Aethera<sup className="ml-0.5 text-[8px] text-white/20">®</sup>
                    </span>
                    <p className="mt-2 text-xs leading-relaxed text-white/30">
                      8 métodos financeiros de 5 países. Open Finance, analytics e IA.
                    </p>
                  </div>
                  {[
                    { title: "Produto", links: ["Recursos", "Métodos", "Preços", "FAQ"] },
                    { title: "Empresa", links: ["Sobre", "Blog", "Carreiras", "Contato"] },
                    { title: "Legal", links: ["Privacidade", "Termos", "Cookies", "LGPD"] },
                  ].map((col) => (
                    <div key={col.title}>
                      <h4 className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-white/40">{col.title}</h4>
                      <ul className="space-y-2 text-xs">
                        {col.links.map((link) => (
                          <li key={link}>
                            <a href="#" className="text-white/30 transition-colors hover:text-white/60">{link}</a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
                <div className="mt-10 border-t border-white/5 pt-6 text-center text-[11px] text-white/20">
                  © 2026 Aethera. Todos os direitos reservados.
                </div>
              </footer>
            </div>
          </div>
        </section>
      </div>

      {/* Floating WhatsApp button */}
      <a
        href="https://wa.me/5547992921005"
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-[#22c55e] text-white shadow-lg shadow-[#22c55e]/20 transition-all hover:scale-110 active:scale-95"
        style={{ filter: "drop-shadow(0 4px 12px rgba(34,197,94,0.3))" }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      </a>
    </div>
    </ContentReveal>
  );
}
