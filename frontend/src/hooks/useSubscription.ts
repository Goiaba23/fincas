import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useSubscriptionStatus() {
  return useQuery({
    queryKey: ["subscription", "status"],
    queryFn: () => api.get("/api/v1/subscriptions/status").then((r) => r.data),
    refetchInterval: 60_000,
  });
}

export function useStartTrial() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post("/api/v1/subscriptions/start-trial"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["subscription"] }),
  });
}

export function useActivateSubscription() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post("/api/v1/subscriptions/activate"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["subscription"] }),
  });
}

export function useCancelSubscription() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post("/api/v1/subscriptions/cancel"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["subscription"] }),
  });
}
