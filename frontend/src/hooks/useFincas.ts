import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useMetodos() {
  return useQuery({
    queryKey: ["fincas", "metodos"],
    queryFn: () => api.get("/api/v1/fincas/metodos").then((r) => r.data),
  });
}

export function useKakeiboReport(workspaceId?: string) {
  return useQuery({
    queryKey: ["fincas", "kakeibo", "report", workspaceId],
    queryFn: () => api.get(`/api/v1/fincas/kakeibo/report/${workspaceId}`).then((r) => r.data),
    enabled: !!workspaceId,
  });
}

export function useKakeiboStreak(workspaceId?: string) {
  return useQuery({
    queryKey: ["fincas", "kakeibo", "streak", workspaceId],
    queryFn: () => api.get(`/api/v1/fincas/kakeibo/streak/${workspaceId}`).then((r) => r.data),
    enabled: !!workspaceId,
  });
}

export function useCreateKakeiboEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => api.post("/api/v1/fincas/kakeibo/entry", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["fincas", "kakeibo"] });
    },
  });
}

export function useMicroSavingsRules(workspaceId?: string) {
  return useQuery({
    queryKey: ["fincas", "micro-savings", "rules", workspaceId],
    queryFn: () => api.get(`/api/v1/fincas/micro-savings/rules/${workspaceId}`).then((r) => r.data),
    enabled: !!workspaceId,
  });
}

export function useCreateMicroSavingsRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => api.post("/api/v1/fincas/micro-savings/rule", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["fincas", "micro-savings"] }),
  });
}

export function useDeleteMicroSavingsRule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ruleId: string) => api.delete(`/api/v1/fincas/micro-savings/rule/${ruleId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["fincas", "micro-savings"] }),
  });
}

export function useExecuteRoundup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => api.post("/api/v1/fincas/micro-savings/roundup", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["fincas", "micro-savings"] });
      qc.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}

export function useLagomBurndown(workspaceId?: string, month?: string) {
  return useQuery({
    queryKey: ["fincas", "lagom", "burndown", workspaceId, month],
    queryFn: () => {
      const params = month ? `?month=${month}` : "";
      return api.get(`/api/v1/fincas/lagom/burndown/${workspaceId}${params}`).then((r) => r.data);
    },
    enabled: !!workspaceId,
  });
}

export function useDesafioSuico(workspaceId?: string) {
  return useQuery({
    queryKey: ["fincas", "desafio-suico", workspaceId],
    queryFn: () => api.get(`/api/v1/fincas/desafio-suico/streak/${workspaceId}`).then((r) => r.data),
    enabled: !!workspaceId,
  });
}

export function useLimpezaFinanceira(workspaceId?: string) {
  return useQuery({
    queryKey: ["fincas", "limpeza", workspaceId],
    queryFn: () => api.get(`/api/v1/fincas/limpeza/${workspaceId}`).then((r) => r.data),
    enabled: !!workspaceId,
  });
}
