"use client";

import { Conversation, ConversationContent, ConversationScrollButton } from "@/components/ai-elements/conversation";
import { Message, MessageContent, MessageResponse } from "@/components/ai-elements/message";
import { PromptInput, PromptInputBody, PromptInputFooter, PromptInputSubmit, PromptInputTextarea } from "@/components/ai-elements/prompt-input";
import { ModeToggle } from "@/components/mode-toggle";
import { useAgentStream } from "@/hooks/use-agent-stream";
import { Message as MessageType, Product } from "@/types";
import { GlobeIcon } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ProductGrid } from "./product-grid";


const mockProducts: Product[] = [
  {
    name: "Smartphone Galaxy S23",
    brand: "Samsung",
    price: "R$ 4.599,00",
    availability: "Em estoque",
    average_rating: 4.7,
    total_reviews: 1289,
    images: [
      "https://example.com/images/galaxy-s23-front.jpg",
      "https://example.com/images/galaxy-s23-back.jpg"
    ],
    url: "https://example.com/produtos/samsung-galaxy-s23"
  },
  {
    name: "iPhone 15",
    brand: "Apple",
    price: "R$ 6.999,00",
    availability: "Pré-venda",
    average_rating: 4.8,
    total_reviews: 980,
    images: [
      "https://example.com/images/iphone-15.jpg"
    ],
    url: "https://example.com/produtos/iphone-15"
  },
  {
    name: "Notebook Inspiron 15",
    brand: "Dell",
    price: "R$ 3.899,00",
    availability: "Em estoque",
    average_rating: 4.5,
    total_reviews: 540,
    images: [
      "https://example.com/images/inspiron-15.jpg"
    ],
    url: "https://example.com/produtos/dell-inspiron-15"
  },
  {
    name: "Fone de Ouvido WH-1000XM5",
    brand: "Sony",
    price: "R$ 2.299,00",
    availability: "Poucas unidades",
    average_rating: 4.9,
    total_reviews: 2100,
    images: [
      "https://example.com/images/sony-wh1000xm5.jpg"
    ],
    url: "https://example.com/produtos/sony-wh-1000xm5"
  },
  {
    name: "Smart TV 55\" 4K UHD",
    brand: "LG",
    price: "R$ 2.799,00",
    availability: "Em estoque",
    average_rating: 4.6,
    total_reviews: 760,
    images: [
      "https://example.com/images/lg-tv-55.jpg"
    ],
    url: "https://example.com/produtos/lg-smart-tv-55-4k"
  }
];

export const ChatbotInterface = () => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [lastSearch, setLastSearch] = useState<Product[] | null>(mockProducts);
  const streamingTextRef = useRef("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { stream } = useAgentStream({
    onToken: (token) => {
      streamingTextRef.current += token;
      setStreamingText(streamingTextRef.current);
    },
    onFinalState: (state) => {
      if (state.last_search && Array.isArray(state.last_search)) {
        setLastSearch(state.last_search);
      }
    },
    onComplete: () => {
      if (streamingTextRef.current) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: streamingTextRef.current,
            timestamp: new Date(),
            products: lastSearch || undefined,
          },
        ]);
      }
      setStreamingText("");
      streamingTextRef.current = "";
      setIsStreaming(false);
      setLastSearch(null);
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

    await stream(
      [...messages, userMessage].map((m) => ({
        role: m.role,
        content: m.content,
      })),
      "br"
    );
  };

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-background via-background to-accent/5">
      <div className="flex flex-col h-full w-full">
        <header className="border-b border-border/40 bg-card/30 backdrop-blur-xl shrink-0">
          <div className="container max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-gradient-to-br from-primary to-primary/60">
                  <GlobeIcon className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="text-xl font-bold">Product Pulse</h1>
                </div>
              </div>
              <ModeToggle />
            </div>
          </div>
        </header>

        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 max-w-4xl mx-auto w-full flex flex-col min-h-0">
            <Conversation>
              <ConversationContent>
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

        <div className="shrink-0 border-t border-border/40 bg-card/30 backdrop-blur-xl">
          <div className="p-4 max-w-4xl mx-auto w-full">
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