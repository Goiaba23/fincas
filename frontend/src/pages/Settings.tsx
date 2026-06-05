import { Bell, Moon, Shield, Globe, CreditCard, User } from "lucide-react";

export default function Settings() {
  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Configurações</h1>
        <p className="text-sm text-muted-foreground">Gerencie suas preferências</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Section icon={<User className="h-4 w-4" />} title="Perfil" desc="Nome, email e foto do perfil" />
        <Section icon={<Bell className="h-4 w-4" />} title="Notificações" desc="Alertas e lembretes financeiros" />
        <Section icon={<Moon className="h-4 w-4" />} title="Aparência" desc="Tema claro/escuro" />
        <Section icon={<Globe className="h-4 w-4" />} title="Moeda" desc="Moeda padrão e formato regional" />
        <Section icon={<CreditCard className="h-4 w-4" />} title="Contas" desc="Conectar bancos e importar dados" />
        <Section icon={<Shield className="h-4 w-4" />} title="Segurança" desc="Privacidade e exportar dados" />
      </div>

      <div className="glass-card rounded-xl p-6">
        <h3 className="text-sm font-bold mb-4">Informações do App</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Versão</span>
            <span>0.1.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Framework</span>
            <span>React + FastAPI</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Banco de Dados</span>
            <span>PostgreSQL</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function Section({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <button className="glass-card group flex w-full items-center gap-4 rounded-xl p-5 text-left transition-all hover:shadow-lg">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/5 text-primary">
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium group-hover:text-primary transition-colors">{title}</p>
        <p className="text-xs text-muted-foreground">{desc}</p>
      </div>
    </button>
  );
}
