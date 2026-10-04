"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Filter, Search, CheckCircle2, Info } from "lucide-react";

export default function MinistryAlerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const MINISTRY_NAME = "Ministry_7";

  useEffect(() => {
    fetch("http://localhost:8000/api/projects")
      .then(res => res.json())
      .then(data => {
        // We simulate alerts for projects that are anomalous or have high/critical risk
        const ministryProjects = data.filter((p: any) => p.ministry === MINISTRY_NAME);
        const generatedAlerts = ministryProjects
          .filter((p: any) => p.is_anomalous || p.risk_level === "Critical" || p.risk_level === "High")
          .map((p: any, idx: number) => ({
            id: `ALT-${p.id.split('-')[1]}-${idx}`,
            project_id: p.id,
            project_name: p.name,
            alert_type: p.is_anomalous ? "Data Anomaly" : "Risk Threshold Exceeded",
            severity: p.risk_level === "Critical" ? "Critical" : "High",
            detected_date: "2026-10-01",
            status: "Under Review"
          }));
        setAlerts(generatedAlerts);
        setLoading(false);
      });
  }, []);

  const filteredAlerts = alerts.filter(a => 
    a.project_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    a.project_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    a.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Priority Alerts & Reviews</h1>
        <p className="text-slate-500 font-medium mt-1">Review critical signals and anomalies for your portfolio.</p>
      </div>

      <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl flex items-start text-sm text-amber-800">
        <Info className="w-5 h-5 mr-3 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Access Notification:</span> You have view-only access to alerts within your ministry scope. Final verification and closure actions are restricted to authorized Monitoring Officers.
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-50">
          <div className="relative w-full max-w-lg">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text"
              placeholder="Search Alert ID or Project..."
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>
          <button className="flex items-center px-4 py-2 border border-slate-200 rounded-lg text-sm font-bold text-slate-600 bg-white hover:bg-slate-50 transition">
            <Filter className="w-4 h-4 mr-2" /> Filters
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Alert ID</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Type / Severity</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Detected Date</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Status</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={6} className="p-8 text-center text-slate-500">Loading alerts...</td></tr>
              ) : filteredAlerts.map(a => (
                <tr key={a.id} className="hover:bg-slate-50 transition">
                  <td className="p-4 text-sm font-bold text-slate-900">{a.id}</td>
                  <td className="p-4">
                    <div className="font-bold text-sm text-slate-900 truncate max-w-[250px]">{a.project_name}</div>
                    <div className="text-xs text-slate-500 mt-1">{a.project_id}</div>
                  </td>
                  <td className="p-4">
                    <div className="text-sm text-slate-800">{a.alert_type}</div>
                    <div className={`text-xs font-bold mt-1 ${a.severity === 'Critical' ? 'text-rose-600' : 'text-orange-600'}`}>
                      {a.severity}
                    </div>
                  </td>
                  <td className="p-4 text-sm text-slate-700">{a.detected_date}</td>
                  <td className="p-4">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest bg-blue-100 text-blue-700">
                      {a.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <button className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg transition">View Details</button>
                  </td>
                </tr>
              ))}
              {!loading && filteredAlerts.length === 0 && (
                <tr><td colSpan={6} className="p-8 text-center text-slate-500">No active priority alerts match the search.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
