import { useState } from "react";
import { useAccounts, useCreateAccount, type Account } from "@/hooks/useAccounts";
import { formatCurrency } from "@/lib/utils";
import { CreditCard as CreditCardIcon, Building2, PiggyBank, Wallet, Plus, ChevronRight } from "lucide-react";
import { CreditCard } from "react-credit-cards-library";

const ACCOUNT_ICONS: Record<string, React.ReactNode> = {
  checking: <Building2 className="h-4 w-4" />,
  savings: <PiggyBank className="h-4 w-4" />,
  credit_card: <CreditCardIcon className="h-4 w-4" />,
  cash: <Wallet className="h-4 w-4" />,
};

export default function Accounts() {
  const { data: accounts, isLoading } = useAccounts();
  const createAccount = useCreateAccount();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", type: "checking", balance: "", color: "#6366f1", credit_limit: "", card_brand: "", card_last_digits: "" });

  const creditCards = accounts?.filter((a) => a.type === "credit_card") ?? [];
  const otherAccounts = accounts?.filter((a) => a.type !== "credit_card") ?? [];

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name) return;
    await createAccount.mutateAsync({
      name: form.name,
      account_type: form.type,
      balance: parseFloat(form.balance) || 0,
      color: form.color,
      card_brand: form.card_brand || undefined,
      card_last_digits: form.card_last_digits || undefined,
      credit_limit: form.type === "credit_card" ? (parseFloat(form.credit_limit) || 0) : undefined,
    });
    setForm({ name: "", type: "checking", balance: "", color: "#6366f1", credit_limit: "", card_brand: "", card_last_digits: "" });
    setShowForm(false);
  };

  const totalBalance = accounts?.reduce((s, a) => s + a.balance, 0) ?? 0;
  const totalCreditLimit = creditCards.reduce((s, a) => s + (a.credit_limit ?? 0), 0);
  const totalCreditUsed = creditCards.reduce((s, a) => s + Math.abs(Math.min(a.balance, 0)), 0);

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Contas</h1>
          <p className="text-sm text-muted-foreground">Gerencie suas contas e cartões</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="glass-button flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium"
        >
          <Plus className="h-4 w-4" />
          Nova Conta
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="glass-card animate-slide-up rounded-xl p-5 space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <input
              placeholder="Nome da conta"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
            <select
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
              className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            >
              <option value="checking">Conta Corrente</option>
              <option value="savings">Poupança</option>
              <option value="credit_card">Cartão de Crédito</option>
              <option value="cash">Dinheiro</option>
            </select>
            <input
              type="number" step="0.01"
              placeholder="Saldo inicial"
              value={form.balance}
              onChange={(e) => setForm({ ...form, balance: e.target.value })}
              className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
            {form.type === "credit_card" && (
              <>
                <input
                  type="number" step="0.01"
                  placeholder="Limite do cartão"
                  value={form.credit_limit}
                  onChange={(e) => setForm({ ...form, credit_limit: e.target.value })}
                  className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
                />
                <input
                  placeholder="Bandeira (visa, mastercard, elo)"
                  value={form.card_brand}
                  onChange={(e) => setForm({ ...form, card_brand: e.target.value })}
                  className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
                />
                <input
                  placeholder="Últimos 4 dígitos"
                  maxLength={4}
                  value={form.card_last_digits}
                  onChange={(e) => setForm({ ...form, card_last_digits: e.target.value })}
                  className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none focus:border-primary"
                />
              </>
            )}
          </div>
          <div className="flex gap-2">
            <button type="submit" className="glass-button rounded-lg px-4 py-2 text-sm font-medium">Criar</button>
            <button type="button" onClick={() => setShowForm(false)} className="rounded-lg px-4 py-2 text-sm text-muted-foreground hover:text-foreground">Cancelar</button>
          </div>
        </form>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <SummaryCard title="Saldo Total" value={formatCurrency(totalBalance)} />
        <SummaryCard title="Limite Total" value={formatCurrency(totalCreditLimit)} />
        <SummaryCard title="Fatura Total" value={formatCurrency(totalCreditUsed)} />
      </div>

      {creditCards.length > 0 && (
        <div>
          <h2 className="text-lg font-bold mb-4">Cartões de Crédito</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {creditCards.map((card) => (
              <CreditCard3D key={card.id} account={card} />
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-bold mb-4">Contas</h2>
        <div className="glass-card rounded-xl overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : otherAccounts.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-sm text-muted-foreground">Nenhuma conta criada</p>
            </div>
          ) : (
            otherAccounts.map((acc) => (
              <div
                key={acc.id}
                className="flex items-center justify-between px-6 py-4 transition-colors hover:bg-accent/20 border-b border-border/50 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-10 w-10 items-center justify-center rounded-xl text-white"
                    style={{ backgroundColor: acc.color || "#6366f1" }}
                  >
                    {ACCOUNT_ICONS[acc.type] ?? <Building2 className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{acc.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{acc.type === "credit_card" ? "Cartão" : acc.type === "checking" ? "Conta Corrente" : acc.type === "savings" ? "Poupança" : acc.type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-bold ${acc.balance < 0 ? "text-red-500" : "text-emerald-500"}`}>
                    {formatCurrency(acc.balance)}
                  </span>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="glass-card rounded-xl p-5">
      <p className="text-xs text-muted-foreground">{title}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
    </div>
  );
}

function CreditCard3D({ account }: { account: Account }) {
  const number = account.card_last_digits
    ? `**** **** **** ${account.card_last_digits}`
    : "**** **** **** ****";

  return (
    <div className="transform transition-all hover:scale-[1.02]">
      <CreditCard
        number={number}
        name={account.name.toUpperCase()}
        expiry="12/28"
        cvc="***"
        focus=""
        richColors
        locale="pt-BR"
        cardSizes={{ width: "100%", maxWidth: "360px", height: "220px" }}
      />
      <div className="mt-3 flex items-center justify-between px-1">
        <div>
          <p className="text-xs text-muted-foreground">Limite</p>
          <p className="text-sm font-bold">{formatCurrency(account.credit_limit ?? 0)}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Usado</p>
          <p className="text-sm font-bold text-red-500">{formatCurrency(Math.abs(Math.min(account.balance, 0)))}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Disponível</p>
          <p className="text-sm font-bold text-emerald-500">
            {formatCurrency((account.credit_limit ?? 0) - Math.abs(Math.min(account.balance, 0)))}
          </p>
        </div>
      </div>
    </div>
  );
}
