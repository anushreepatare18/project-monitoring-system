"use client";

import { useEffect, useState } from "react";
import { Search, Filter, AlertTriangle, MessageSquare, ShieldCheck, CheckCircle, Info } from "lucide-react";

export default function OfficerAlertsQueue() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8000\'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        // Generate mock alerts from dataset projects matching anomaly/risk criteria
        const alertProjects = data.filter((p: any) => p.is_anomalous || p.risk_level === "Critical" || p.risk_level === "High");
        setProjects(alertProjects);
        setLoading(false);
      });
  }, []);

  const filtered = projects.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    p.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleReviewAction = (actionStr: string) => {
    alert(`Action logged: ${actionStr}. State persistence simulated.`);
    setSelectedAlert(null);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 flex flex-col h-[calc(100vh-120px)]">
      <div className="shrink-0">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-indigo-600">Priority Alert Queue</h1>
        <p className="text-slate-500 font-medium mt-1">
          Investigate anomalies, review AI risk predictions, and log official actions.
        </p>
      </div>

      <div className="flex flex-1 gap-6 min-h-0">
        
        {/* Left Column: Queue */}
        <div className="w-full md:w-1/2 flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center bg-slate-50">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text"
                placeholder="Search Alert ID or Project..."
                className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
            <button className="ml-3 px-3 py-2 border border-slate-200 rounded-lg text-slate-600 bg-white hover:bg-slate-50 transition"><Filter className="w-4 h-4" /></button>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {loading ? <div className="p-8 text-center text-slate-500">Loading queue...</div> : null}
            <div className="divide-y divide-slate-100">
              {filtered.map((p, idx) => {
                const alertId = `ALT-${p.id.split('-')[1]}-${idx}`;
                const isSelected = selectedAlert?.id === p.id;
                
                return (
                  <div 
                    key={p.id}
                    onClick={() => setSelectedAlert(p)}
                    className={`p-4 cursor-pointer transition ${isSelected ? 'bg-indigo-50 border-l-4 border-indigo-600' : 'hover:bg-slate-50 border-l-4 border-transparent'}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="font-bold text-sm text-slate-900 truncate pr-4">{p.name}</div>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest shrink-0 ${p.risk_level === 'Critical' ? 'bg-rose-100 text-rose-700' : 'bg-orange-100 text-orange-700'}`}>
                        {p.risk_level}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 flex justify-between items-center">
                      <span>{alertId} • {p.is_anomalous ? "Data Anomaly" : "High Risk"}</span>
                      <span className="font-medium text-slate-400">1d ago</span>
                    </div>
                  </div>
                );
              })}
              {!loading && filtered.length === 0 && <div className="p-8 text-center text-slate-500">Queue is empty.</div>}
            </div>
          </div>
        </div>

        {/* Right Column: Alert Review Panel */}
        {selectedAlert ? (
          <div className="w-full md:w-1/2 flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden relative">
            <div className="p-5 border-b border-slate-100 bg-slate-50 flex justify-between items-center shrink-0">
              <h3 className="font-bold text-slate-900">Reviewing {selectedAlert.id}</h3>
              <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-blue-100 text-blue-700">Under Review</span>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-slate-500 block text-xs">Agency</span><span className="font-medium text-slate-900">{selectedAlert.implementing_agency}</span></div>
                <div><span className="text-slate-500 block text-xs">Sector</span><span className="font-medium text-slate-900">{selectedAlert.sector}</span></div>
                <div><span className="text-slate-500 block text-xs">Cost vs Exp</span><span className="font-medium text-slate-900">₹{selectedAlert.original_cost_cr?.toLocaleString()} Cr / ₹{selectedAlert.expenditure_cr?.toLocaleString()} Cr</span></div>
                <div><span className="text-slate-500 block text-xs">Progress (Phy/Fin)</span><span className="font-medium text-slate-900">{selectedAlert.physical_progress_pct}% / {selectedAlert.financial_progress_pct}%</span></div>
              </div>

              {selectedAlert.is_anomalous && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <div className="flex items-center text-amber-800 font-bold mb-2 text-sm"><AlertTriangle className="w-4 h-4 mr-2 text-amber-600" /> Automated Anomaly Flag</div>
                  <p className="text-xs text-amber-700 leading-relaxed">
                    <strong>Trigger Rule:</strong> Financial progress ({selectedAlert.financial_progress_pct}%) significantly outpaces reported physical progress ({selectedAlert.physical_progress_pct}%).
                    <br/><br/><em>*This is a rule-based check supporting officer review. It does not prove manipulation.</em>
                  </p>
                </div>
              )}

              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 font-bold text-sm text-slate-900 flex items-center">
                  <ShieldCheck className="w-4 h-4 mr-2 text-indigo-500" /> AI Risk Explanation (SHAP Mock)
                </div>
                <div className="p-4 space-y-3">
                  <div className="flex items-center text-xs">
                    <span className="w-40 truncate text-slate-600 font-medium">Historical Delay Flag</span>
                    <div className="flex-1 mx-3 h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-rose-500 w-[80%]"></div></div>
                    <span className="w-12 text-right text-rose-600 font-bold">+0.15</span>
                  </div>
                  <div className="flex items-center text-xs">
                    <span className="w-40 truncate text-slate-600 font-medium">Cost Overrun Flag</span>
                    <div className="flex-1 mx-3 h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-rose-500 w-[60%]"></div></div>
                    <span className="w-12 text-right text-rose-600 font-bold">+0.11</span>
                  </div>
                  <div className="flex items-center text-xs">
                    <span className="w-40 truncate text-slate-600 font-medium">Recent Update Rate</span>
                    <div className="flex-1 mx-3 h-2 bg-slate-100 rounded-full overflow-hidden flex justify-end"><div className="h-full bg-emerald-500 w-[30%]"></div></div>
                    <span className="w-12 text-right text-emerald-600 font-bold">-0.05</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-2 italic flex items-center"><Info className="w-3 h-3 mr-1" /> Feature contributions describe the model's prediction; they do not establish causation. (Illustrative Demo)</div>
                </div>
              </div>

            </div>

            {/* Action Footer */}
            <div className="p-5 border-t border-slate-100 bg-slate-50 shrink-0">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Officer Workflow Action</h4>
              <div className="flex space-x-3">
                <button onClick={() => handleReviewAction("Request Clarification")} className="flex-1 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 font-bold text-sm py-2 rounded-lg flex items-center justify-center transition">
                  <MessageSquare className="w-4 h-4 mr-2" /> Request Clarification
                </button>
                <button onClick={() => handleReviewAction("Mark Reviewed / No Issue")} className="flex-1 bg-indigo-600 text-white hover:bg-indigo-700 font-bold text-sm py-2 rounded-lg flex items-center justify-center transition">
                  <CheckCircle className="w-4 h-4 mr-2" /> Mark as Reviewed
                </button>
              </div>
            </div>

          </div>
        ) : (
          <div className="w-full md:w-1/2 flex flex-col items-center justify-center bg-slate-50 rounded-2xl border border-slate-200 border-dashed text-slate-400">
            <AlertTriangle className="w-12 h-12 mb-4 text-slate-300" />
            <p className="font-medium">Select an alert from the queue to review.</p>
          </div>
        )}

      </div>
    </div>
  );
}
