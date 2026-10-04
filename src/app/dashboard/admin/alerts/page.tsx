"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Clock, CheckCircle2, Search, Filter, Send } from "lucide-react";

export default function AdminAlerts() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  const [response, setResponse] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const Admin_NAME = "Agency_1";

  useEffect(() => {
    fetch("http://localhost:8000/api/projects")
      .then(res => res.json())
      .then(data => {
        
        setProjects(data);
        setLoading(false);
      });
  }, []);

  // Generate synthetic alerts based on risk and delays for demonstration
  const alerts = projects.flatMap(p => {
    const list = [];
    if (p.risk_level === 'Critical' || p.risk_level === 'High') {
      list.push({
        id: `ALT-${p.id}-01`,
        project_id: p.id,
        project_name: p.name,
        type: p.overrun_flag ? 'Cost Escalation' : 'Schedule Delay',
        severity: p.risk_level,
        date: p.last_update_date || '2026-10-01',
        status: p.risk_level === 'Critical' ? 'Awaiting Response' : 'Under Review',
        description: `The AI model flagged a high probability of ${p.overrun_flag ? 'cost overrun' : 'time delay'}. Please verify current expenditure and physical progress rates.`,
        action_required: "Submit clarification regarding current pace of work and mitigation plan."
      });
    }
    return list;
  });

  const totalAlerts = alerts.length;
  const awaitingResponse = alerts.filter(a => a.status === 'Awaiting Response').length;

  const handleSubmitResponse = () => {
    if (!response.trim() || !selectedAlert) return;
    setSubmitting(true);
    setTimeout(() => {
      selectedAlert.status = 'Response Submitted';
      setSubmitting(false);
      setSelectedAlert(null);
      setResponse("");
    }, 1000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Alerts & Responses</h1>
        <p className="text-slate-500 font-medium mt-1">
          Review system alerts and submit required clarifications.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Total Alerts</div>
          <div className="text-3xl font-black text-slate-900">{totalAlerts}</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-orange-200 bg-orange-50/50 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="text-sm font-bold text-orange-600 uppercase tracking-widest mb-1">Awaiting Response</div>
          <div className="text-3xl font-black text-orange-600">{awaitingResponse}</div>
        </div>
      </div>

      <div className="flex gap-6 relative">
        <div className={`transition-all duration-300 ${selectedAlert ? 'w-2/3 hidden md:block' : 'w-full'}`}>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100">
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Alert ID / Project</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Type & Severity</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Date</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr><td colSpan={4} className="p-8 text-center text-slate-500">Loading alerts...</td></tr>
                  ) : alerts.map(a => (
                    <tr 
                      key={a.id} 
                      className={`hover:bg-slate-50 transition cursor-pointer ${selectedAlert?.id === a.id ? 'bg-orange-50 border-l-4 border-orange-500' : 'border-l-4 border-transparent'}`}
                      onClick={() => setSelectedAlert(a)}
                    >
                      <td className="p-4">
                        <div className="font-bold text-sm text-slate-900">{a.id}</div>
                        <div className="text-xs text-slate-500 truncate max-w-[200px]">{a.project_name}</div>
                      </td>
                      <td className="p-4">
                        <div className="text-sm font-bold text-slate-700">{a.type}</div>
                        <div className={`text-[10px] font-bold uppercase ${a.severity === 'Critical' ? 'text-rose-600' : 'text-orange-600'}`}>{a.severity}</div>
                      </td>
                      <td className="p-4 text-sm text-slate-600">{a.date}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                          a.status === 'Awaiting Response' ? 'bg-orange-100 text-orange-700' : 
                          a.status === 'Response Submitted' ? 'bg-emerald-100 text-emerald-700' :
                          'bg-blue-100 text-blue-700'
                        }`}>
                          {a.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {!loading && alerts.length === 0 && (
                    <tr><td colSpan={4} className="p-8 text-center text-slate-500">No alerts found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Alert Details & Response Panel */}
        {selectedAlert && (
          <div className="w-full md:w-1/3 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[calc(100vh-140px)] sticky top-24">
            <div className="p-4 border-b border-slate-100 bg-orange-600 text-white flex justify-between items-center">
              <h3 className="font-bold text-sm">Alert Details</h3>
              <button onClick={() => setSelectedAlert(null)} className="text-orange-200 hover:text-white transition text-xs font-bold uppercase">Close</button>
            </div>
            <div className="p-5 flex-1 overflow-y-auto space-y-6">
              
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Context</h4>
                <div className="text-sm">
                  <div className="mb-1"><span className="text-slate-500">Alert ID:</span> <span className="font-bold">{selectedAlert.id}</span></div>
                  <div className="mb-1"><span className="text-slate-500">Project:</span> <span className="font-bold">{selectedAlert.project_id}</span></div>
                  <div className="mb-1"><span className="text-slate-500">Severity:</span> <span className={`font-bold ${selectedAlert.severity === 'Critical' ? 'text-rose-600' : 'text-orange-600'}`}>{selectedAlert.severity}</span></div>
                </div>
              </div>

              <div className="bg-orange-50 border border-orange-100 p-4 rounded-xl text-sm text-orange-900">
                <div className="font-bold mb-1 flex items-center"><AlertTriangle className="w-4 h-4 mr-2" /> Description</div>
                <p>{selectedAlert.description}</p>
                <div className="mt-3 font-bold">Action Required:</div>
                <p>{selectedAlert.action_required}</p>
              </div>

              {selectedAlert.status === 'Response Submitted' ? (
                <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl text-sm text-emerald-900 flex items-start">
                  <CheckCircle2 className="w-5 h-5 mr-2 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold">Response Submitted</div>
                    <p className="mt-1">Your clarification has been recorded and is pending review by the Monitoring Officer.</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 border-t border-slate-100 pt-4">
                  <label className="block text-xs font-bold text-slate-700">Submit Clarification</label>
                  <textarea 
                    rows={4}
                    value={response}
                    onChange={e => setResponse(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                    placeholder="Provide detailed explanation or corrective action plan..."
                  />
                  <button 
                    onClick={handleSubmitResponse}
                    disabled={!response.trim() || submitting}
                    className="w-full bg-emerald-600 text-white rounded-lg py-2 text-sm font-bold flex items-center justify-center hover:bg-emerald-700 disabled:opacity-50 transition"
                  >
                    {submitting ? 'Submitting...' : <><Send className="w-4 h-4 mr-2" /> Submit Response</>}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
