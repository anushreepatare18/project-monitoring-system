"use client";

import { useEffect, useState } from "react";
import { Flag, CheckCircle2, Clock, AlertCircle } from "lucide-react";

export default function AdminMilestones() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const Admin_NAME = "Agency_1";

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        
        setProjects(data);
        setLoading(false);
      });
  }, []);

  // Generate synthetic milestones based on the projects
  const milestones = projects.flatMap(p => [
    {
      id: `M-${p.id}-1`,
      project_id: p.id,
      project_name: p.name,
      name: "Site Clearance & Setup",
      planned_date: "2024-05-01",
      status: "Completed",
      progress: 100
    },
    {
      id: `M-${p.id}-2`,
      project_id: p.id,
      project_name: p.name,
      name: "Foundation & Sub-structure",
      planned_date: "2025-01-15",
      status: p.physical_progress_pct > 30 ? "Completed" : (p.physical_progress_pct > 0 ? "In Progress" : "Upcoming"),
      progress: p.physical_progress_pct > 30 ? 100 : p.physical_progress_pct * 2
    },
    {
      id: `M-${p.id}-3`,
      project_id: p.id,
      project_name: p.name,
      name: "Main Construction Phase",
      planned_date: "2026-06-30",
      status: p.physical_progress_pct > 80 ? "Completed" : (p.physical_progress_pct > 30 ? "In Progress" : "Upcoming"),
      progress: p.physical_progress_pct > 80 ? 100 : (p.physical_progress_pct > 30 ? p.physical_progress_pct : 0)
    }
  ]);

  const total = milestones.length;
  const completed = milestones.filter(m => m.status === 'Completed').length;
  const inProgress = milestones.filter(m => m.status === 'In Progress').length;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Project Milestones</h1>
        <p className="text-slate-500 font-medium mt-1">
          Monitor planned work stages and report milestone completion.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center">
          <Flag className="w-6 h-6 text-slate-400 mb-2" />
          <div className="text-3xl font-black text-slate-900">{total}</div>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">Total Milestones</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center">
          <CheckCircle2 className="w-6 h-6 text-emerald-500 mb-2" />
          <div className="text-3xl font-black text-emerald-600">{completed}</div>
          <div className="text-xs font-bold text-emerald-600 uppercase tracking-widest mt-1">Completed</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center">
          <Clock className="w-6 h-6 text-blue-500 mb-2" />
          <div className="text-3xl font-black text-blue-600">{inProgress}</div>
          <div className="text-xs font-bold text-blue-600 uppercase tracking-widest mt-1">In Progress</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center">
          <AlertCircle className="w-6 h-6 text-orange-500 mb-2" />
          <div className="text-3xl font-black text-orange-600">{total - completed - inProgress}</div>
          <div className="text-xs font-bold text-orange-600 uppercase tracking-widest mt-1">Upcoming</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Milestone</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Planned Date</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Progress</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Loading milestones...</td></tr>
              ) : milestones.map(m => (
                <tr key={m.id} className="hover:bg-slate-50 transition">
                  <td className="p-4">
                    <div className="font-bold text-sm text-slate-900">{m.name}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{m.id}</div>
                  </td>
                  <td className="p-4 text-sm text-slate-600 truncate max-w-[200px]">{m.project_name}</td>
                  <td className="p-4 text-sm text-slate-600">{m.planned_date}</td>
                  <td className="p-4">
                    <div className="flex items-center">
                      <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden mr-2">
                        <div className={`h-full ${m.status === 'Completed' ? 'bg-emerald-500' : 'bg-blue-500'}`} style={{ width: `${Math.min(100, m.progress)}%` }}></div>
                      </div>
                      <span className="text-xs font-bold text-slate-500">{m.progress.toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                      m.status === 'Completed' ? 'bg-emerald-100 text-emerald-700' : 
                      m.status === 'In Progress' ? 'bg-blue-100 text-blue-700' :
                      'bg-slate-100 text-slate-600'
                    }`}>
                      {m.status}
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
