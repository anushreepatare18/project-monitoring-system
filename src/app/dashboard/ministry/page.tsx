"use client";

import { 
  Briefcase, 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  IndianRupee, 
  Bell
} from "lucide-react";

export default function MinistryDashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500 tracking-tight">Ministry Portfolio Dashboard</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Monitor macro-level portfolio health, track physical vs financial progress, and allocate budgets effectively.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-xl w-fit">
            <Briefcase className="w-5 h-5 text-blue-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">2111</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Total Projects</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-emerald-50 dark:bg-emerald-900/30 p-3 rounded-xl w-fit">
            <Activity className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">1977</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Ongoing</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-red-50 dark:bg-red-900/30 p-3 rounded-xl w-fit">
            <AlertTriangle className="w-5 h-5 text-red-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">107</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">High/Critical Risk</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-xl w-fit">
            <CheckCircle2 className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">134</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Completed</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-indigo-50 dark:bg-indigo-900/30 p-3 rounded-xl w-fit">
            <IndianRupee className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none tracking-tight">₹13,23,634.19 Cr</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Total Approved Cost</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-xl w-fit">
            <IndianRupee className="w-5 h-5 text-orange-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none tracking-tight">₹11,03,149.13 Cr</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Total Expenditure</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-xl w-fit">
            <Bell className="w-5 h-5 text-orange-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">0</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Active Alerts</div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Portfolio Summary</h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
          The Ministry of Road Transport & Highways (MoRTH) is currently monitoring 1977 active infrastructure projects with a total approved cost of ₹13,23,634.19 Cr. To date, ₹11,03,149.13 Cr has been expended. There are 107 projects flagged with High or Critical AI risk scores requiring immediate attention.
        </p>
        <span className="inline-block px-4 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-[10px] font-bold uppercase tracking-widest rounded-full">
          DATA SCOPE: MORTH AUTHORIZED PROJECTS ONLY
        </span>
      </div>
    </div>
  );
}
