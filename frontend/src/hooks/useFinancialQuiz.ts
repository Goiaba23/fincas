import { useQuery, useMutation } from "@tanstack/react-query";
import api from "@/lib/api";

export interface QuestionOption {
  value: string | number;
  label: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  type: string;
  options: QuestionOption[] | null;
  placeholder: string | null;
}

export interface MethodScore {
  key: string;
  name: string;
  origin: string;
  icon: string;
  tagline: string;
  description: string;
  benefits: string[];
  best_for: string;
  score: number;
  max_score: number;
  percentage: number;
}

export interface QuizRecommendation {
  top_recommendation: MethodScore | null;
  all_scores: MethodScore[];
  alternatives: MethodScore[];
  dream_advice: string | null;
}

export function useQuizQuestions() {
  return useQuery({
    queryKey: ["quiz-questions"],
    queryFn: async () => {
      const res = await api.get("/api/v1/quiz/questions");
      return res.data as QuizQuestion[];
    },
  });
}

export function useQuizRecommendation() {
  return useMutation({
    mutationFn: async (answers: Record<string, string | number>) => {
      const res = await api.post("/api/v1/quiz/recommend", { answers });
      return res.data as QuizRecommendation;
    },
  });
}

export function useSaveRecommendation() {
  return useMutation({
    mutationFn: async (params: { method_key: string; method_name: string }) => {
      const res = await api.post("/api/v1/quiz/save-recommendation", params);
      return res.data;
    },
  });
}
