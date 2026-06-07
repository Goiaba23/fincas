import { useState, useRef } from "react";
import { useCsvPreview, useCsvConfirm, useImportHistory } from "@/hooks/useImport";
import { useAccounts } from "@/hooks/useAccounts";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, ArrowRight } from "lucide-react";

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [accountId, setAccountId] = useState("");
  const [previewed, setPreviewed] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const previewMutation = useCsvPreview();
  const confirmMutation = useCsvConfirm();
  const { data: accounts } = useAccounts();
  const { data: history } = useImportHistory();

  const preview = previewMutation.data;

  const handlePreview = async () => {
    if (!file) return;
    setPreviewed(true);
    await previewMutation.mutateAsync({ file, account_id: accountId || undefined });
  };

  const handleConfirm = async () => {
    if (!file) return;
    await confirmMutation.mutateAsync({ file, account_id: accountId || undefined });
    setFile(null);
    setPreviewed(false);
    previewMutation.reset();
    if (fileRef.current) fileRef.current.value = "";
  };

  const reset = () => {
    setFile(null);
    setPreviewed(false);
    previewMutation.reset();
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Importar Transações</h1>
        <p className="text-sm text-muted-foreground">Importe extratos bancários em CSV</p>
      </div>

      <div className="glass-card rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-4">
          <div
            className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 cursor-pointer hover:bg-primary/20 transition-colors"
            onClick={() => fileRef.current?.click()}
          >
            <Upload className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null);
                setPreviewed(false);
                previewMutation.reset();
                confirmMutation.reset();
              }}
            />
            <p className="text-sm font-medium">
              {file ? file.name : "Clique para selecionar um arquivo CSV"}
            </p>
            <p className="text-xs text-muted-foreground">
              {file ? `${(file.size / 1024).toFixed(1)} KB` : "Formatos aceitos: CSV"}
            </p>
          </div>
          {accounts && accounts.length > 0 && (
            <select
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              className="rounded-lg border border-border/50 bg-background px-3 py-2 text-sm outline-none"
            >
              <option value="">Sem conta vinculada</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          )}
        </div>

        {file && !previewed && (
          <button
            onClick={handlePreview}
            disabled={previewMutation.isPending}
            className="glass-button flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium"
          >
            {previewMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            Visualizar Importação
          </button>
        )}

        {previewMutation.isError && (
          <div className="flex items-center gap-2 rounded-lg bg-red-500/10 p-3 text-sm text-red-500">
            <AlertCircle className="h-4 w-4" />
            {(previewMutation.error as any)?.response?.data?.detail || "Erro ao processar arquivo"}
          </div>
        )}

        {confirmMutation.data && (
          <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 p-3 text-sm text-emerald-500">
            <CheckCircle2 className="h-4 w-4" />
            {confirmMutation.data.imported} importadas, {confirmMutation.data.skipped} ignoradas (já existentes), {confirmMutation.data.failed} com erro
          </div>
        )}
      </div>

      {preview && (
        <div className="glass-card animate-slide-up rounded-xl overflow-hidden">
          <div className="border-b border-border/50 px-6 py-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold">Pré-visualização ({preview.total} transações)</h3>
            </div>
            <div className="flex gap-2">
              <button
                onClick={reset}
                className="rounded-lg px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                disabled={confirmMutation.isPending}
                className="glass-button flex items-center gap-1.5 rounded-lg px-4 py-1.5 text-sm font-medium"
              >
                {confirmMutation.isPending ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <ArrowRight className="h-3.5 w-3.5" />
                )}
                Confirmar Importação
              </button>
            </div>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {preview.preview.map((row, i) => (
              <div
                key={i}
                className="flex items-center justify-between px-6 py-2.5 transition-colors hover:bg-accent/20 border-b border-border/30 last:border-0 text-sm"
              >
                <span className="text-muted-foreground w-24">{formatDate(row.date)}</span>
                <span className="flex-1 truncate px-4">{row.description}</span>
                <span className={`font-medium w-24 text-right ${
                  row.type === "deposit" ? "text-emerald-500" : "text-red-500"
                }`}>
                  {row.type === "deposit" ? "+" : "-"}{formatCurrency(row.amount)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {history && history.length > 0 && (
        <div>
          <h2 className="text-lg font-bold mb-4">Histórico de Importações</h2>
          <div className="glass-card rounded-xl overflow-hidden">
            {history.map((h) => (
              <div
                key={h.id}
                className="flex items-center justify-between px-6 py-3 border-b border-border/50 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{h.filename}</p>
                    <p className="text-xs text-muted-foreground">{h.imported_rows} de {h.total_rows} importadas</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{formatDate(h.created_at)}</span>
                  {h.status === "completed" && (
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
