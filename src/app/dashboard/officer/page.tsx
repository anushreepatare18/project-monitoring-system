"use client";

import { 
  Target, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2 
} from "lucide-react";

export default function OfficerDashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-blue-600 dark:text-blue-500 tracking-tight">Monitoring Officer Dashboard</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Review AI risk anomalies, investigate project delays, and resolve field alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-xl w-fit">
            <Target className="w-5 h-5 text-blue-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">2111</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Total Monitored</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-red-50 dark:bg-red-900/30 p-3 rounded-xl w-fit">
            <ShieldAlert className="w-5 h-5 text-red-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">107</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Critical Risk</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-xl w-fit">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">0</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">High Risk</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-emerald-50 dark:bg-emerald-900/30 p-3 rounded-xl w-fit">
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">1977</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Projects On Track</div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-8 flex flex-col md:flex-row items-center justify-between">
        <div className="max-w-3xl pr-8">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Alert Queue Overview</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            You have <strong className="text-slate-900 dark:text-white font-bold">0 new anomalies</strong> detected by the PRAGYA AI engine that require triage. There are <strong className="text-slate-900 dark:text-white font-bold">0 alerts</strong> where implementing agencies have provided responses needing your final review.
          </p>
        </div>
        
        <div className="flex gap-4 mt-6 md:mt-0 shrink-0">
          <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-900/30 rounded-2xl p-4 w-32 flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-orange-600 dark:text-orange-500 mb-1">0</span>
            <span className="text-[10px] font-bold text-orange-800 dark:text-orange-400 uppercase tracking-widest text-center">Action Req.</span>
          </div>
          <div className="bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl p-4 w-32 flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-slate-700 dark:text-slate-300 mb-1">0</span>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest text-center">In Progress</span>
          </div>
        </div>
      </div>
    </div>
  );
}
