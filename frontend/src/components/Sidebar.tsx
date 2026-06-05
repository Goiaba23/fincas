import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ArrowRightLeft,
  PiggyBank,
  Target,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Bot,
  Globe,
  BookOpen,
  TrendingDown,
  CreditCard,
  Sparkles,
  Map,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

const mainNav = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/transactions", icon: ArrowRightLeft, label: "Transações" },
];

const methodNav = [
  { to: "/fincas", icon: Globe, label: "Métodos Financeiros" },
  { to: "/fincas/kakeibo", icon: BookOpen, label: "Kakeibo" },
  { to: "/fincas/micro-savings", icon: TrendingDown, label: "Micro-Poupança" },
  { to: "/fincas/metodos", icon: Map, label: "Mais Métodos" },
];

const financeNav = [
  { to: "/budgets", icon: PiggyBank, label: "Orçamentos" },
  { to: "/goals", icon: Target, label: "Metas" },
  { to: "/planos", icon: CreditCard, label: "Planos" },
];

const otherNav = [
  { to: "/assistant", icon: Bot, label: "Assistente IA" },
  { to: "/settings", icon: Settings, label: "Configurações" },
];

export function Sidebar({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  const { logout, user } = useAuth();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r transition-all duration-300",
        "glass-strong",
        open ? "w-64" : "w-16"
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-xs font-bold text-primary-foreground">
            F
          </div>
          {open && <span className="text-lg font-bold gradient-text">Fincas</span>}
        </div>
        <Button variant="ghost" size="icon" onClick={onToggle} className="h-7 w-7">
          {open ? <ChevronLeft className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-4 overflow-y-auto p-3">
        <NavSection label="Principal" open={open}>
          {mainNav.map((item) => (
            <NavItem key={item.to} item={item} open={open} />
          ))}
        </NavSection>

        <NavSection label="Métodos" open={open}>
          {methodNav.map((item) => (
            <NavItem key={item.to} item={item} open={open} />
          ))}
        </NavSection>

        <NavSection label="Financeiro" open={open}>
          {financeNav.map((item) => (
            <NavItem key={item.to} item={item} open={open} badge={item.to === "/planos" ? "Trial" : undefined} />
          ))}
        </NavSection>

        <NavSection label="Outros" open={open}>
          {otherNav.map((item) => (
            <NavItem key={item.to} item={item} open={open} />
          ))}
        </NavSection>
      </nav>

      <div className="border-t p-3">
        {open && user && (
          <div className="mb-2 flex items-center gap-2 rounded-lg bg-accent/30 px-3 py-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/20 text-xs font-bold text-primary">
              {user.display_name?.charAt(0)?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-foreground">{user.display_name}</div>
              <div className="truncate text-xs text-muted-foreground">{user.email}</div>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-muted-foreground hover:text-destructive"
          size="sm"
          onClick={logout}
        >
          <LogOut className="h-4 w-4" />
          {open && <span>Sair</span>}
        </Button>
      </div>
    </aside>
  );
}

function NavSection({ label, open, children }: { label: string; open: boolean; children: React.ReactNode }) {
  return (
    <div>
      {open && <div className="px-3 pb-1 text-[10px] font-bold uppercase tracking-[2px] text-muted-foreground/50">{label}</div>}
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}

function NavItem({ item, open, badge }: { item: { to: string; icon: React.ElementType; label: string }; open: boolean; badge?: string }) {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.to}
      className={({ isActive }) =>
        cn(
          "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-200",
          isActive
            ? "bg-primary/15 text-primary font-medium"
            : "text-muted-foreground hover:bg-accent/40 hover:text-foreground"
        )
      }
    >
      <Icon className="h-4 w-4 shrink-0" />
      {open && (
        <>
          <span className="flex-1">{item.label}</span>
          {badge && (
            <span className="inline-flex items-center gap-1 rounded-full bg-primary/20 px-2 py-0.5 text-[10px] font-bold text-primary">
              <Sparkles className="h-2.5 w-2.5" />
              {badge}
            </span>
          )}
        </>
      )}
    </NavLink>
  );
}
