import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  PiggyBank,
  ChevronLeft,
  ChevronRight,
  Plus,
  Wallet,
  RotateCcw,
} from "lucide-react";
import { useBudgets, useEnvelopeState, useCreateBudget, useAssignEnvelope } from "@/hooks/useBudget";
import { formatCurrency } from "@/lib/utils";
import { Button } from "@/components/ui/button";

function getMonthName(m: number) {
  const names = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
  ];
  return names[m - 1];
}

function getCurrentMonth() {
  const d = new Date();
  return { year: d.getFullYear(), month: d.getMonth() + 1 };
}

export default function Budgets() {
  const { data: budgets, isLoading: budgetsLoading } = useBudgets();
  const [{ year, month }, setMonthDate] = useState(getCurrentMonth);
  const [selectedBudgetId, setSelectedBudgetId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newBudgetName, setNewBudgetName] = useState("");

  const activeBudgetId = selectedBudgetId || budgets?.[0]?.id;

  const { data: envelopeState, isLoading: envLoading } = useEnvelopeState(activeBudgetId, year, month);
  const createBudget = useCreateBudget();
  const assignEnvelope = useAssignEnvelope();

  const prevMonth = () => {
    if (month === 1) setMonthDate({ year: year - 1, month: 12 });
    else setMonthDate({ year, month: month - 1 });
  };

  const nextMonth = () => {
    if (month === 12) setMonthDate({ year: year + 1, month: 1 });
    else setMonthDate({ year, month: month + 1 });
  };

  const isCurrentMonth = year === getCurrentMonth().year && month === getCurrentMonth().month;

  const handleCreateBudget = async () => {
    if (!newBudgetName.trim()) return;
    const res = await createBudget.mutateAsync({ name: newBudgetName.trim() });
    setSelectedBudgetId(res.id);
    setShowCreate(false);
    setNewBudgetName("");
  };

  const handleAssign = async (categoryId: string, amount: number) => {
    if (!activeBudgetId) return;
    const monthStr = `${year}-${String(month).padStart(2, "0")}`;
    await assignEnvelope.mutateAsync({
      budget_id: activeBudgetId,
      category_id: categoryId,
      amount,
      month: monthStr,
    });
  };

  const envList = envelopeState?.envelopes ?? [];
  const groupedEnvelopes = envList.reduce<Record<string, typeof envList>>(
    (acc, env) => {
      const gid = env.group_id || "outros";
      if (!acc[gid]) acc[gid] = [];
      acc[gid].push(env);
      return acc;
    },
    {}
  );

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <PiggyBank className="h-6 w-6 text-primary" />
            Orçamento por Envelopes
          </h1>
          <p className="text-sm text-muted-foreground">
            Gerencie seu dinheiro usando o método de envelope
          </p>
        </div>
        <div className="flex items-center gap-2">
          {budgets && budgets.length > 0 && (
            <select
              value={activeBudgetId || ""}
              onChange={(e) => setSelectedBudgetId(e.target.value)}
              className="glass-input rounded-lg px-3 py-2 text-sm"
            >
              {budgets.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          )}
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1 h-4 w-4" /> Novo Orçamento
          </Button>
        </div>
      </div>

      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass-card rounded-xl p-5"
          >
            <div className="flex items-center gap-3">
              <input
                value={newBudgetName}
                onChange={(e) => setNewBudgetName(e.target.value)}
                placeholder="Nome do orçamento..."
                className="glass-input flex-1 rounded-lg px-4 py-2 text-sm"
                onKeyDown={(e) => e.key === "Enter" && handleCreateBudget()}
              />
              <Button size="sm" onClick={handleCreateBudget} disabled={!newBudgetName.trim()}>Criar</Button>
              <Button size="sm" variant="ghost" onClick={() => setShowCreate(false)}>Cancelar</Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={prevMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="text-center">
            <p className="text-lg font-bold">
              {getMonthName(month)} {year}
            </p>
            {isCurrentMonth && (
              <p className="text-xs text-muted-foreground">Mês atual</p>
            )}
          </div>
          <Button variant="outline" size="icon" onClick={nextMonth} disabled={isCurrentMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {budgetsLoading || envLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : envelopeState ? (
        <div className="space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-xl overflow-hidden"
          >
            <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-6">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Wallet className="h-4 w-4" />
                Ready to Assign
              </div>
              <div className="flex items-baseline gap-2">
                <span className={`text-4xl font-bold ${envelopeState.total_available >= 0 ? "text-emerald-500" : "text-red-500"}`}>
                  {formatCurrency(envelopeState.total_available)}
                </span>
                <span className="text-sm text-muted-foreground">disponível</span>
              </div>
              <div className="mt-3 flex gap-6 text-sm">
                <div>
                  <span className="text-muted-foreground">Total orçado: </span>
                  <span className="font-medium">{formatCurrency(envelopeState.total_assigned)}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Atividade: </span>
                  <span className={`font-medium ${envelopeState.total_activity < 0 ? "text-red-500" : "text-emerald-500"}`}>
                    {formatCurrency(envelopeState.total_activity)}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

          {Object.entries(groupedEnvelopes).map(([groupId, envelopes]) => (
            <motion.div
              key={groupId}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card rounded-xl overflow-hidden"
            >
              <div className="border-b border-border/50 px-6 py-3 flex items-center justify-between">
                <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wider">
                  {envelopes[0]?.category_name || "Sem grupo"}
                </h3>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>Orçado</span>
                  <span>Atividade</span>
                  <span>Disponível</span>
                </div>
              </div>
              <div className="p-2">
                {envelopes.map((env, i) => (
                  <EnvelopeRow
                    key={env.category_id}
                    envelope={env}
                    index={i}
                    onAssign={(amount) => handleAssign(env.category_id, amount)}
                  />
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass-card rounded-xl p-12 text-center">
          <PiggyBank className="mx-auto h-12 w-12 text-muted-foreground/30" />
          <h3 className="mt-4 text-lg font-bold">Nenhum orçamento encontrado</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Crie seu primeiro orçamento para começar a usar o método de envelopes
          </p>
          <Button className="mt-4" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1 h-4 w-4" /> Criar Orçamento
          </Button>
        </div>
      )}
    </div>
  );
}

function EnvelopeRow({
  envelope,
  index,
  onAssign,
}: {
  envelope: {
    category_id: string;
    category_name: string;
    category_color: string | null;
    assigned: number;
    activity: number;
    available: number;
    carryover: number;
    is_carryover_enabled: boolean;
  };
  index: number;
  onAssign: (amount: number) => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editAmount, setEditAmount] = useState("");

  const availablePercent = envelope.assigned > 0
    ? Math.min((envelope.available / envelope.assigned) * 100, 200)
    : envelope.available > 0 ? 100 : 0;

  const barColor = envelope.available >= 0 ? "bg-emerald-500" : "bg-red-500";
  const textColor = envelope.available >= 0 ? "text-emerald-500" : "text-red-500";

  const handleSave = () => {
    const amt = parseFloat(editAmount);
    if (!isNaN(amt)) {
      onAssign(amt);
    }
    setIsEditing(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      className="group flex items-center justify-between rounded-lg px-4 py-3 transition-all hover:bg-accent/20"
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div
          className="h-2 w-2 rounded-full shrink-0"
          style={{ backgroundColor: envelope.category_color || "#6B7280" }}
        />
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">{envelope.category_name}</p>
          {envelope.carryover !== 0 && (
            <p className="text-[10px] text-muted-foreground flex items-center gap-1">
              <RotateCcw className="h-2.5 w-2.5" />
              Carryover: {formatCurrency(envelope.carryover)}
            </p>
          )}
        </div>
      </div>

      <div className="hidden sm:flex items-center flex-1 max-w-[200px] mx-4">
        <div className="w-full h-1.5 rounded-full bg-muted/50 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${availablePercent}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className={`h-full rounded-full ${barColor}`}
          />
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm shrink-0">
        {isEditing ? (
          <div className="flex items-center gap-1">
            <input
              type="number"
              step="0.01"
              value={editAmount}
              onChange={(e) => setEditAmount(e.target.value)}
              className="glass-input w-20 rounded px-2 py-1 text-xs text-right"
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && handleSave()}
            />
            <button onClick={handleSave} className="text-xs text-primary font-medium">OK</button>
            <button onClick={() => setIsEditing(false)} className="text-xs text-muted-foreground">X</button>
          </div>
        ) : (
          <button
            onClick={() => { setEditAmount(String(envelope.assigned)); setIsEditing(true); }}
            className="text-right font-medium w-16 hover:text-primary transition-colors"
          >
            {formatCurrency(envelope.assigned)}
          </button>
        )}
        <span className={`w-16 text-right ${envelope.activity < 0 ? "text-red-400" : "text-emerald-400"}`}>
          {formatCurrency(envelope.activity)}
        </span>
        <span className={`w-16 text-right font-bold ${textColor}`}>
          {formatCurrency(envelope.available)}
        </span>
      </div>
    </motion.div>
  );
}
