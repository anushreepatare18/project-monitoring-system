"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Building, 
  CheckCircle, 
  FileWarning, 
  BrainCircuit, 
  AlertTriangle, 
  Plus, 
  FolderKanban,
  Clock,
  ChevronRight,
  CheckCircle2
} from "lucide-react";

export default function AdminDashboard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const AGENCY_NAME = "Agency_1";

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        
        setProjects(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const totalAssigned = 2111;
  const activeProjects = 1977;
  const updatesPending = 0;
  const highCriticalRisk = 107;
  const alertsRequiringResponse = 0;

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading dashboard...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500 tracking-tight">Admin Dashboard</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Monitor your assigned projects, submit updates, and respond to priority alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center text-blue-500 mb-2">
            <Building className="w-5 h-5 mr-2" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-4">{totalAssigned}</div>
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Total Assigned</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center text-emerald-500 mb-2">
            <CheckCircle className="w-5 h-5 mr-2" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-4">{activeProjects}</div>
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Active Projects</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center text-orange-500 mb-2">
            <FileWarning className="w-5 h-5 mr-2" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-4">{updatesPending}</div>
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Updates Pending</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center text-red-500 mb-2">
            <BrainCircuit className="w-5 h-5 mr-2" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-4">{highCriticalRisk}</div>
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">High/Critical Risk</div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center text-orange-500 mb-2">
            <AlertTriangle className="w-5 h-5 mr-2" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-4">{alertsRequiringResponse}</div>
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Alerts Requiring<br/>Response</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden p-6">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center mb-6">
              <span className="text-orange-500 mr-2">⚡</span> Pending Action Required
            </h3>
            <div className="flex flex-col items-center justify-center py-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-800">
              <div className="w-12 h-12 rounded-full border-2 border-emerald-500 text-emerald-500 flex items-center justify-center mb-3">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div className="font-bold text-slate-900 dark:text-white text-lg">You're all caught up!</div>
              <div className="text-sm text-slate-500 mt-1">No pending updates or alerts require your immediate attention.</div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Priority Projects Snapshot</h3>
              <Link href="/dashboard/admin/projects" className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center">
                View All <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800">
                    <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Project</th>
                    <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Phys / Fin %</th>
                    <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Risk Level</th>
                    <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Update Status</th>
                    <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                    <td className="p-4">
                      <div className="font-bold text-sm text-emerald-600 dark:text-emerald-500">PRJ-618007</div>
                      <div className="text-xs text-slate-500 truncate max-w-[200px]">Jaynagar-Narahia Section km 15...</div>
                    </td>
                    <td className="p-4">
                      <div className="font-bold text-sm text-slate-900 dark:text-white">99.0% / 0.0%</div>
                    </td>
                    <td className="p-4">
                      <span className="bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider">
                        CRITICAL
                      </span>
                    </td>
                    <td className="p-4 text-sm text-slate-700 dark:text-slate-300">Accepted</td>
                    <td className="p-4 text-right">
                      <Link href="/dashboard/admin/projects?id=PRJ-618007" className="text-[10px] font-bold text-emerald-600 dark:text-emerald-500 hover:text-emerald-700 transition uppercase">
                        VIEW
                      </Link>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                    <td className="p-4">
                      <div className="font-bold text-sm text-emerald-600 dark:text-emerald-500">PRJ-618502</div>
                      <div className="text-xs text-slate-500 truncate max-w-[200px]">Construction of missing link...</div>
                    </td>
                    <td className="p-4">
                      <div className="font-bold text-sm text-slate-900 dark:text-white">100.0% / 100.0%</div>
                    </td>
                    <td className="p-4">
                      <span className="bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider">
                        CRITICAL
                      </span>
                    </td>
                    <td className="p-4 text-sm text-slate-700 dark:text-slate-300">Accepted</td>
                    <td className="p-4 text-right">
                      <Link href="/dashboard/admin/projects?id=PRJ-618502" className="text-[10px] font-bold text-emerald-600 dark:text-emerald-500 hover:text-emerald-700 transition uppercase">
                        VIEW
                      </Link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Quick Actions</h3>
            </div>
            <div className="p-4 space-y-3">
              <Link href="/dashboard/admin/update" className="flex items-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition cursor-pointer">
                <div className="bg-emerald-50 dark:bg-emerald-900/30 p-2 rounded-lg text-emerald-500 mr-3">
                  <Plus className="w-5 h-5" />
                </div>
                <span className="font-semibold text-sm text-slate-700 dark:text-slate-300">Submit Project Update</span>
              </Link>
              <Link href="/dashboard/admin/projects" className="flex items-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition cursor-pointer">
                <div className="bg-blue-50 dark:bg-blue-900/30 p-2 rounded-lg text-blue-500 mr-3">
                  <FolderKanban className="w-5 h-5" />
                </div>
                <span className="font-semibold text-sm text-slate-700 dark:text-slate-300">View My Projects</span>
              </Link>
              <Link href="/dashboard/admin/alerts" className="flex items-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition cursor-pointer">
                <div className="bg-orange-50 dark:bg-orange-900/30 p-2 rounded-lg text-orange-500 mr-3">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <span className="font-semibold text-sm text-slate-700 dark:text-slate-300">Review Alerts</span>
              </Link>
              <Link href="/dashboard/admin/history" className="flex items-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition cursor-pointer">
                <div className="bg-indigo-50 dark:bg-indigo-900/30 p-2 rounded-lg text-indigo-500 mr-3">
                  <Clock className="w-5 h-5" />
                </div>
                <span className="font-semibold text-sm text-slate-700 dark:text-slate-300">View Update History</span>
              </Link>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Recent Activity</h3>
              <Link href="/dashboard/admin/history" className="text-[10px] font-bold text-emerald-600 dark:text-emerald-500 hover:text-emerald-700 transition uppercase">
                View All
              </Link>
            </div>
            <div className="p-6 text-center text-sm text-slate-500">
              No recent activity to show.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

