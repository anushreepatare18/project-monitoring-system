"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, AlertTriangle, ShieldCheck, TrendingUp } from "lucide-react";

type Message = {
  id: number;
  sender: "bot" | "user";
  text: string;
};

export default function OfficerAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, sender: "bot", text: "Hello! I am PRAGYA AI. I can assist you with anomaly review, alert summaries, and risk explanations. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMsg: Message = { id: Date.now(), sender: "user", text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // Mock deterministic responses
    setTimeout(() => {
      let botResponse = "I can help summarize alerts, explain risk scores, or review anomalies. Please ask about 'alerts', 'anomaly review', or 'explain risk'.";
      const q = userMsg.text.toLowerCase();

      if (q.includes("alerts") || q.includes("summarize")) {
        botResponse = "You currently have 5 active alerts in your queue. Two are marked as 'High Priority' due to sudden expenditure jumps. I recommend reviewing PRJ-924FB0F4 first.";
      } else if (q.includes("explain") || q.includes("risk")) {
        botResponse = "For PRJ-924FB0F4, the model predicts 'High' schedule risk. The top contributing features are: 1) Historical delay > 6 months, 2) Financial progress lagging physical progress by 15%, 3) Sector average delays. Note: AI assists, human verification is required.";
      } else if (q.includes("anomaly") || q.includes("review")) {
        botResponse = "I detected an anomaly in PRJ-924FB0F4: The expenditure increased by 40% in one period, while physical progress only increased by 2%. This rule-based flag should be verified.";
      }

      setMessages(prev => [...prev, { id: Date.now(), sender: "bot", text: botResponse }]);
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 flex justify-between items-center">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mr-3 shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-slate-900">PRAGYA AI Assistant</h2>
            <p className="text-xs text-slate-500 font-medium">Monitoring Officer Mode</p>
          </div>
        </div>
        <button onClick={() => setMessages([messages[0]])} className="text-xs font-bold text-slate-500 hover:text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-lg">Clear Chat</button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6" ref={scrollRef}>
        {messages.map(m => (
          <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[80%] ${m.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.sender === 'user' ? 'bg-indigo-600 text-white ml-3' : 'bg-indigo-100 text-indigo-600 mr-3'}`}>
                {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-none'}`}>
                {m.text}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="flex">
              <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center mr-3"><Bot className="w-4 h-4" /></div>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex space-x-2 rounded-tl-none">
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-100 bg-white">
        <div className="flex space-x-2 mb-3 overflow-x-auto pb-1">
          <button onClick={() => setInput("Summarize my pending alerts")} className="shrink-0 flex items-center text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-100 transition"><AlertTriangle className="w-3 h-3 mr-1.5" /> Summarize Alerts</button>
          <button onClick={() => setInput("Explain risk factors for PRJ-924FB0F4")} className="shrink-0 flex items-center text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-100 transition"><ShieldCheck className="w-3 h-3 mr-1.5" /> Explain Risk</button>
          <button onClick={() => setInput("Show anomalies in recent updates")} className="shrink-0 flex items-center text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-100 transition"><TrendingUp className="w-3 h-3 mr-1.5" /> Anomaly Review</button>
        </div>
        <div className="relative">
          <input type="text" placeholder="Ask PRAGYA AI..." className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white text-sm" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} disabled={loading} />
          <button onClick={handleSend} disabled={!input.trim() || loading} className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"><Send className="w-4 h-4" /></button>
        </div>
      </div>
    </div>
  );
}
