import { useMutation } from "@tanstack/react-query";
import api from "@/lib/api";

interface ChatResponse {
  conversation_id: string;
  message: string;
}

export function useChat() {
  return useMutation({
    mutationFn: async (data: { message: string; conversation_id?: string }) => {
      const res = await api.post("/api/v1/ai/chat", data);
      return res.data as ChatResponse;
    },
  });
}
