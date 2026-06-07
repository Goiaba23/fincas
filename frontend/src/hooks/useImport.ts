import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

interface PreviewRow {
  date: string;
  description: string;
  amount: number;
  type: string;
  category_id: string | null;
  import_hash: string;
}

interface PreviewResponse {
  preview: PreviewRow[];
  total: number;
}

interface ImportHistoryItem {
  id: string;
  filename: string;
  status: string;
  total_rows: number;
  imported_rows: number;
  created_at: string;
}

export function useCsvPreview() {
  return useMutation({
    mutationFn: async ({ file, account_id }: { file: File; account_id?: string }) => {
      const form = new FormData();
      form.append("file", file);
      if (account_id) form.append("account_id", account_id);
      const res = await api.post("/api/v1/imports/csv/preview", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data as PreviewResponse;
    },
  });
}

export function useCsvConfirm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ file, account_id }: { file: File; account_id?: string }) => {
      const form = new FormData();
      form.append("file", file);
      if (account_id) form.append("account_id", account_id);
      const res = await api.post("/api/v1/imports/csv/confirm", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["import-history"] });
    },
  });
}

export function useImportHistory() {
  return useQuery({
    queryKey: ["import-history"],
    queryFn: async () => {
      const res = await api.get("/api/v1/imports/history");
      return res.data as ImportHistoryItem[];
    },
  });
}
