"use client";

import { useEffect, useState } from "react";
import { History, Download, Filter } from "lucide-react";

export default function AgencyUpdateHistory() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const AGENCY_NAME = "Agency_1";

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8000\'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        const agencyProjects = data.filter((p: any) => p.implementing_agency === AGENCY_NAME);
        setProjects(agencyProjects);
        setLoading(false);
      });
  }, []);

  // Synthetic history entries
  const history = projects.slice(0, 10).map(p => ({
    update_id: `UPD-${p.id}-10`,
    project_id: p.id,
    project_name: p.name,
    month: "Oct 2026",
    date: p.last_update_date || "2026-10-02",
    phy: p.physical_progress_pct,
    fin: p.financial_progress_pct || 0,
    status: "Submitted",
    remarks: "Progress on track."
  }));

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Update History</h1>
          <p className="text-slate-500 font-medium mt-1">
            Traceable record of all periodic updates submitted by {AGENCY_NAME}.
          </p>
        </div>
        <button className="bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold flex items-center hover:bg-slate-50 transition">
          <Download className="w-4 h-4 mr-2" /> Export CSV
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex gap-4">
          <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
            <option>All Months</option>
            <option>Oct 2026</option>
            <option>Sep 2026</option>
          </select>
          <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
            <option>All Statuses</option>
            <option>Submitted</option>
            <option>Under Review</option>
            <option>Returned</option>
          </select>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Update ID</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Month / Date</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Progress (Phy/Fin)</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Loading history...</td></tr>
              ) : history.map(h => (
                <tr key={h.update_id} className="hover:bg-slate-50 transition cursor-pointer">
                  <td className="p-4 font-bold text-sm text-slate-900">{h.update_id}</td>
                  <td className="p-4">
                    <div className="text-sm font-bold text-slate-700 truncate max-w-[200px]">{h.project_name}</div>
                    <div className="text-xs text-slate-500">{h.project_id}</div>
                  </td>
                  <td className="p-4">
                    <div className="text-sm font-bold text-slate-700">{h.month}</div>
                    <div className="text-xs text-slate-500">{h.date}</div>
                  </td>
                  <td className="p-4 text-sm font-medium">
                    <span className="text-blue-600">{h.phy}%</span> / <span className="text-indigo-600">{h.fin}%</span>
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest bg-emerald-100 text-emerald-700">
                      {h.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
