"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  FolderKanban, 
  Activity, 
  AlertTriangle, 
  Bell, 
  ChevronRight, 
  Clock, 
  CheckCircle2, 
  FileText 
} from "lucide-react";

export default function AgencyOverview() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const AGENCY_NAME = "Agency_1";

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        const agencyProjects = data.filter((p: any) => p.implementing_agency === AGENCY_NAME);
        setProjects(agencyProjects);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const totalProjects = projects.length;
  const highRiskProjects = projects.filter(p => p.risk_level === 'High' || p.risk_level === 'Critical').length;
  // Mocking some other KPI values for the agency
  const updatesPending = 2;
  const alertsRequiringResponse = highRiskProjects; 

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading overview...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight text-emerald-600 dark:text-emerald-500">Agency Overview</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Quick summary of assigned projects, pending work, and important alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link href="/dashboard/agency/projects" className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 transition-transform cursor-pointer">
          <div className="flex items-center text-slate-500 mb-2">
            <FolderKanban className="w-4 h-4 mr-2" />
            <span className="text-xs font-bold uppercase tracking-widest">Total Projects</span>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">{totalProjects}</div>
        </Link>
        <Link href="/dashboard/agency/update" className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 transition-transform cursor-pointer">
          <div className="flex items-center text-slate-500 mb-2">
            <Activity className="w-4 h-4 mr-2" />
            <span className="text-xs font-bold uppercase tracking-widest">Updates Pending</span>
          </div>
          <div className="text-3xl font-black text-orange-600 dark:text-orange-500">{updatesPending}</div>
        </Link>
        <Link href="/dashboard/agency/insights" className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 transition-transform cursor-pointer">
          <div className="flex items-center text-slate-500 mb-2">
            <AlertTriangle className="w-4 h-4 mr-2" />
            <span className="text-xs font-bold uppercase tracking-widest">High/Critical Risk</span>
          </div>
          <div className="text-3xl font-black text-red-600 dark:text-red-500">{highRiskProjects}</div>
        </Link>
        <Link href="/dashboard/agency/alerts" className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 transition-transform cursor-pointer">
          <div className="flex items-center text-slate-500 mb-2">
            <Bell className="w-4 h-4 mr-2" />
            <span className="text-xs font-bold uppercase tracking-widest">Alerts to Respond</span>
          </div>
          <div className="text-3xl font-black text-red-600 dark:text-red-500">{alertsRequiringResponse}</div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 dark:border-slate-800">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Pending Action Required</h3>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            <div className="p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition flex items-start">
              <Clock className="w-5 h-5 text-orange-500 mt-0.5 mr-3 shrink-0" />
              <div className="flex-1">
                <div className="font-bold text-sm text-slate-900 dark:text-white">Project Update Due</div>
                <div className="text-xs text-slate-500 mt-1">PRJ-1001 - Review pending for October reporting.</div>
              </div>
              <Link href="/dashboard/agency/update" className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1.5 rounded-lg hover:bg-emerald-100 transition">REVIEW</Link>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 dark:border-slate-800">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Recent Activity</h3>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            <div className="p-4 flex items-start">
              <CheckCircle2 className="w-5 h-5 text-emerald-500 mt-0.5 mr-3 shrink-0" />
              <div>
                <div className="font-bold text-sm text-slate-900 dark:text-white">Update Submitted</div>
                <div className="text-xs text-slate-500 mt-1">PRJ-2004 - Submitted successfully on Oct 2nd.</div>
              </div>
            </div>
            <div className="p-4 flex items-start">
              <FileText className="w-5 h-5 text-blue-500 mt-0.5 mr-3 shrink-0" />
              <div>
                <div className="font-bold text-sm text-slate-900 dark:text-white">Clarification Added</div>
                <div className="text-xs text-slate-500 mt-1">PRJ-1050 - Added response to pending alert.</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">Project Snapshot</h3>
          <Link href="/dashboard/agency/projects" className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center">
            View All <ChevronRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project ID</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project Name</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Progress</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Risk Level</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {projects.slice(0, 5).map(p => (
                <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                  <td className="p-4 font-bold text-sm text-blue-600 dark:text-blue-400">{p.id}</td>
                  <td className="p-4 text-sm text-slate-700 dark:text-slate-300 truncate max-w-[200px]">{p.name}</td>
                  <td className="p-4">
                    <div className="w-32">
                      <div className="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${Math.min(100, p.physical_progress_pct)}%` }}></div>
                      </div>
                      <div className="text-[9px] font-bold text-slate-500 mt-1">{p.physical_progress_pct}%</div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${
                      p.risk_level === 'Critical' ? 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400' :
                      p.risk_level === 'High' ? 'bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400' :
                      p.risk_level === 'Medium' ? 'bg-yellow-50 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400' :
                      'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400'
                    }`}>
                      {p.risk_level}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <Link href={`/dashboard/agency/projects?id=${p.id}`} className="text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition">
                      VIEW
                    </Link>
                  </td>
                </tr>
              ))}
              {projects.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">No active projects found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
