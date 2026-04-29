import { useMutation, useQuery } from "@tanstack/react-query";

import { askAssistant, getAssistantHealth, transcribeAssistantAudio } from "./api";

export function useAssistantHealth() {
  return useQuery({
    queryKey: ["assistant", "health"],
    queryFn: getAssistantHealth,
    retry: false
  });
}

export function useAskAssistant() {
  return useMutation({
    mutationFn: askAssistant
  });
}

export function useTranscribeAssistantAudio() {
  return useMutation({
    mutationFn: transcribeAssistantAudio
  });
}
