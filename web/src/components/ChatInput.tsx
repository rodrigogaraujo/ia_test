"use client";

import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!disabled) inputRef.current?.focus();
  }, [disabled]);

  function handleSubmit() {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div style={{ padding: "16px 24px", borderTop: "1px solid #222" }}>
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "flex-end",
          backgroundColor: "#111",
          borderRadius: 12,
          border: "1px solid #333",
          padding: "8px 12px",
        }}
      >
        <textarea
          ref={inputRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Pergunte sobre viagens..."
          disabled={disabled}
          rows={1}
          style={{
            flex: 1,
            backgroundColor: "transparent",
            border: "none",
            color: "#ededed",
            fontSize: 14,
            resize: "none",
            outline: "none",
            fontFamily: "inherit",
            lineHeight: 1.5,
            maxHeight: 120,
          }}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !text.trim()}
          style={{
            padding: "8px 16px",
            borderRadius: 8,
            border: "none",
            backgroundColor: disabled || !text.trim() ? "#333" : "#3b82f6",
            color: "#fff",
            fontSize: 14,
            cursor: disabled || !text.trim() ? "not-allowed" : "pointer",
            fontWeight: 500,
            transition: "background-color 0.2s",
          }}
        >
          Enviar
        </button>
      </div>
      <p style={{ fontSize: 11, color: "#555", textAlign: "center", marginTop: 8 }}>
        Blis Travel Agents - Assistente multi-agent com FAQ (RAG) + Search (Tavily)
      </p>
    </div>
  );
}
