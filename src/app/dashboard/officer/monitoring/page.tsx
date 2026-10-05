"use client";

import { Target } from "lucide-react";

export default function OfficerMonitoring() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-[#1e3a8a] dark:text-blue-400 tracking-tight">Project Monitoring</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Track the physical and financial progress of all your assigned projects.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-12 flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-16 h-16 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-500 flex items-center justify-center mb-6">
          <Target className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Monitoring Workspace</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 text-center max-w-md mb-8 leading-relaxed">
          Select a project from the list below to view detailed progress updates, milestones, and funding releases.
        </p>
        
        <div className="w-full max-w-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 rounded-xl p-4 text-center">
          <span className="text-slate-400 text-sm italic">Select a project to load its monitoring details...</span>
        </div>
      </div>
    </div>
  );
}
