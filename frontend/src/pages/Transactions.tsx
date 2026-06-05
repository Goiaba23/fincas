import { useTransactions } from "@/hooks/useTransactions";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ArrowUpRight, ArrowDownLeft, Search } from "lucide-react";
import { useState } from "react";

export default function Transactions() {
  const { data: transactions, isLoading } = useTransactions();
  const [search, setSearch] = useState("");

  const filtered = transactions?.filter((t) =>
    t.description?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Transações</h1>
        <p className="text-sm text-muted-foreground">Histórico de transações</p>
      </div>

      <div className="flex items-center gap-3">
        <div className="glass-input flex flex-1 items-center gap-2 rounded-lg px-3 py-2">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Buscar transações..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
      </div>

      <div className="glass-card animate-slide-up rounded-xl overflow-hidden">
        <div className="border-b border-border/50 px-6 py-4">
          <h3 className="text-sm font-bold">💳 Todas as Transações</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {filtered?.length ?? 0} transações encontradas
          </p>
        </div>
        <div className="p-5">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : filtered?.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-sm text-muted-foreground">
                {search ? "Nenhuma transação encontrada para essa busca" : "Nenhuma transação encontrada"}
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              {filtered?.map((t) => (
                <div
                  key={t.id}
                  className="flex items-center justify-between rounded-lg px-4 py-3 transition-colors hover:bg-accent/20"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex h-9 w-9 items-center justify-center rounded-lg ${
                        t.type === "deposit" ? "bg-emerald-500/10" : "bg-red-500/10"
                      }`}
                    >
                      {t.type === "deposit" ? (
                        <ArrowUpRight className="h-4 w-4 text-emerald-500" />
                      ) : (
                        <ArrowDownLeft className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{t.description || "Sem descrição"}</p>
                      <p className="text-xs text-muted-foreground">{formatDate(t.date)}</p>
                    </div>
                  </div>
                  <span
                    className={`text-sm font-bold ${
                      t.type === "deposit" ? "text-emerald-500" : "text-red-500"
                    }`}
                  >
                    {t.type === "deposit" ? "+" : "-"}
                    {formatCurrency(t.amount)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
