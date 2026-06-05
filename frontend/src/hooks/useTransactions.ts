import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: string;
  date: string;
}

export function useTransactions() {
  return useQuery({
    queryKey: ["transactions"],
    queryFn: async () => {
      const res = await api.get("/api/v1/transactions/");
      return res.data as Transaction[];
    },
  });
}
