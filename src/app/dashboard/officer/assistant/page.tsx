"use client";
import { Bot } from "lucide-react";

export default function RiskAssistantPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Risk Assistant</h1>
        <p className="text-sm font-medium text-slate-500">
          Chat with the PRAGYA AI assistant to analyze complex risk factors.
        </p>
      </div>

      <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 mt-12 max-w-4xl mx-auto text-center">
        <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-4 mx-auto">
          <Bot className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Assistant Ready</h2>
        <p className="text-slate-500 text-sm mb-6">Type a query in the chat widget below to start analyzing project risks.</p>
      </div>
    </div>
  );
}
