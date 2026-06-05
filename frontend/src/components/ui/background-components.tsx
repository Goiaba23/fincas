import { cn } from "@/lib/utils";

interface BackgroundGlowProps {
  className?: string;
  children?: React.ReactNode;
}

export function BackgroundGlow({ className, children }: BackgroundGlowProps) {
  return (
    <div className={cn("relative min-h-screen w-full bg-white", className)}>
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `
            radial-gradient(circle at center, #FFF991 0%, transparent 70%)
          `,
          opacity: 0.6,
          mixBlendMode: "multiply",
        }}
      />
      {children}
    </div>
  );
}
