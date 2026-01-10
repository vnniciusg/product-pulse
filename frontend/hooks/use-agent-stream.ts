"use client";

import { useCallback, useRef } from "react";

interface StreamEvent {
  type: "token" | "final_state" | "error" | "done";
  delta?: string;
  state?: any;
  error?: string;
}

interface UseAgentStreamOptions {
  onToken?: (token: string) => void;
  onFinalState?: (state: any) => void;
  onError?: (error: string) => void;
  onComplete?: () => void;
}

export const useAgentStream = (options: UseAgentStreamOptions) => {
  const streamResponse = useRef<string>("");
  const abortControllerRef = useRef<AbortController | null>(null);

  const stream = useCallback(
    async (messages: any[], region?: string) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        streamResponse.current = "";

        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages,
            region: region || "us",
            stream_mode: ["messages", "state"],
          }),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("No reader available");
        }

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            options.onComplete?.();
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);

              if (data === "[DONE]") {
                options.onComplete?.();
                continue;
              }

              try {
                const parsed: StreamEvent = JSON.parse(data);

                if (parsed.type === "token" && parsed.delta) {
                  streamResponse.current += parsed.delta;
                  options.onToken?.(parsed.delta);
                } else if (parsed.type === "final_state" && parsed.state) {
                  options.onFinalState?.(parsed.state);
                } else if (parsed.type === "error") {
                  options.onError?.(parsed.error || "Unknown error");
                }
              } catch (e) {}
            }
          }
        }
      } catch (error: any) {
        if (error.name !== "AbortError") {
          options.onError?.(error.message || "Stream error");
        }
      }
    },
    [options]
  );

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  return { stream, stop };
};
