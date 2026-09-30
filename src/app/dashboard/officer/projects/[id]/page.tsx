"use client";

import { useState, useEffect, useRef } from "react";
import { 
  BarChart2, 
  AlertTriangle, 
  Search, 
  CheckCircle2,
  Bot,
  Send,
  ChevronDown,
  MessageSquare,
  ArrowLeft
} from "lucide-react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";

export default function ProjectDetailExplanation() {
  const { id } = useParams();
  
  const [projectData, setProjectData] = useState<any>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { role: "assistant", text: "Hello! I'm the PRAGYA Risk Intelligence Assistant. I answer questions about project risk scores, SHAP explanations, anomaly flags, milestone delays, and cost overruns — grounded entirely in stored AI outputs. I never invent data." }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch project details and explanation
    const fetchData = async () => {
      try {
        const [projRes, expRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/projects/${id}`),
          fetch(`http://127.0.0.1:8000/api/projects/${id}/explanation`)
        ]);

        if (projRes.ok) setProjectData(await projRes.json());
        if (expRes.ok) setExplanation(await expRes.json());
      } catch (err) {
        console.error("Failed to fetch project data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleSendMessage = async (queryOverride?: string) => {
    const q = queryOverride || chatInput;
    if (!q.trim()) return;

    const newHistory = [...chatHistory, { role: "user", text: q }];
    setChatHistory(newHistory);
    setChatInput("");
    setChatLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/dataset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, history: chatHistory })
      });
      if (res.ok) {
        const data = await res.json();
        setChatHistory([...newHistory, { role: "assistant", text: data.reply }]);
      } else {
        setChatHistory([...newHistory, { role: "assistant", text: "I'm having trouble connecting to my knowledge base right now." }]);
      }
    } catch (err) {
      setChatHistory([...newHistory, { role: "assistant", text: "Network error occurred." }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Analyzing Model Weights...</p>
        </div>
      </div>
    );
  }

  const pData = projectData || { name: "Ghatampur Thermal Power Plant", risk_level: "CRITICAL", risk_score: 85, physical_progress_pct: 55.6 };
  const riskColor = pData.risk_level === 'Critical' ? 'text-red-500 border-red-200 bg-red-100' : pData.risk_level === 'High' ? 'text-orange-500 border-orange-200 bg-orange-100' : 'text-emerald-500 border-emerald-200 bg-emerald-100';

  return (
    <div className="p-8 max-w-7xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      
      <div className="mb-4">
        <Link href="/dashboard/officer/projects" className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-emerald-600 transition-colors uppercase tracking-widest">
          <ArrowLeft className="w-4 h-4" /> Back to Project Register
        </Link>
      </div>

      {/* Top Header Row */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-slate-200 gap-6"
      >
        <div>
          <h1 className="text-2xl font-black text-blue-700 tracking-tight">{id as string}</h1>
          <p className="text-xs font-medium text-slate-400 mt-1">{pData.name}</p>
        </div>
        
        <div className="flex items-center gap-8 md:gap-12 flex-wrap">
          <span className={`inline-block px-3 py-1 text-[10px] font-black rounded-full uppercase tracking-widest border ${riskColor}`}>
            {pData.risk_level}
          </span>
          <div className="flex items-center gap-2">
            <span className="text-xl font-black text-slate-900">{Math.round(pData.risk_score)}</span>
            <span className="text-xs font-bold text-slate-400 mt-1">/100</span>
          </div>
          <div className="flex flex-col gap-1 w-32">
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }} 
                animate={{ width: `${pData.physical_progress_pct}%` }} 
                transition={{ duration: 1, delay: 0.2 }}
                className="h-full bg-blue-500 rounded-full" 
              />
            </div>
            <span className="text-[9px] font-bold text-slate-500">{pData.physical_progress_pct}%</span>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        
        {/* Left Column */}
        <div className="space-y-8">
          
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
            <div className="flex items-center gap-2 mb-4">
              <BarChart2 className="w-5 h-5 text-blue-500" />
              <h2 className="text-sm font-black text-slate-900 tracking-tight">SHAP Explanation Panel</h2>
            </div>
            
            {!explanation || !explanation.shap_explanations || explanation.shap_explanations.length === 0 ? (
              <div className="bg-red-50/50 border border-red-200 p-5 rounded-2xl">
                <div className="flex items-center gap-2 text-red-500 mb-2">
                  <AlertTriangle className="w-4 h-4" />
                  <h3 className="text-xs font-bold">AI Explanation Unavailable</h3>
                </div>
                <p className="text-[10px] text-red-400 mt-1 font-medium">No valid SHAP values returned from the backend.</p>
              </div>
            ) : (
              <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
                <p className="text-[11px] text-slate-500 mb-4 leading-relaxed">
                  These factors had the highest impact on the model's prediction for this project's risk score. Positive impact increases risk; negative impact decreases it.
                </p>
                <div className="space-y-4">
                  {explanation.shap_explanations.slice(0, 5).map((exp: any, i: number) => (
                    <div key={i} className="flex flex-col gap-1">
                      <div className="flex justify-between text-xs font-bold">
                        <span className="text-slate-700 capitalize">{exp.feature.replace(/_/g, ' ')}</span>
                        <span className={exp.impact > 0 ? "text-red-500" : "text-emerald-500"}>
                          {exp.impact > 0 ? "+" : ""}{exp.impact.toFixed(2)}
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
                        {exp.impact > 0 ? (
                          <div className="w-1/2 flex justify-end"><div className="bg-transparent h-full w-full"></div></div>
                        ) : null}
                        {exp.impact > 0 ? (
                          <div className="w-1/2 bg-red-400 h-full" style={{ width: `${Math.min(100, Math.abs(exp.impact) * 20)}%` }}></div>
                        ) : (
                          <div className="w-1/2 bg-emerald-400 h-full ml-auto" style={{ width: `${Math.min(100, Math.abs(exp.impact) * 20)}%` }}></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>

          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
            <h2 className="text-sm font-black text-slate-900 tracking-tight mb-4">Sub-Risk Categories</h2>
            <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm divide-y divide-slate-50">
              <div className="flex justify-between items-center py-3">
                <span className="text-xs font-bold text-slate-600">Cost Overrun Risk</span>
                <span className="text-xs font-black text-red-500">High</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-xs font-bold text-slate-600">Schedule Delay Risk</span>
                <span className="text-xs font-black text-orange-500">Medium</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-xs font-bold text-slate-600">Implementation Risk</span>
                <span className="text-xs font-black text-emerald-500">Low</span>
              </div>
            </div>
          </motion.div>
          
        </div>

        {/* Right Column */}
        <div className="space-y-8">
          
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
            <div className="flex items-center gap-2 mb-4">
              <Search className="w-5 h-5 text-blue-500" />
              <h2 className="text-[11px] font-black text-slate-900 tracking-widest uppercase">Suggested Officer Actions</h2>
            </div>
            <div className="space-y-3">
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start group hover:bg-emerald-50 transition-colors cursor-pointer">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                <p className="text-xs text-slate-600 font-medium leading-relaxed">Verify the latest progress update against actual field reports.</p>
              </div>
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start group hover:bg-emerald-50 transition-colors cursor-pointer">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                <p className="text-xs text-slate-600 font-medium leading-relaxed">Request clarification from <span className="italic text-slate-500 font-bold">{pData.implementing_agency || 'Agency'}</span> regarding the expenditure discrepancy.</p>
              </div>
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start group hover:bg-emerald-50 transition-colors cursor-pointer">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                <p className="text-xs text-slate-600 font-medium leading-relaxed">Schedule a follow-up review for the next reporting period.</p>
              </div>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="w-5 h-5 text-blue-500" />
              <h2 className="text-[11px] font-black text-slate-900 tracking-widest uppercase">Ask AI About This Project</h2>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm flex flex-col h-[400px]">
              
              {/* Chat Area */}
              <div className="flex-1 overflow-y-auto p-5 space-y-6">
                {chatHistory.map((msg, idx) => (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    key={idx} 
                    className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    {msg.role === 'assistant' ? (
                      <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                        <Bot className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0 text-[10px] font-bold">
                        YOU
                      </div>
                    )}
                    <div className={`p-4 text-xs shadow-sm leading-relaxed max-w-[85%] ${
                      msg.role === 'assistant' 
                        ? 'bg-white border border-slate-200 rounded-2xl rounded-tl-sm text-slate-600' 
                        : 'bg-blue-600 text-white rounded-2xl rounded-tr-sm'
                    }`}>
                      {msg.role === 'assistant' && idx === 0 && (
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-[9px] font-black text-emerald-600 tracking-widest uppercase">✦ PRAGYA AI</span>
                        </div>
                      )}
                      <div className="whitespace-pre-wrap">{msg.text}</div>
                    </div>
                  </motion.div>
                ))}
                
                {chatLoading && (
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-600 shadow-sm flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Inputs */}
              <div className="p-4 border-t border-slate-100 bg-slate-50/50">
                <div className="flex gap-2 mb-4 overflow-x-auto pb-2 scrollbar-hide">
                  {[`Why is ${pData.id} flagged?`, `Compare risk factors for ${pData.id}`, `Summarize issues`].map((q) => (
                    <button 
                      key={q}
                      onClick={() => handleSendMessage(q)}
                      className="shrink-0 bg-white border border-slate-200 px-3 py-1.5 rounded-full text-[10px] font-bold text-slate-600 hover:bg-slate-100 transition-colors whitespace-nowrap"
                    >
                      {q}
                    </button>
                  ))}
                </div>
                
                <form 
                  onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                  className="relative"
                >
                  <input 
                    type="text" 
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    disabled={chatLoading}
                    placeholder="Ask about project risk, SHAP reasons, anomaly flags..." 
                    className="w-full pl-4 pr-12 py-3 bg-white border border-slate-200 rounded-full text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
                  />
                  <button 
                    type="submit"
                    disabled={!chatInput.trim() || chatLoading}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-emerald-500 text-white rounded-full flex items-center justify-center hover:bg-emerald-600 transition-colors disabled:opacity-50 disabled:hover:bg-emerald-500"
                  >
                    <Send className="w-3 h-3 ml-0.5" />
                  </button>
                </form>
                
                <p className="text-center text-[9px] text-slate-400 mt-3 italic">
                  Answers are grounded in stored AI risk data. Verify with the dashboard before acting.
                </p>
              </div>
            </div>
          </motion.div>
          
        </div>
      </div>
      
    </div>
  );
}
