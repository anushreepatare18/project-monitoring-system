"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, AlertCircle, FileText, Activity } from "lucide-react";

type Message = {
  id: number;
  sender: "bot" | "user";
  text: string;
};

export default function AdminAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, sender: "bot", text: "Hello! I am PRAGYA AI, your project monitoring assistant. How can I help you today? You can ask me to summarize your projects, check pending updates, or explain risk insights." }
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

    // Mock deterministic responses for Phase 6
    setTimeout(() => {
      let botResponse = "I'm sorry, I couldn't understand that. You can ask about 'pending updates', 'risk explanation', or 'project status'.";
      const q = userMsg.text.toLowerCase();

      if (q.includes("pending") || q.includes("updates")) {
        botResponse = "Based on your assigned projects, you have 3 projects with updates pending for this reporting period. Please navigate to the 'My Projects' tab to submit them.";
      } else if (q.includes("risk") || q.includes("explain")) {
        botResponse = "Risk insights indicate that Project PRJ-924FB0F4 has a High schedule risk due to a 12-month delay from the planned end date. This is a decision-support signal for review.";
      } else if (q.includes("status") || q.includes("progress")) {
        botResponse = "Your average physical progress across all assigned projects is approximately 35%. Financial expenditure is tracking closely with physical progress, with no major financial anomalies detected in the current portfolio.";
      }

      setMessages(prev => [...prev, { id: Date.now(), sender: "bot", text: botResponse }]);
      setLoading(false);
    }, 1500);
  };

  const suggestPrompt = (text: string) => {
    setInput(text);
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex justify-between items-center">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mr-3 shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white">PRAGYA AI Assistant</h2>
            <p className="text-xs text-slate-500 font-medium">Admin Intelligence Mode</p>
          </div>
        </div>
        <button 
          onClick={() => setMessages([messages[0]])}
          className="text-xs font-bold text-slate-500 hover:text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-lg"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6" ref={scrollRef}>
        {messages.map(m => (
          <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[80%] ${m.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.sender === 'user' ? 'bg-blue-600 text-white ml-3' : 'bg-emerald-100 text-emerald-600 mr-3'}`}>
                {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={`p-4 rounded-2xl text-sm ${m.sender === 'user' ? 'bg-blue-600 text-white rounded-tr-none shadow-sm' : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-none shadow-sm'}`}>
                {m.text}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="flex">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 mr-3">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-2xl text-sm bg-slate-50 border border-slate-200 text-slate-500 rounded-tl-none flex items-center space-x-2">
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Inputs */}
      <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-white">
        <div className="flex space-x-2 mb-3 overflow-x-auto pb-1">
          <button onClick={() => suggestPrompt("Which projects have pending updates?")} className="shrink-0 flex items-center text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-100 transition">
            <AlertCircle className="w-3 h-3 mr-1.5" /> Pending Updates
          </button>
          <button onClick={() => suggestPrompt("Explain the risk factors for my projects.")} className="shrink-0 flex items-center text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-100 transition">
            <Activity className="w-3 h-3 mr-1.5" /> Risk Factors
          </button>
          <button onClick={() => suggestPrompt("Summarize portfolio progress.")} className="shrink-0 flex items-center text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full hover:bg-slate-100 transition">
            <FileText className="w-3 h-3 mr-1.5" /> Progress Summary
          </button>
        </div>

        <div className="relative">
          <input 
            type="text" 
            placeholder="Ask PRAGYA AI a question..." 
            className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition text-sm"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={loading}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="text-center mt-2 text-[10px] text-slate-400 font-medium">
          AI assists. Humans decide. Responses are based on authorized portfolio data.
        </div>
      </div>
    </div>
  );
}
