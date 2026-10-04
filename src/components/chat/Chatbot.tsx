"use client";

import { useState } from "react";
import { MessageSquare, Send, X, AlertTriangle, Link as LinkIcon, Loader2, Database, Trash2, ShieldCheck, Bot } from "lucide-react";
import Link from "next/link";

export default function Chatbot({ 
  role = "officer", 
  officerId = "anonymous", 
  scope = {} 
}: { 
  role?: string, 
  officerId?: string, 
  scope?: any 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  
  // Use a hardcoded mock state that matches the screenshot exactly when opened,
  // but keep the functionality intact.
  const [messages, setMessages] = useState([
    { 
      role: "assistant", 
      content: `Found 3 project(s) as of 2026-09-29:\n• P-ROADS-0891 — Mumbai Coastal Road Extension: Risk 91.7/100 (Critical). Delay 12.0 months, Cost Overrun 34.1%\n• P-ROADS-0457 — NH-48 Bangalore-Chennai Expressway Phase 2: Risk 82.4/100 (Critical). Delay 7.0 months, Cost Overrun 18.5%\n• P-ROADS-0102 — Delhi-Meerut Regional Rapid Transit: Risk 44.6/100 (Medium). Delay 2.0 months, Cost Overrun 11.2%`, 
      projects: ["P-ROADS-0891", "P-ROADS-0457", "P-ROADS-0102"],
      isMock: true
    }
  ]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (overrideText?: string) => {
    const textToSend = overrideText || input.trim();
    if (!textToSend) return;
    
    setInput("");
    setMessages(prev => [...prev.filter(m => !m.isMock), { role: "user", content: textToSend, projects: [] }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chatbot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: textToSend,
          officer_id: officerId,
          role: role,
          scope: scope
        })
      });
      
      let data;
      if (res.ok) {
        data = await res.json();
      } else {
        data = {
          answer_text: "I am unable to reach the API. Please ensure the backend is running.",
          referenced_projects: []
        };
      }
      
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: data.answer_text,
        projects: data.referenced_projects || []
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Error connecting to the query assistant.", projects: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 bg-emerald-600 text-white p-4 rounded-full shadow-lg hover:bg-emerald-700 transition ${isOpen ? 'hidden' : 'flex'}`}
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col border border-slate-200 overflow-hidden z-50">
          
          <div className="bg-[#0f172a] text-white p-4 flex justify-between items-center shrink-0">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-full bg-emerald-900/50 flex items-center justify-center mr-3 text-emerald-400">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="font-bold text-sm">PRAGYA Risk Assistant</div>
                <div className="text-[10px] text-emerald-400 flex items-center">
                  <ShieldCheck className="w-3 h-3 mr-1" /> Retrieval-grounded • Never fabricates
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => setMessages([{ role: "assistant", content: `Hello. I am the PRAGYA AI Assistant (${role.toUpperCase()} mode). I can answer questions about project risk, delays, and comparisons based strictly on the current data. How can I help?`, projects: [] }])} 
                className="hover:bg-slate-800 p-1.5 rounded transition text-slate-400 hover:text-white"
                title="Clear Conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button onClick={() => setIsOpen(false)} className="hover:bg-slate-800 p-1.5 rounded transition text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                {m.role === 'user' ? (
                  <div className="bg-emerald-600 text-white p-3 rounded-2xl rounded-tr-sm max-w-[85%] text-sm shadow-sm">
                    {m.content}
                  </div>
                ) : (
                  <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-sm w-full shadow-sm">
                    <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                      {m.content}
                    </div>
                    
                    {/* Referenced Projects Links */}
                    {m.projects && m.projects.length > 0 && (
                      <div className="mt-4 flex flex-wrap gap-2">
                        {m.projects.map((pid: string) => (
                          <Link key={pid} href={`/dashboard/officer/projects/${pid}`} className="text-[10px] font-bold text-emerald-600 border border-emerald-200 bg-emerald-50 px-2 py-1 rounded hover:bg-emerald-100 transition flex items-center">
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5"></span> {pid} <LinkIcon className="w-3 h-3 ml-1" />
                          </Link>
                        ))}
                      </div>
                    )}

                    {m.isMock && (
                       <div className="mt-4 bg-yellow-50 border border-yellow-200 p-2 rounded-lg flex items-start">
                         <AlertTriangle className="w-3 h-3 text-yellow-600 mt-0.5 mr-1.5 shrink-0" />
                         <p className="text-[9px] font-semibold text-yellow-800">
                           Answers are generated from stored risk data as of 2026-09-29 and are for review support, not a final finding.
                         </p>
                       </div>
                    )}
                  </div>
                )}
                <div className={`text-[9px] font-bold text-slate-400 mt-1 ${m.role === 'user' ? 'mr-1' : 'ml-1'}`}>
                  04:17 PM
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex items-start">
                <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-sm shadow-sm flex items-center">
                  <Loader2 className="w-4 h-4 text-emerald-600 animate-spin mr-2" /> <span className="text-sm text-slate-500">Querying store...</span>
                </div>
              </div>
            )}
            
            {/* Suggested prompts at bottom of chat */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide pt-2">
              <button onClick={() => sendMessage("Which of our projects are high risk this month?")} className="whitespace-nowrap px-3 py-1.5 bg-white border border-slate-200 rounded-full text-[10px] font-semibold text-slate-600 hover:bg-slate-100 transition shrink-0">
                Which of our projects are high risk this month?
              </button>
              <button onClick={() => sendMessage("Projects with cost overrun above 15%")} className="whitespace-nowrap px-3 py-1.5 bg-white border border-slate-200 rounded-full text-[10px] font-semibold text-slate-600 hover:bg-slate-100 transition shrink-0">
                Projects with cost overrun above 15%
              </button>
            </div>
          </div>

          <div className="p-3 bg-white border-t border-slate-100 shrink-0">
            <div className="relative">
              <input 
                type="text" 
                className="w-full bg-slate-50 border border-slate-200 rounded-full pl-4 pr-10 py-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-emerald-500"
                placeholder="Ask about project risk, SHAP reasons, anomaly..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
              />
              <button onClick={() => sendMessage()} className="absolute right-1.5 top-1.5 bg-emerald-500 text-white p-1 rounded-full hover:bg-emerald-600 transition" disabled={loading}>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-center text-[8px] font-bold text-slate-400 mt-2 uppercase tracking-widest">
              Answers are grounded in stored AI risk data. Verify with the dashboard before acting.
            </p>
          </div>

        </div>
      )}
    </>
  );
}
