import { useRef, useState, type ReactNode } from "react";

interface MagneticButtonProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
}

export function MagneticButton({ children, onClick, className = "" }: MagneticButtonProps) {
  const ref = useRef<HTMLButtonElement>(null);
  const [style, setStyle] = useState<React.CSSProperties>({});

  const handleMouseMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const maxDist = 200;
    const strength = Math.max(0, 1 - dist / maxDist);
    const maxPull = 6;
    const pullX = dist < 1 ? 0 : (dx / dist) * strength * maxPull;
    const pullY = dist < 1 ? 0 : (dy / dist) * strength * maxPull;
    setStyle({
      transform: `translate(${pullX}px, ${pullY}px) scale(1.04)`,
    });
  };

  const handleMouseLeave = () => {
    setStyle({
      transform: "translate(0px, 0px) scale(1)",
    });
  };

  return (
    <button
      ref={ref}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
      style={{
        ...style,
        transition: "transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)",
      }}
    >
      {children}
    </button>
  );
}
