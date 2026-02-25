import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blis Travel Agents",
  description: "Assistente multi-agent de viagens",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body
        style={{
          margin: 0,
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          backgroundColor: "#0a0a0a",
          color: "#ededed",
        }}
      >
        {children}
      </body>
    </html>
  );
}
