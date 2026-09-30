import "./globals.css";
import type { Metadata } from "next";
import ChatWidget from "@/components/chat/ChatWidget";

export const metadata: Metadata = {
  title: "PRAGYA AI - Infrastructure Monitoring",
  description: "AI-driven project monitoring and risk assessment for infrastructure projects.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        <ChatWidget />
      </body>
    </html>
  );
}
