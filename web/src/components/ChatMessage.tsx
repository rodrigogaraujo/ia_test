"use client";

interface Source {
  type: string;
  title: string;
  content_preview: string;
  url: string | null;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agentUsed?: string;
  sources?: Source[];
  isStreaming?: boolean;
}

const agentBadge: Record<string, { label: string; color: string }> = {
  faq: { label: "FAQ", color: "#22c55e" },
  search: { label: "Search", color: "#3b82f6" },
  both: { label: "FAQ + Search", color: "#a855f7" },
};

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 16,
      }}
    >
      <div
        style={{
          maxWidth: "80%",
          padding: "12px 16px",
          borderRadius: 12,
          backgroundColor: isUser ? "#1d4ed8" : "#1a1a1a",
          border: isUser ? "none" : "1px solid #2a2a2a",
        }}
      >
        {/* Message content */}
        <div style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
          {message.content}
          {message.isStreaming && (
            <span
              style={{
                display: "inline-block",
                width: 6,
                height: 14,
                backgroundColor: "#3b82f6",
                marginLeft: 2,
                animation: "blink 1s infinite",
              }}
            />
          )}
        </div>

        {/* Agent badge + sources */}
        {!isUser && message.agentUsed && (
          <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid #2a2a2a" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <span
                style={{
                  fontSize: 11,
                  padding: "2px 8px",
                  borderRadius: 4,
                  backgroundColor: agentBadge[message.agentUsed]?.color || "#555",
                  color: "#fff",
                  fontWeight: 600,
                }}
              >
                {agentBadge[message.agentUsed]?.label || message.agentUsed}
              </span>
            </div>

            {message.sources && message.sources.length > 0 && (
              <div style={{ fontSize: 12, color: "#888" }}>
                <span style={{ fontWeight: 500 }}>Fontes:</span>
                <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                  {message.sources.map((s, i) => (
                    <li key={i} style={{ marginBottom: 2 }}>
                      {s.url ? (
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: "#60a5fa", textDecoration: "none" }}
                        >
                          {s.title}
                        </a>
                      ) : (
                        <span>{s.title}</span>
                      )}
                      <span style={{ color: "#555", marginLeft: 4 }}>
                        [{s.type}]
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
