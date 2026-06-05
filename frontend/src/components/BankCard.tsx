import { useRef, useState } from "react";
import type { CSSProperties } from "react";

interface BankCardProps {
  id: string;
  gradient: string;
  flag: string;
  subtitle: string;
}

export function BankCard({ id: _, gradient, flag, subtitle }: BankCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [style, setStyle] = useState<CSSProperties>({});

  const handleMouseMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const maxDist = 250;
    const strength = Math.max(0, 1 - dist / maxDist);
    const maxPull = 8;
    const pullX = dist < 1 ? 0 : (dx / dist) * strength * maxPull;
    const pullY = dist < 1 ? 0 : (dy / dist) * strength * maxPull;
    setStyle({
      transform: `translate(${pullX}px, ${pullY}px) scale(1.03)`,
    });
  };

  const handleMouseLeave = () => {
    setStyle({ transform: "translate(0px, 0px) scale(1)" });
  };

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`group relative h-[200px] w-[280px] shrink-0 cursor-pointer overflow-hidden rounded-2xl p-5 text-white shadow-xl ${gradient}`}
      style={{
        ...style,
        transition: "transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)",
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-black/10" />
      <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-white/5 blur-xl" />
      <div className="absolute -bottom-6 -left-6 h-24 w-24 rounded-full bg-white/5 blur-2xl" />

      <div className="relative z-10 flex h-full flex-col justify-between">
        <div className="flex items-start justify-between">
          <span className="text-[10px] uppercase tracking-widest text-white/50">{flag}</span>
        </div>

        <div>
          <p className="mb-1 tracking-[4px] text-white/70 font-mono text-sm opacity-60">
            •••• •••• •••• ••••
          </p>
          <div className="flex items-end justify-between">
            <p className="text-xs font-medium tracking-wide text-white/80">FINCAS</p>
            <p className="text-[10px] font-mono text-white/40">{subtitle}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export const bankCardStyles: BankCardProps[] = [
  { id: "nubank", gradient: "bg-gradient-to-br from-[#820AD1] to-[#4B0082]", flag: "Brasil", subtitle: "Kakeibo" },
  { id: "inter", gradient: "bg-gradient-to-br from-[#FF7A00] to-[#CC6200]", flag: "Brasil", subtitle: "Tsumitate" },
  { id: "picpay", gradient: "bg-gradient-to-br from-[#21C25E] to-[#14803E]", flag: "Brasil", subtitle: "Lagom" },
  { id: "c6", gradient: "bg-gradient-to-br from-[#1A1A1A] to-[#3A3A3A]", flag: "Brasil", subtitle: "Regra 10" },
  { id: "itau", gradient: "bg-gradient-to-br from-[#FF6600] to-[#CC4E00]", flag: "Brasil", subtitle: "Desafio Suíço" },
  { id: "bradesco", gradient: "bg-gradient-to-br from-[#003399] to-[#001D66]", flag: "Brasil", subtitle: "Acordo a Dois" },
  { id: "santander", gradient: "bg-gradient-to-br from-[#EC0000] to-[#A30000]", flag: "Brasil", subtitle: "Limpeza" },
  { id: "caixa", gradient: "bg-gradient-to-br from-[#004C97] to-[#002E5C]", flag: "Brasil", subtitle: "Envelopes" },
];
