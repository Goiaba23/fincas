import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

interface Budget {
  id: string;
  name: string;
  type: string;
  currency: string;
  monthly_income: number;
  ready_to_assign: number;
}

interface Envelope {
  category_id: string;
  category_name: string;
  category_color: string | null;
  group_id: string | null;
  assigned: number;
  activity: number;
  available: number;
  carryover: number;
  is_carryover_enabled: boolean;
}

interface EnvelopeState {
  budget_id: string;
  budget_name: string;
  year: number;
  month: number;
  total_assigned: number;
  total_activity: number;
  total_available: number;
  envelopes: Envelope[];
  currency: string;
}

interface EnvelopeHistory {
  month: string;
  assigned: number;
  activity: number;
  available: number;
}

export function useBudgets() {
  return useQuery({
    queryKey: ["budgets"],
    queryFn: async () => {
      const res = await api.get("/api/v1/budgets/");
      return res.data as Budget[];
    },
  });
}

export function useEnvelopeState(budgetId: string | undefined, year: number, month: number) {
  return useQuery({
    queryKey: ["envelope-state", budgetId, year, month],
    queryFn: async () => {
      const res = await api.get(`/api/v1/budgets/${budgetId}/envelopes`, {
        params: { year, month },
      });
      return res.data as EnvelopeState;
    },
    enabled: !!budgetId,
  });
}

export function useEnvelopeHistory(budgetId: string, categoryId: string, months = 6) {
  return useQuery({
    queryKey: ["envelope-history", budgetId, categoryId, months],
    queryFn: async () => {
      const res = await api.get(
        `/api/v1/budgets/${budgetId}/envelopes/${categoryId}/history`,
        { params: { months } }
      );
      return res.data as { category_id: string; history: EnvelopeHistory[] };
    },
    enabled: !!budgetId && !!categoryId,
  });
}

export function useCreateBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { name: string; monthly_income?: number }) => {
      const res = await api.post("/api/v1/budgets/", data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });
}

export function useAssignEnvelope() {
  return useMutation({
    mutationFn: async (data: { budget_id: string; category_id: string; amount: number; month: string }) => {
      const res = await api.post("/api/v1/budgets/envelopes/assign", data);
      return res.data;
    },
  });
}
