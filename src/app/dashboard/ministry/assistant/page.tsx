"use client";

import { 
  Bot, 
  Send, 
  User,
  Database,
  Search,
  MessageSquare,
  ShieldCheck,
  AlertTriangle
} from "lucide-react";

export default function RiskAssistant() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500 tracking-tight">PRAGYA Risk Intelligence Assistant</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1 max-w-3xl">
          Ask plain-English questions about project risk — grounded in stored SHAP outputs, anomaly flags, and benchmark data. Answers are never fabricated.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col h-[700px]">
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50 dark:bg-slate-900/50">
              
              {/* User Message */}
              <div className="flex flex-col items-end">
                <div className="flex items-end">
                  <div className="bg-emerald-600 text-white px-5 py-3 rounded-2xl rounded-tr-sm max-w-lg shadow-sm text-sm font-medium">
                    Which of our projects are high risk this month?
                  </div>
                  <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center ml-3 shrink-0 text-slate-500">
                    <User className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-[10px] font-bold text-slate-400 mt-1 mr-11">04:17 PM</div>
              </div>

              {/* Bot Message */}
              <div className="flex flex-col items-start">
                <div className="flex items-end w-full">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-500 flex items-center justify-center mr-3 shrink-0 mb-auto">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 px-5 py-4 rounded-2xl rounded-tl-sm w-full max-w-2xl shadow-sm">
                    <div className="flex items-center space-x-2 mb-3">
                      <span className="text-[10px] font-black text-emerald-600 dark:text-emerald-500 uppercase tracking-widest flex items-center">
                        <span className="mr-1">✨</span> PRAGYA AI
                      </span>
                      <span className="bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded flex items-center">
                        <Database className="w-3 h-3 mr-1" /> RAW DATA
                      </span>
                    </div>
                    
                    <div className="text-sm text-slate-700 dark:text-slate-300 space-y-3 leading-relaxed">
                      <p>Found 3 project(s) as of 2026-09-29:</p>
                      <ul className="space-y-2">
                        <li>• <strong>P-ROADS-0891</strong> — Mumbai Coastal Road Extension: Risk 91.7/100 (Critical). Delay 12.0 months. Cost Overrun 34.1%</li>
                        <li>• <strong>P-ROADS-0457</strong> — NH-48 Bangalore-Chennai Expressway Phase 2: Risk 82.4/100 (Critical). Delay 7.0 months, Cost Overrun 18.5%</li>
                        <li>• <strong>P-ROADS-0102</strong> — Delhi-Meerut Regional Rapid Transit: Risk 44.6/100 (Medium), Delay 2.0 months, Cost Overrun 11.2%</li>
                      </ul>
                    </div>

                    <div className="flex flex-wrap gap-2 mt-4">
                      <button className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50 bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1.5 rounded-full hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition">
                        <span className="mr-1 inline-block w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> P-ROADS-0891
                      </button>
                      <button className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50 bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1.5 rounded-full hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition">
                        <span className="mr-1 inline-block w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> P-ROADS-0457
                      </button>
                      <button className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50 bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1.5 rounded-full hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition">
                        <span className="mr-1 inline-block w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> P-ROADS-0102
                      </button>
                    </div>

                    <div className="mt-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-900/30 p-2.5 rounded-lg flex items-start">
                      <AlertTriangle className="w-3.5 h-3.5 text-yellow-600 dark:text-yellow-500 mt-0.5 mr-2 shrink-0" />
                      <p className="text-[10px] font-semibold text-yellow-800 dark:text-yellow-400/90">
                        Answers are generated from stored risk data as of 2026-09-29 and are for review support, not a final finding.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="text-[10px] font-bold text-slate-400 mt-1 ml-11">04:17 PM</div>
              </div>

            </div>

            <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
              <div className="flex gap-2 overflow-x-auto pb-3 scrollbar-hide">
                <button className="whitespace-nowrap px-4 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">
                  Which of our projects are high risk this month?
                </button>
                <button className="whitespace-nowrap px-4 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">
                  Projects with cost overrun above 15%
                </button>
                <button className="whitespace-nowrap px-4 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">
                  Sector-wise risk summary
                </button>
                <button className="whitespace-nowrap px-4 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">
                  Show more
                </button>
              </div>
              <div className="relative">
                <input 
                  type="text" 
                  placeholder="Ask about project risk, SHAP reasons, anomaly flags..."
                  className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full pl-5 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <button className="absolute right-2 top-2 bg-emerald-500 text-white p-1.5 rounded-full hover:bg-emerald-600 transition">
                  <Send className="w-4 h-4" />
                </button>
              </div>
              <p className="text-center text-[9px] font-bold text-slate-400 mt-2 uppercase tracking-widest">
                Answers are grounded in stored AI risk data. Verify with the dashboard before acting.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
            <h3 className="font-bold text-slate-900 dark:text-white mb-5 flex items-center text-sm">
              <ShieldCheck className="w-4 h-4 mr-2 text-emerald-500" /> How It Works
            </h3>
            
            <div className="space-y-4">
              <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30 p-4 rounded-xl flex items-start">
                <div className="text-blue-500 font-black mr-3 mt-0.5">1</div>
                <div>
                  <h4 className="text-xs font-bold text-blue-800 dark:text-blue-400 uppercase tracking-widest flex items-center mb-1">
                    <MessageSquare className="w-3 h-3 mr-1" /> Intent Parsing
                  </h4>
                  <p className="text-xs text-blue-700/80 dark:text-blue-300/80">LLM extracts structured fields (sector, risk band, project IDs) from your question. It never supplies facts.</p>
                </div>
              </div>
              
              <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-900/30 p-4 rounded-xl flex items-start">
                <div className="text-emerald-500 font-black mr-3 mt-0.5">2</div>
                <div>
                  <h4 className="text-xs font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-widest flex items-center mb-1">
                    <Database className="w-3 h-3 mr-1" /> Grounded Retrieval
                  </h4>
                  <p className="text-xs text-emerald-700/80 dark:text-emerald-300/80">A deterministic query runs against the actual risk store — risk scores, SHAP reasons, anomaly flags. Every query is logged.</p>
                </div>
              </div>

              <div className="bg-purple-50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-900/30 p-4 rounded-xl flex items-start">
                <div className="text-purple-500 font-black mr-3 mt-0.5">3</div>
                <div>
                  <h4 className="text-xs font-bold text-purple-800 dark:text-purple-400 uppercase tracking-widest flex items-center mb-1">
                    <Bot className="w-3 h-3 mr-1" /> Answer Composition
                  </h4>
                  <p className="text-xs text-purple-700/80 dark:text-purple-300/80">Only the retrieved rows are passed to the LLM. For "why flagged" queries, SHAP output is returned verbatim — no LLM involved.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
            <h3 className="font-bold text-slate-900 dark:text-white mb-5 text-sm">Answer Badge Guide</h3>
            
            <div className="space-y-4 text-xs">
              <div className="flex items-start">
                <span className="px-2 py-0.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 font-bold uppercase tracking-widest rounded mr-3 shrink-0 text-[9px]">
                  DIRECT SHAP
                </span>
                <span className="text-slate-600 dark:text-slate-400">SHAP reasons returned verbatim — no LLM generation</span>
              </div>
              <div className="flex items-start">
                <span className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800 font-bold uppercase tracking-widest rounded mr-3 shrink-0 text-[9px]">
                  DATA-GROUNDED
                </span>
                <span className="text-slate-600 dark:text-slate-400">LLM narrates only retrieved rows — no invented data</span>
              </div>
              <div className="flex items-start">
                <span className="px-2 py-0.5 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800 font-bold uppercase tracking-widest rounded mr-3 shrink-0 text-[9px]">
                  NO DATA FOUND
                </span>
                <span className="text-slate-600 dark:text-slate-400">Query returned zero rows — no guess made</span>
              </div>
              <div className="flex items-start">
                <span className="px-2 py-0.5 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 font-bold uppercase tracking-widest rounded mr-3 shrink-0 text-[9px]">
                  OUT OF SCOPE
                </span>
                <span className="text-slate-600 dark:text-slate-400">Question references data not in the risk store</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
