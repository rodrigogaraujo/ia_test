"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3456";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agentUsed?: string;
  sources?: Array<{
    type: string;
    title: string;
    content_preview: string;
    url: string | null;
  }>;
  isStreaming?: boolean;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [useStreaming, setUseStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    if (useStreaming) {
      await sendStreaming(text);
    } else {
      await sendRegular(text);
    }

    setIsLoading(false);
  }

  async function sendRegular(text: string) {
    try {
      const res = await fetch(`${API_URL}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const assistantMsg: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.response,
        agentUsed: data.agent_used,
        sources: data.sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      const errMsg: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `Erro: ${error instanceof Error ? error.message : "Falha na comunicação com a API"}`,
      };
      setMessages((prev) => [...prev, errMsg]);
    }
  }

  async function sendStreaming(text: string) {
    const assistantId = `assistant-${Date.now()}`;
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const url = `${API_URL}/api/v1/chat/stream?session_id=${encodeURIComponent(sessionId)}&message=${encodeURIComponent(text)}`;
      const eventSource = new EventSource(url);

      eventSource.addEventListener("token", (e) => {
        const data = JSON.parse(e.data);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: m.content + data.token }
              : m
          )
        );
      });

      eventSource.addEventListener("done", (e) => {
        const data = JSON.parse(e.data);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  isStreaming: false,
                  agentUsed: data.agent_used,
                  sources: data.sources,
                }
              : m
          )
        );
        eventSource.close();
      });

      eventSource.addEventListener("error", (e) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  isStreaming: false,
                  content: m.content || "Erro durante streaming",
                }
              : m
          )
        );
        eventSource.close();
      });
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, isStreaming: false, content: "Erro ao conectar ao streaming" }
            : m
        )
      );
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <header style={{ padding: "16px 24px", borderBottom: "1px solid #222", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>Blis Travel Agents</h1>
          <span style={{ fontSize: 12, color: "#888" }}>Assistente multi-agent de viagens</span>
        </div>
        <label style={{ fontSize: 13, color: "#888", display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={useStreaming}
            onChange={(e) => setUseStreaming(e.target.checked)}
            style={{ accentColor: "#3b82f6" }}
          />
          SSE Streaming
        </label>
      </header>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "24px" }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", marginTop: 80, color: "#555" }}>
            <p style={{ fontSize: 16, marginBottom: 8 }}>Pergunte sobre viagens</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", maxWidth: 500, margin: "0 auto" }}>
              {[
                "Qual o limite de bagagem de mão na LATAM?",
                "Quanto está a passagem SP-Lisboa em março?",
                "Quero levar meu cachorro para Portugal, o que preciso?",
                "Como funciona o check-in online?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  style={{
                    padding: "8px 14px",
                    borderRadius: 8,
                    border: "1px solid #333",
                    background: "#111",
                    color: "#ccc",
                    fontSize: 13,
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {isLoading && !messages.some((m) => m.isStreaming) && (
          <div style={{ padding: "12px 16px", color: "#888", fontSize: 14 }}>
            Pensando...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
