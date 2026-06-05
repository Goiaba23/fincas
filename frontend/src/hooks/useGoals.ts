import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

interface Goal {
  id: string;
  name: string;
  target: number;
  current: number;
  progress: number;
  target_date: string | null;
  description: string | null;
}

export function useGoals() {
  return useQuery({
    queryKey: ["goals"],
    queryFn: async () => {
      const res = await api.get("/api/v1/goals/");
      return res.data as Goal[];
    },
  });
}

export function useCreateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: { name: string; target_amount: number; target_date?: string; description?: string }) => {
      const res = await api.post("/api/v1/goals/", data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["goals"] }),
  });
}

export function useUpdateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, current_amount }: { id: string; current_amount: number }) => {
      const res = await api.patch(`/api/v1/goals/${id}`, { current_amount });
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["goals"] }),
  });
}

export function useDeleteGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/goals/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["goals"] }),
  });
}
