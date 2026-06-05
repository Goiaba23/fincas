import { useEffect, useRef, useState } from "react";
import { Wifi } from "lucide-react";

interface CardConfig {
  id: string;
  gradient: string;
  flag: string;
  subtitle: string;
}

interface CardCarousel3DProps {
  cards: CardConfig[];
}

export function CardCarousel3D({ cards }: CardCarousel3DProps) {
  const [isPaused, setIsPaused] = useState(false);
  const angleRef = useRef(0);
  const animRef = useRef<number | null>(null);

  const count = cards.length;
  const spreadAngle = 140;
  const stepAngle = spreadAngle / (count - 1);
  const startAngle = -spreadAngle / 2;

  useEffect(() => {
    let lastTime = performance.now();

    const animate = (now: number) => {
      const dt = now - lastTime;
      lastTime = now;
      if (!isPaused) {
        angleRef.current += dt * 0.0008;
        if (angleRef.current > 1) angleRef.current -= 1;
      }
      animRef.current = requestAnimationFrame(animate);
    };

    animRef.current = requestAnimationFrame(animate);
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [isPaused]);

  const t = angleRef.current;
  const easeInOut = (x: number) =>
    x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;

  const fanProgress = easeInOut(t);

  return (
    <div
      className="relative mx-auto h-[520px] w-full"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="absolute bottom-0 left-1/2 z-20 -translate-x-1/2">
        <div className="mx-auto h-20 w-20 rounded-full bg-primary/20 blur-3xl" />
      </div>

      {cards.map((card, i) => {
        const targetAngle = startAngle + i * stepAngle;
        const currentAngle = targetAngle * fanProgress;
        const radians = (currentAngle * Math.PI) / 180;
        const radius = 340;
        const yOffset = -40;
        const x = Math.sin(radians) * radius;
        const y = Math.cos(radians) * radius * 0.35 + yOffset;
        const zIndex = Math.floor(
          (i / (count - 1)) * 10 + (1 - fanProgress) * 5
        );

        const opacity = 0.4 + 0.6 * fanProgress;
        const scale = 0.85 + 0.15 * fanProgress;

        return (
          <div
            key={card.id}
            className="absolute left-1/2 bottom-24 transition-transform duration-75"
            style={{
              transform: `translateX(-140px) translateY(${-y}px) translateX(${x}px) scale(${scale})`,
              zIndex,
              opacity,
              transformOrigin: "bottom center",
            }}
          >
            <div
              className={`group h-[220px] w-[280px] cursor-pointer overflow-hidden rounded-2xl p-5 text-white shadow-2xl transition-all duration-500 hover:scale-105 hover:shadow-[0_0_40px_rgba(255,255,255,0.15)] ${card.gradient}`}
            >
              <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-black/20" />
              <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/5 blur-xl" />
              <div className="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-white/5 blur-2xl" />

              <div className="relative z-10 flex h-full flex-col justify-between">
                <div className="flex items-start justify-between">
                  <span className="text-3xl">{card.flag}</span>
                  <Wifi className="h-5 w-5 rotate-90 text-white/60" />
                </div>

                <div>
                  <p className="mb-1 tracking-[5px] text-white/70 font-mono text-sm">
                    •••• •••• •••• 2026
                  </p>
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-white/50">Titular</p>
                      <p className="text-xs font-semibold tracking-wide">FINCAS</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] uppercase tracking-wider text-white/50">Método</p>
                      <p className="text-xs font-semibold font-mono">{card.subtitle}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
