import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export interface DashboardData {
  balance: number;
  monthly: {
    income: number;
    expense: number;
    net: number;
    savings_rate: number;
  };
  category_breakdown: {
    category: string;
    group: string;
    amount: number;
    percentage: number;
  }[];
  recent_transactions: {
    id: string;
    description: string;
    amount: number;
    type: "deposit" | "withdrawal";
    date: string;
    category: string | null;
  }[];
  goals: {
    id: string;
    name: string;
    target_amount: number;
    current_amount: number;
    progress_pct: number;
    is_completed: boolean;
  }[];
  budget_progress: {
    category_id: string;
    category_name: string;
    budgeted: number;
    spent: number;
    remaining: number;
    progress_pct: number;
  }[];
  net_worth_history: {
    month: string;
    year: number;
    income: number;
    expense: number;
    net: number;
    date: string;
  }[];
  balance_sparkline: {
    month: string;
    value: number;
  }[];
}

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const { data } = await api.get("/api/v1/dashboard");
      return data;
    },
    staleTime: 30_000,
  });
}
