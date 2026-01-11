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
  const optionsRef = useRef(options);

  optionsRef.current = options;

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

        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");

          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.trim().startsWith("data: ")) {
              const data = line.trim().slice(6);

              if (data === "[DONE]") {
                continue;
              }

              try {
                const parsed: StreamEvent = JSON.parse(data);

                if (parsed.type === "token" && parsed.delta) {
                  streamResponse.current += parsed.delta;
                  optionsRef.current.onToken?.(parsed.delta);
                } else if (parsed.type === "final_state" && parsed.state) {
                  optionsRef.current.onFinalState?.(parsed.state);
                } else if (parsed.type === "error") {
                  optionsRef.current.onError?.(parsed.error || "Unknown error");
                }
              } catch (e) {
                console.error("Error parsing stream event:", e, data);
              }
            }
          }
        }

        if (buffer.trim().startsWith("data: ")) {
          const data = buffer.trim().slice(6);
          if (data !== "[DONE]") {
            try {
              const parsed: StreamEvent = JSON.parse(data);
              if (parsed.type === "token" && parsed.delta) {
                streamResponse.current += parsed.delta;
                optionsRef.current.onToken?.(parsed.delta);
              } else if (parsed.type === "final_state" && parsed.state) {
                optionsRef.current.onFinalState?.(parsed.state);
              }
            } catch (e) { }
          }
        }

        optionsRef.current.onComplete?.();
      } catch (error: any) {
        if (error.name !== "AbortError") {
          optionsRef.current.onError?.(error.message || "Stream error");
        }
      } finally {
        if (abortControllerRef.current === controller) {
          abortControllerRef.current = null;
        }
      }
    },
    []
  );

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  return { stream, stop };
};
