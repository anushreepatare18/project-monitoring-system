"use client";

import { 
  BarChart2, 
  AlertTriangle, 
  Search, 
  CheckCircle2,
  Bot,
  Send,
  ChevronDown,
  MessageSquare
} from "lucide-react";
import { useParams } from "next/navigation";

export default function ProjectDetailExplanation() {
  const { id } = useParams();

  return (
    <div className="p-8 max-w-7xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      
      {/* Top Header Row */}
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-blue-700 tracking-tight">{id as str || "PRJ-400259"}</h1>
          <p className="text-xs font-medium text-slate-400 mt-1">Ghatampur Thermal Power Plant 3 X 660 MW</p>
        </div>
        
        <div className="flex items-center gap-12">
          <span className="inline-block px-3 py-1 bg-red-100 text-[10px] font-black text-red-600 rounded-full uppercase tracking-widest border border-red-200">
            CRITICAL
          </span>
          <div className="flex items-center gap-2">
            <span className="text-xl font-black text-slate-900">85</span>
            <span className="text-xs font-bold text-slate-400 mt-1">/100</span>
          </div>
          <div className="flex flex-col gap-1 w-32">
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full w-[55.6%]"></div>
            </div>
            <span className="text-[9px] font-bold text-slate-500">55.60%</span>
          </div>
          <button className="flex items-center gap-2 bg-blue-50 text-blue-600 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-blue-100 transition-colors">
            EXPLAIN <ChevronDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        
        {/* Left Column */}
        <div className="space-y-8">
          
          <div>
            <div className="flex items-center gap-2 mb-4">
              <BarChart2 className="w-5 h-5 text-blue-500" />
              <h2 className="text-sm font-black text-slate-900 tracking-tight">Explanation Panel</h2>
            </div>
            
            <div className="bg-red-50/50 border border-red-200 p-5 rounded-2xl">
              <div className="flex items-center gap-2 text-red-500 mb-2">
                <AlertTriangle className="w-4 h-4" />
                <h3 className="text-xs font-bold">AI Explanation Unavailable</h3>
              </div>
              <p className="text-[10px] text-red-400 mt-1 font-medium">Failed to fetch</p>
              <p className="text-[10px] text-red-400/80 mt-1">Make sure the Python backend is running on port 8000.</p>
            </div>
          </div>

          <div>
            <h2 className="text-sm font-black text-slate-900 tracking-tight mb-4">Sub-Risk Categories</h2>
            <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm divide-y divide-slate-50">
              <div className="flex justify-between items-center py-3">
                <span className="text-xs font-bold text-slate-600">Cost Risk</span>
                <span className="text-xs font-black text-red-500">High</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-xs font-bold text-slate-600">Schedule Risk</span>
                <span className="text-xs font-black text-red-500">Medium</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-xs font-bold text-slate-600">Implementation Risk</span>
                <span className="text-xs font-black text-red-500">Medium</span>
              </div>
            </div>
          </div>
          
        </div>

        {/* Right Column */}
        <div className="space-y-8">
          
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Search className="w-5 h-5 text-blue-500" />
              <h2 className="text-[11px] font-black text-slate-900 tracking-widest uppercase">Suggested Officer Actions</h2>
            </div>
            <div className="space-y-3">
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-600 font-medium leading-relaxed">Verify the latest progress update against actual field reports.</p>
              </div>
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-600 font-medium leading-relaxed">Request clarification from <span className="italic text-slate-400">Not specified in dataset</span> regarding the expenditure discrepancy.</p>
              </div>
              <div className="bg-emerald-50/50 border border-emerald-100 rounded-xl p-4 flex gap-3 items-start">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-600 font-medium leading-relaxed">Schedule a follow-up review for the next reporting period.</p>
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="w-5 h-5 text-blue-500" />
              <h2 className="text-[11px] font-black text-slate-900 tracking-widest uppercase">Ask AI About This Project</h2>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm flex flex-col h-[400px]">
              
              {/* Chat Area */}
              <div className="flex-1 overflow-y-auto p-5">
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-600 shadow-sm leading-relaxed max-w-[85%]">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[9px] font-black text-emerald-600 tracking-widest uppercase">✦ PRAGYA AI</span>
                    </div>
                    <p className="mb-3 font-semibold">Hello! I'm the PRAGYA Risk Intelligence Assistant.</p>
                    <p className="mb-3">I answer questions about project risk scores, SHAP explanations, anomaly flags, milestone delays, and cost overruns — grounded entirely in stored AI outputs. I never invent data.</p>
                    <p className="text-slate-500 italic">Try: "Which projects in the roads sector are high risk?"</p>
                    <div className="text-[9px] text-slate-400 mt-2 text-right">08:42 PM</div>
                  </div>
                </div>
              </div>

              {/* Chat Inputs */}
              <div className="p-4 border-t border-slate-100 bg-slate-50/50">
                <div className="flex gap-2 mb-4 overflow-x-auto pb-2 scrollbar-hide">
                  <button className="shrink-0 bg-white border border-slate-200 px-3 py-1.5 rounded-full text-[10px] font-bold text-slate-600 hover:bg-slate-50 transition-colors whitespace-nowrap">
                    Which projects in the roads sector are high risk?
                  </button>
                  <button className="shrink-0 bg-white border border-slate-200 px-3 py-1.5 rounded-full text-[10px] font-bold text-slate-600 hover:bg-slate-50 transition-colors whitespace-nowrap">
                    Why is project PRJ-001 flagged?
                  </button>
                  <button className="shrink-0 bg-white border border-slate-200 px-3 py-1.5 rounded-full text-[10px] font-bold text-slate-600 hover:bg-slate-50 transition-colors whitespace-nowrap">
                    Compare risk factors
                  </button>
                </div>
                
                <div className="relative">
                  <input 
                    type="text" 
                    placeholder="Ask about project risk, SHAP reasons, anomaly flags..." 
                    className="w-full pl-4 pr-12 py-3 bg-white border border-slate-200 rounded-full text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                  <button className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-emerald-500 text-white rounded-full flex items-center justify-center hover:bg-emerald-600 transition-colors">
                    <Send className="w-3 h-3 ml-0.5" />
                  </button>
                </div>
                
                <p className="text-center text-[9px] text-slate-400 mt-3 italic">
                  Answers are grounded in stored AI risk data. Verify with the dashboard before acting.
                </p>
              </div>
            </div>
          </div>
          
        </div>
      </div>
      
    </div>
  );
}
