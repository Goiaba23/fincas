export function NubankLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none">
      <rect width="100" height="100" rx="16" fill="#820AD1" />
      <rect width="100" height="100" rx="16" fill="url(#nubank-g)" />
      <text x="50" y="64" textAnchor="middle" fontSize="44" fontWeight="800" fontFamily="Inter, sans-serif" fill="white" letterSpacing="-2">N</text>
      <defs>
        <linearGradient id="nubank-g" x1="0" y1="0" x2="100" y2="100">
          <stop stopColor="#a855f7" stopOpacity="0.3" />
          <stop offset="1" stopColor="transparent" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function InterLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none">
      <rect width="100" height="100" rx="16" fill="#FF7A00" />
      <rect width="100" height="100" rx="16" fill="url(#inter-g)" />
      <text x="50" y="64" textAnchor="middle" fontSize="40" fontWeight="700" fontFamily="Inter, sans-serif" fill="white">I</text>
      <defs>
        <linearGradient id="inter-g" x1="0" y1="0" x2="100" y2="100">
          <stop stopColor="#ff9a44" stopOpacity="0.3" />
          <stop offset="1" stopColor="transparent" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function PicPayLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none">
      <rect width="100" height="100" rx="16" fill="#21C25E" />
      <text x="50" y="64" textAnchor="middle" fontSize="36" fontWeight="700" fontFamily="Inter, sans-serif" fill="white">P</text>
    </svg>
  );
}

export function C6Logo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 120 100" fill="none">
      <rect width="120" height="100" rx="16" fill="#1A1A1A" />
      <text x="60" y="64" textAnchor="middle" fontSize="32" fontWeight="700" fontFamily="Inter, sans-serif" fill="white" letterSpacing="-1">C6</text>
    </svg>
  );
}

export function ItauLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 120 100" fill="none">
      <rect width="120" height="100" rx="16" fill="#FF6600" />
      <text x="60" y="64" textAnchor="middle" fontSize="36" fontWeight="800" fontFamily="Inter, sans-serif" fill="white" letterSpacing="-1">IT</text>
    </svg>
  );
}

export function BradescoLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 140 100" fill="none">
      <rect width="140" height="100" rx="16" fill="#003399" />
      <text x="70" y="60" textAnchor="middle" fontSize="22" fontWeight="700" fontFamily="Inter, sans-serif" fill="white" letterSpacing="-0.5">BRADESCO</text>
      <text x="70" y="82" textAnchor="middle" fontSize="11" fontWeight="500" fontFamily="Inter, sans-serif" fill="#6699ff">Desde 1943</text>
    </svg>
  );
}

export function SantanderLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 140 100" fill="none">
      <rect width="140" height="100" rx="16" fill="#EC0000" />
      <text x="70" y="60" textAnchor="middle" fontSize="20" fontWeight="700" fontFamily="Inter, sans-serif" fill="white" letterSpacing="2">SANTANDER</text>
      <text x="70" y="82" textAnchor="middle" fontSize="10" fontWeight="500" fontFamily="Inter, sans-serif" fill="#ff6666">ESTILO</text>
    </svg>
  );
}

export function CaixaLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 120 100" fill="none">
      <rect width="120" height="100" rx="16" fill="#004C97" />
      <text x="60" y="58" textAnchor="middle" fontSize="26" fontWeight="700" fontFamily="Inter, sans-serif" fill="white" letterSpacing="1">CAIXA</text>
      <text x="60" y="80" textAnchor="middle" fontSize="9" fontWeight="500" fontFamily="Inter, sans-serif" fill="#66aaff">ECONÔMICA FEDERAL</text>
    </svg>
  );
}

export function VisaLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 20" fill="none">
      <text x="0" y="16" fontSize="16" fontWeight="800" fontFamily="Inter, sans-serif" fill="currentColor" letterSpacing="-0.5">VISA</text>
    </svg>
  );
}

export function MastercardLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 20" fill="none">
      <circle cx="18" cy="10" r="10" fill="#EB001B" />
      <circle cx="36" cy="10" r="10" fill="#F79E1B" opacity="0.7" />
      <text x="48" y="14" fontSize="10" fontWeight="600" fontFamily="Inter, sans-serif" fill="currentColor">MC</text>
    </svg>
  );
}

export function EloLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 20" fill="none">
      <text x="0" y="16" fontSize="14" fontWeight="700" fontFamily="Inter, sans-serif" fill="currentColor" letterSpacing="0">ELO</text>
    </svg>
  );
}
