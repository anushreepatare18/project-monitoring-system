"use client";

import { useState } from "react";
import { Search, ChevronDown, ChevronUp, BarChart3, AlertTriangle, Lightbulb } from "lucide-react";

export default function AdminInsights() {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Project Risk Register</h1>
      
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-800/50">
          <div className="relative w-96">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            <input 
              type="text" 
              placeholder="Search by Project ID or Name..."
              className="block w-full pl-10 pr-3 py-2 border border-slate-200 dark:border-slate-700 rounded-full bg-white dark:bg-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <button className="flex items-center px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-full bg-white dark:bg-slate-900 text-sm font-semibold text-slate-700 dark:text-slate-300">
              Critical
              <ChevronDown className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project ID</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest text-center">Overall Risk</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest text-center">Score</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Physical Progress</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              <tr className={`${expanded ? 'bg-slate-50/50 dark:bg-slate-800/20' : ''}`}>
                <td className="p-4">
                  <div className="font-bold text-emerald-600 dark:text-emerald-500 text-sm">PRJ-400259</div>
                  <div className="text-[11px] text-slate-400 truncate max-w-[250px]">Ghatampur Thermal Power Plant 3 X 660 MW</div>
                </td>
                <td className="p-4 text-center">
                  <span className="bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 px-3 py-1 rounded text-[10px] font-bold uppercase tracking-wider">
                    CRITICAL
                  </span>
                </td>
                <td className="p-4 text-center">
                  <div className="font-bold text-slate-900 dark:text-white text-sm">91/100</div>
                </td>
                <td className="p-4">
                  <div className="w-32">
                    <div className="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: '55.68%' }}></div>
                    </div>
                    <div className="text-[10px] font-bold text-slate-500 mt-1">55.68%</div>
                  </div>
                </td>
                <td className="p-4 text-right">
                  <button 
                    onClick={() => setExpanded(!expanded)}
                    className="inline-flex items-center px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-500 text-[10px] font-bold uppercase rounded-lg hover:bg-emerald-100 transition-colors"
                  >
                    Explain {expanded ? <ChevronUp className="w-3 h-3 ml-1" /> : <ChevronDown className="w-3 h-3 ml-1" />}
                  </button>
                </td>
              </tr>
              {expanded && (
                <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                  <td colSpan={5} className="p-6">
                    <div className="flex items-center mb-4">
                      <BarChart3 className="w-5 h-5 text-emerald-500 mr-2" />
                      <h3 className="font-bold text-slate-900 dark:text-white text-sm">Explanation Panel</h3>
                    </div>
                    
                    <div className="flex gap-2 mb-6">
                      <span className="px-3 py-1 bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400 rounded-full text-[10px] font-bold border border-emerald-100 dark:border-emerald-800">Cost Overrun 19%</span>
                      <span className="px-3 py-1 bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 rounded-full text-[10px] font-bold border border-red-100 dark:border-red-800">Time Delay 81%</span>
                      <span className="px-3 py-1 bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 rounded-full text-[10px] font-bold border border-red-100 dark:border-red-800">Impl Risk 98%</span>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center">
                          <BarChart3 className="w-4 h-4 mr-2" /> Top Contributing Features (SHAP Values)
                        </h4>
                        
                        <div className="space-y-4">
                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Expenditure To Progress Ratio</span>
                              <span className="text-xs font-bold text-red-500">+0.811</span>
                            </div>
                            <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-1">
                              <div className="h-full bg-red-500 rounded-full" style={{ width: '81%' }}></div>
                            </div>
                            <div className="text-[10px] text-slate-500 italic">Expenditure is in line with physical progress (0.0x), which increases risk.</div>
                          </div>

                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Days Since Last Update</span>
                              <span className="text-xs font-bold text-emerald-500">-0.801</span>
                            </div>
                            <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-1 flex justify-end">
                              <div className="h-full bg-emerald-500 rounded-full" style={{ width: '80%' }}></div>
                            </div>
                            <div className="text-[10px] text-slate-500 italic">Recent update received (~1.0 days ago), which decreases risk.</div>
                          </div>

                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Progress Gap</span>
                              <span className="text-xs font-bold text-red-500">+0.519</span>
                            </div>
                            <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-1">
                              <div className="h-full bg-red-500 rounded-full" style={{ width: '52%' }}></div>
                            </div>
                            <div className="text-[10px] text-slate-500 italic">Progress is 1.8% ahead of the expected planned level, which significantly increases risk.</div>
                          </div>

                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Sector</span>
                              <span className="text-xs font-bold text-emerald-500">-0.389</span>
                            </div>
                            <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-1 flex justify-end">
                              <div className="h-full bg-emerald-500 rounded-full" style={{ width: '39%' }}></div>
                            </div>
                            <div className="text-[10px] text-slate-500 italic">Sector has a value of Power, which decreases risk.</div>
                          </div>

                          <div>
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Agency</span>
                              <span className="text-xs font-bold text-emerald-500">-0.339</span>
                            </div>
                            <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-1 flex justify-end">
                              <div className="h-full bg-emerald-500 rounded-full" style={{ width: '34%' }}></div>
                            </div>
                            <div className="text-[10px] text-slate-500 italic">Agency has a value of Not specified in dataset, which decreases risk.</div>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-6">
                        <div>
                          <h4 className="text-xs font-bold text-red-500 uppercase tracking-widest mb-3 flex items-center">
                            <AlertTriangle className="w-4 h-4 mr-2" /> Early Warning Cards
                          </h4>
                          <div className="bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-xl p-4 flex items-start">
                            <div className="text-[10px] font-bold text-red-600 bg-red-100 dark:bg-red-900/40 px-2 py-0.5 rounded mr-3 shrink-0 uppercase tracking-wider">
                              MODEL-GENERATED
                            </div>
                            <div className="text-sm text-red-900 dark:text-red-300">
                              Value requiring verification: Expenditure ratio deviates significantly from historical baselines.
                            </div>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-xs font-bold text-orange-500 uppercase tracking-widest mb-3 flex items-center">
                            <Lightbulb className="w-4 h-4 mr-2" /> Suggested Agency Actions
                          </h4>
                          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex gap-3 flex-wrap">
                            <button className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                              Verify latest figures
                            </button>
                            <button className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                              Respond to officer
                            </button>
                            <button className="px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                              Add clarification
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="mt-8">
                      <h4 className="font-bold text-slate-900 dark:text-white text-sm">Sub-Risk Categories</h4>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
