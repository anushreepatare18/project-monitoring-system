"use client";

import { 
  Globe, 
  Activity, 
  IndianRupee,
  Info
} from "lucide-react";

export default function PublicDashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-teal-600 dark:text-teal-500 tracking-tight">Public Transparency Portal</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Explore approved information regarding major central sector infrastructure projects.
        </p>
      </div>

      <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-2xl p-4 flex items-start">
        <Info className="w-5 h-5 text-slate-500 dark:text-slate-400 mr-3 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-700 dark:text-slate-300 text-sm mb-1">Transparency Notice & Demo Data</h4>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            This dashboard displays only projects explicitly marked as public by the respective Ministries. The data shown here is <strong className="font-bold">illustrative sample data</strong> intended to demonstrate the PRAGYA AI prototype's transparency features. It does not represent live government data.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-xl w-fit">
            <Globe className="w-5 h-5 text-blue-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">0</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Published Projects</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-emerald-50 dark:bg-emerald-900/30 p-3 rounded-xl w-fit">
            <Activity className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none">0</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Ongoing Projects</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-indigo-50 dark:bg-indigo-900/30 p-3 rounded-xl w-fit">
            <IndianRupee className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none tracking-tight">₹0.00 Cr</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Total Approved Cost</div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between min-h-[140px]">
          <div className="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-xl w-fit">
            <IndianRupee className="w-5 h-5 text-orange-500" />
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-slate-900 dark:text-white leading-none tracking-tight">₹0.00 Cr</div>
            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-2">Total Expenditure</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">About the Portal</h3>
          <div className="space-y-4 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            <p>
              The PRAGYA AI Public Dashboard serves as a centralized gateway for citizens and stakeholders to monitor the execution of national infrastructure projects. Our goal is to promote accountability by providing standardized, up-to-date visibility into physical and financial progress.
            </p>
            <p>
              All records presented here undergo a rigorous internal verification process by Monitoring Officers and are approved by the relevant Ministry before publication. Note that internal risk assessments and preliminary findings are excluded to prevent misinformation.
            </p>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4">Projects by Sector</h3>
          <div className="flex-1 flex items-center justify-center text-sm text-slate-400 italic">
            No sectors available.
          </div>
        </div>
      </div>

    </div>
  );
}
