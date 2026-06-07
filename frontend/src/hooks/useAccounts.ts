import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export interface Account {
  id: string;
  name: string;
  type: string;
  balance: number;
  currency_code: string;
  credit_limit: number | null;
  card_brand: string | null;
  card_last_digits: string | null;
  color: string | null;
  icon: string | null;
  statement_close_day: number | null;
  statement_due_day: number | null;
}

export function useAccounts() {
  return useQuery({
    queryKey: ["accounts"],
    queryFn: async () => {
      const res = await api.get("/api/v1/accounts/");
      return res.data as Account[];
    },
  });
}

export function useCreateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      name: string;
      account_type: string;
      balance?: number;
      color?: string;
      icon?: string;
      credit_limit?: number;
      card_brand?: string;
      card_last_digits?: string;
      statement_close_day?: number;
      statement_due_day?: number;
    }) => {
      const res = await api.post("/api/v1/accounts/", data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
  });
}
