"use client";

import { useState } from "react";
import { AlertCircle, Plus, Search, HelpCircle, FileText } from "lucide-react";

export default function AdminIssues() {
  const [issues] = useState([
    { id: "ISS-001", project: "PRJ-1002", category: "Land Acquisition", severity: "High", date: "2026-09-15", status: "Under Review", description: "Delay in acquiring 2 hectares in sector B." },
    { id: "ISS-002", project: "PRJ-1005", category: "Environmental Clearance", severity: "Critical", date: "2026-09-28", status: "Open", description: "Pending forest department NOC for pipeline routing." },
    { id: "ISS-003", project: "PRJ-1010", category: "Weather", severity: "Medium", date: "2026-10-01", status: "Resolved", description: "Unseasonal monsoon stopped foundation work for 12 days." }
  ]);

  const [showForm, setShowForm] = useState(false);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Issues & Constraints</h1>
          <p className="text-slate-500 font-medium mt-1">
            Report project blockers and track their resolution.
          </p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center transition"
        >
          {showForm ? 'Cancel' : <><Plus className="w-4 h-4 mr-2" /> Report Issue</>}
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2 text-orange-500" /> New Issue Report
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Project</label>
              <select className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
                <option>PRJ-1001</option>
                <option>PRJ-1002</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Category</label>
              <select className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
                <option>Land acquisition</option>
                <option>Funding</option>
                <option>Environmental clearance</option>
                <option>Weather</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Severity</label>
              <select className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
                <option>Medium</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1">Description</label>
              <textarea rows={3} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" placeholder="Detail the constraint..."></textarea>
            </div>
            <div className="md:col-span-2 flex justify-end">
              <button className="bg-emerald-600 text-white px-6 py-2 rounded-lg text-sm font-bold hover:bg-emerald-700">Submit Report</button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
          <h3 className="font-bold text-sm text-slate-700">Issue Register</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Issue ID</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Category & Severity</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Reported</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {issues.map(iss => (
                <tr key={iss.id} className="hover:bg-slate-50 transition cursor-pointer">
                  <td className="p-4 font-bold text-sm text-slate-900">{iss.id}</td>
                  <td className="p-4 text-sm text-slate-600">{iss.project}</td>
                  <td className="p-4">
                    <div className="text-sm font-bold text-slate-700">{iss.category}</div>
                    <div className={`text-[10px] font-bold uppercase tracking-wider ${iss.severity === 'Critical' ? 'text-rose-600' : 'text-orange-600'}`}>{iss.severity}</div>
                  </td>
                  <td className="p-4 text-sm text-slate-600">{iss.date}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                      iss.status === 'Resolved' ? 'bg-emerald-100 text-emerald-700' : 
                      iss.status === 'Open' ? 'bg-rose-100 text-rose-700' :
                      'bg-orange-100 text-orange-700'
                    }`}>
                      {iss.status}
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
