"use client";

import { Conversation, ConversationContent, ConversationEmptyState, ConversationScrollButton } from "@/components/ai-elements/conversation";
import { Message, MessageContent, MessageResponse } from "@/components/ai-elements/message";
import { PromptInput, PromptInputBody, PromptInputFooter, PromptInputSubmit, PromptInputTextarea } from "@/components/ai-elements/prompt-input";
import { Shimmer } from "@/components/ai-elements/shimmer";
import { ModeToggle } from "@/components/mode-toggle";
import { useAgentStream } from "@/hooks/use-agent-stream";
import { Message as MessageType, Product } from "@/types";
import { MessageSquare } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ProductGrid } from "./product-grid";


export const ChatbotInterface = () => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [lastSearch, setLastSearch] = useState<Product[] | null>(null);
  const streamingTextRef = useRef("");
  const lastSearchRef = useRef<Product[] | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { stream } = useAgentStream({
    onToken: (token) => {
      streamingTextRef.current += token;
      setStreamingText(streamingTextRef.current);
    },
    onFinalState: (state) => {
      if (state.last_search && Array.isArray(state.last_search)) {
        lastSearchRef.current = state.last_search;
        setLastSearch(state.last_search);
      }
    },
    onComplete: () => {
      const finalContent = streamingTextRef.current;
      const finalProducts = lastSearchRef.current;

      if (finalContent) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: finalContent,
            timestamp: new Date(),
            products: finalProducts || undefined,
          },
        ]);
      }

      setStreamingText("");
      streamingTextRef.current = "";
      setIsStreaming(false);
      setLastSearch(null);
      lastSearchRef.current = null;
    },
    onError: () => {
      setIsStreaming(false);
    }
  });

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages, streamingText, lastSearch]);

  useEffect(() => {
    if (streamingTextRef.current && isStreaming) {
      const scrollButton = document.querySelector('[data-conversation-scroll-button]') as HTMLElement;
      if (scrollButton) scrollButton.click();
    }
  }, [streamingText, isStreaming]);


  const handleSubmit = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: MessageType = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);
    streamingTextRef.current = "";
    lastSearchRef.current = null;

    await stream(
      [...messages, userMessage].map((m) => ({
        role: m.role,
        content: m.content,
      })),
      "br"
    );
  };

  return (
    <div className="flex h-screen w-full bg-background text-foreground">
      <div className="flex flex-col h-full w-full">
        <header className="shrink-0 flex justify-end mx-8 my-4">
          <ModeToggle />
        </header>

        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 max-w-6xl mx-auto w-full flex flex-col min-h-0">
            <Conversation>
              <ConversationContent>
                {messages.length === 0 && (
                  <ConversationEmptyState
                    icon={<MessageSquare className="size-10" />}
                    title="Product Pulse AI"
                    description="Search for similar products, compare prices, and get personalized recommendations."
                  />
                )}
                {messages.map((message) => (
                  <Message from={message.role} key={message.timestamp.toISOString()}>
                    <MessageContent>
                      <MessageResponse>
                        {message.content}
                      </MessageResponse>
                      {message.products && message.products.length > 0 && (
                        <div className="mt-4">
                          <ProductGrid products={message.products} />
                        </div>
                      )}
                    </MessageContent>
                  </Message>
                ))}
                {isStreaming && !streamingText && (
                  <Message from="assistant">
                    <MessageContent>
                      <Shimmer>The agent is thinking...</Shimmer>
                    </MessageContent>
                  </Message>
                )}
                {isStreaming && streamingText && (
                  <Message from="assistant">
                    <MessageContent>
                      <MessageResponse>
                        {streamingText}
                      </MessageResponse>
                    </MessageContent>
                  </Message>
                )}
              </ConversationContent>
              <ConversationScrollButton />
            </Conversation>
          </div>
        </div>

        <div className="shrink-0">
          <div className="p-8 max-w-5xl mx-auto w-full">
            <PromptInput onSubmit={handleSubmit} className="w-full">
              <PromptInputBody>
                <PromptInputTextarea
                  onChange={(e) => setInput(e.target.value)}
                  value={input}
                  ref={textareaRef}
                  placeholder="Ask something..."
                />
              </PromptInputBody>
              <PromptInputFooter>
                <PromptInputSubmit disabled={!input || isStreaming} status={isStreaming ? 'streaming' : 'ready'} />
              </PromptInputFooter>
            </PromptInput>
          </div>
        </div>
      </div>
    </div>
  );
};