"use client";

import { useState, useRef, useEffect } from "react";
import {
  MessageSquare, Send, X, AlertTriangle, Link as LinkIcon,
  Loader2, Trash2, ShieldCheck, Bot, Database, ChevronDown,
  ExternalLink, Info, Copy, Check
} from "lucide-react";
import Link from "next/link";

// ── Types ──────────────────────────────────────────────────────────────────────

interface Message {
  id:       string;
  role:     "user" | "assistant";
  content:  string;
  projects: string[];
  asOfDate?: string;
  queryRun?: string;
  isMock?:  boolean;
  ts:       string;
}

interface ChatbotProps {
  role?:      string;
  officerId?: string;
  scope?:     any;
}

// ── Suggested prompts ─────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  "Which projects in the Roads sector are high risk?",
  "Which sector has the most cost overruns right now?",
  "Show projects with milestone delays over 3 months",
  "Projects with anomaly flags in the Health sector",
];

const MOCK_INITIAL: Omit<Message, "id" | "ts"> = {
  role: "assistant",
  content: `Found **3** high-risk Roads projects as of 2026-09-29:

• **P-ROADS-0891** [Roads] — Risk: 91.7/100 (Critical) | Delay: 12.0 mo | Cost growth: 34.1%
• **P-ROADS-0457** [Roads] — Risk: 82.4/100 (Critical) | Delay: 7.0 mo | Cost growth: 18.5%
• **P-ROADS-0102** [Roads] — Risk: 44.6/100 (Medium) | Delay: 2.0 mo | Cost growth: 11.2%`,
  projects: ["P-ROADS-0891", "P-ROADS-0457", "P-ROADS-0102"],
  asOfDate: "2026-09-29",
  isMock:   true,
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function generateId() {
  return Math.random().toString(36).slice(2, 9);
}

function now() {
  return new Date().toLocaleTimeString("en-IN", {
    hour: "2-digit", minute: "2-digit", hour12: true,
  });
}

/** Render markdown-like bold (**text**) and bullets (•) as simple JSX */
function RenderContent({ text }: { text: string }) {
  const lines = text.split("\n");
  return (
    <div className="space-y-1">
      {lines.map((line, i) => {
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        return (
          <p key={i} className="text-sm text-slate-700 leading-relaxed">
            {parts.map((part, j) =>
              part.startsWith("**") && part.endsWith("**") ? (
                <strong key={j} className="font-semibold text-slate-900">
                  {part.slice(2, -2)}
                </strong>
              ) : (
                <span key={j}>{part}</span>
              )
            )}
          </p>
        );
      })}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function Chatbot({
  role = "officer",
  officerId = "anonymous",
  scope = {},
}: ChatbotProps) {
  const [isOpen, setIsOpen]     = useState(false);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [copied, setCopied]     = useState<string | null>(null);
  const [showAudit, setShowAudit] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    { ...MOCK_INITIAL, id: generateId(), ts: now() },
  ]);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLInputElement>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 100);
  }, [isOpen]);

  const clearChat = () => {
    setMessages([{
      id: generateId(), ts: now(),
      role: "assistant",
      content: `Hello. I am the PRAGYA AI Risk Assistant (${role.toUpperCase()} mode).\n\nI answer questions about project risk strictly from stored data — I never fabricate numbers or invent explanations. How can I help?`,
      projects: [],
    }]);
  };

  const copyText = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopied(msgId);
    setTimeout(() => setCopied(null), 1500);
  };

  const sendMessage = async (overrideText?: string) => {
    const textToSend = (overrideText || input).trim();
    if (!textToSend || loading) return;

    setInput("");
    const userMsg: Message = {
      id: generateId(), ts: now(),
      role: "user", content: textToSend, projects: [],
    };
    setMessages(prev => [...prev.filter(m => !m.isMock), userMsg]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chatbot/ask", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question:   textToSend,
          officer_id: officerId,
          role,
          scope: typeof scope === "string" ? scope : (scope?.ministry ?? "ALL"),
        }),
      });

      let data: any;
      if (res.ok) {
        data = await res.json();
      } else {
        data = {
          answer_text:         "⚠️ The PRAGYA API is unreachable. Ensure the backend is running on port 8000.",
          referenced_projects: [],
          as_of_date:          new Date().toISOString().slice(0, 10),
        };
      }

      const assistantMsg: Message = {
        id:       generateId(),
        ts:       now(),
        role:     "assistant",
        content:  data.answer_text ?? "No response received.",
        projects: data.referenced_projects ?? [],
        asOfDate: data.as_of_date,
        queryRun: data.query_run,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch {
      setMessages(prev => [...prev, {
        id: generateId(), ts: now(),
        role: "assistant",
        content: "⚠️ Error connecting to the PRAGYA API.",
        projects: [],
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* ── Floating toggle button ─────────────────────────────────────────── */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-emerald-600 text-white p-4 rounded-full shadow-xl
                     hover:bg-emerald-700 transition-all duration-200 hover:scale-105 z-40 flex
                     items-center gap-2 group"
          aria-label="Open PRAGYA AI Assistant"
        >
          <MessageSquare className="w-6 h-6" />
          <span className="text-sm font-semibold hidden group-hover:inline whitespace-nowrap
                           overflow-hidden max-w-0 group-hover:max-w-xs transition-all duration-300">
            PRAGYA AI
          </span>
        </button>
      )}

      {/* ── Chat window ───────────────────────────────────────────────────── */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[420px] h-[640px] rounded-2xl shadow-2xl
                        flex flex-col border border-slate-200 overflow-hidden z-50
                        bg-white">

          {/* Header */}
          <div className="bg-[#0f172a] text-white px-4 py-3 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-emerald-900/50 flex items-center
                              justify-center text-emerald-400 shrink-0">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="font-bold text-sm tracking-tight">PRAGYA Risk Assistant</div>
                <div className="text-[10px] text-emerald-400 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  Retrieval-grounded · Never fabricates · {role.toUpperCase()} mode
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={clearChat}
                className="p-1.5 hover:bg-slate-700 rounded-lg transition text-slate-400 hover:text-white"
                title="Clear conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-slate-700 rounded-lg transition text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-slate-50">
            {messages.map((m) => (
              <div key={m.id} className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}>

                {m.role === "user" ? (
                  <div className="bg-emerald-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm
                                  max-w-[85%] text-sm shadow-sm">
                    {m.content}
                  </div>
                ) : (
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm w-full
                                  shadow-sm overflow-hidden">
                    {/* Content */}
                    <div className="px-4 pt-4 pb-2">
                      <RenderContent text={m.content} />
                    </div>

                    {/* Referenced project links */}
                    {m.projects && m.projects.length > 0 && (
                      <div className="px-4 pb-3 flex flex-wrap gap-1.5">
                        {m.projects.map((pid: string) => (
                          <Link
                            key={pid}
                            href={`/dashboard/officer/projects/${pid}`}
                            className="inline-flex items-center gap-1 text-[10px] font-bold
                                       text-emerald-700 bg-emerald-50 border border-emerald-200
                                       px-2 py-1 rounded-full hover:bg-emerald-100 transition"
                          >
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                            {pid}
                            <ExternalLink className="w-2.5 h-2.5" />
                          </Link>
                        ))}
                      </div>
                    )}

                    {/* Disclaimer */}
                    {m.asOfDate && (
                      <div className="mx-4 mb-3 bg-amber-50 border border-amber-200 rounded-lg
                                      p-2 flex items-start gap-2">
                        <AlertTriangle className="w-3 h-3 text-amber-600 mt-0.5 shrink-0" />
                        <p className="text-[9px] font-medium text-amber-800 leading-relaxed">
                          Data as of <strong>{m.asOfDate}</strong>. Answers are for review
                          support only — not a final finding. Verify with the dashboard before acting.
                        </p>
                      </div>
                    )}

                    {/* Audit trail toggle */}
                    {m.queryRun && (
                      <div className="border-t border-slate-100 px-4 py-2">
                        <button
                          onClick={() => setShowAudit(showAudit === m.id ? null : m.id)}
                          className="flex items-center gap-1 text-[9px] font-bold text-slate-400
                                     hover:text-slate-600 transition uppercase tracking-wider"
                        >
                          <Database className="w-2.5 h-2.5" />
                          Audit trail
                          <ChevronDown className={`w-2.5 h-2.5 transition ${showAudit === m.id ? "rotate-180" : ""}`} />
                        </button>
                        {showAudit === m.id && (
                          <p className="mt-1 font-mono text-[9px] text-slate-500 bg-slate-50
                                        rounded p-1.5 break-all">
                            {m.queryRun}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Copy button */}
                    <div className="border-t border-slate-100 px-4 py-1.5 flex justify-end">
                      <button
                        onClick={() => copyText(m.content, m.id)}
                        className="flex items-center gap-1 text-[9px] text-slate-400 hover:text-slate-600 transition"
                      >
                        {copied === m.id
                          ? <><Check className="w-2.5 h-2.5 text-emerald-500" /> Copied</>
                          : <><Copy className="w-2.5 h-2.5" /> Copy</>
                        }
                      </button>
                    </div>
                  </div>
                )}

                <div className={`text-[9px] text-slate-400 mt-1 ${m.role === "user" ? "mr-1" : "ml-1"}`}>
                  {m.ts}
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="flex items-start">
                <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl
                                rounded-tl-sm shadow-sm flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-emerald-600 animate-spin" />
                  <span className="text-xs text-slate-500">Querying risk store…</span>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Suggested prompts */}
          <div className="border-t border-slate-100 bg-white px-3 pt-2 pb-1">
            <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-hide">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  disabled={loading}
                  className="whitespace-nowrap px-2.5 py-1 bg-slate-50 border border-slate-200
                             rounded-full text-[10px] font-medium text-slate-600 hover:bg-slate-100
                             transition shrink-0 disabled:opacity-40"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="px-3 pb-3 bg-white shrink-0">
            <div className="relative">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                disabled={loading}
                placeholder="Ask about risk, SHAP reasons, delays, anomalies…"
                className="w-full bg-slate-50 border border-slate-200 rounded-full pl-4 pr-12
                           py-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-400
                           disabled:opacity-60 transition"
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 bg-emerald-500 text-white
                           p-1.5 rounded-full hover:bg-emerald-600 disabled:opacity-40 transition"
                aria-label="Send message"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-center text-[8px] font-bold text-slate-400 mt-1.5
                          uppercase tracking-widest">
              Grounded in AI risk data · Always verify before acting
            </p>
          </div>

        </div>
      )}
    </>
  );
}
