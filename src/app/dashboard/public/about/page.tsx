"use client";

import { 
  Eye, 
  Activity, 
  ShieldCheck,
  Database,
  CheckCircle2
} from "lucide-react";

export default function PublicAbout() {
  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold text-teal-600 dark:text-teal-500 tracking-tight">About PRAGYA AI</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Understanding how India monitors and protects public infrastructure investments.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-8">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Our Mission</h2>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
              PRAGYA AI is an advanced AI-powered Infrastructure Project Monitoring System developed to bring unparalleled transparency, efficiency, and predictive oversight to India's national infrastructure growth. By leveraging real-time data and predictive analytics, PRAGYA AI ensures that critical projects — from highways to airports — are completed on time and within budget.
            </p>

            <div className="space-y-3">
              <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 rounded-xl p-4 flex items-center">
                <div className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-500 flex items-center justify-center mr-4 shrink-0">
                  <Eye className="w-4 h-4" />
                </div>
                <span className="font-bold text-slate-700 dark:text-slate-200 text-sm">Radical Transparency</span>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 rounded-xl p-4 flex items-center">
                <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-500 flex items-center justify-center mr-4 shrink-0">
                  <Activity className="w-4 h-4" />
                </div>
                <span className="font-bold text-slate-700 dark:text-slate-200 text-sm">Predictive Risk Monitoring</span>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 rounded-xl p-4 flex items-center">
                <div className="w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-500 flex items-center justify-center mr-4 shrink-0">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <span className="font-bold text-slate-700 dark:text-slate-200 text-sm">Inter-Ministerial Accountability</span>
              </div>
            </div>
          </div>

          <div className="bg-[#0f172a] rounded-2xl shadow-sm p-8 text-white">
            <h3 className="text-lg font-bold flex items-center mb-4">
              <Database className="w-5 h-5 mr-2 text-teal-400" /> Data & Privacy Policy
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              The Public Transparency Portal provides access only to approved execution metrics and financials. Internal AI risk scores, predictive models, and Monitoring Officer audit logs are strictly shielded to protect sensitive governmental operations.
            </p>
          </div>
        </div>

        <div className="bg-teal-50 dark:bg-teal-900/10 rounded-2xl border border-teal-100 dark:border-teal-900/30 shadow-sm p-8">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-8">How It Works</h2>
          
          <div className="relative border-l-2 border-teal-200 dark:border-teal-800 ml-4 space-y-12">
            
            <div className="relative">
              <div className="absolute -left-[25px] top-2 w-12 h-12 rounded-full bg-teal-500 text-white flex items-center justify-center font-black shadow-[0_0_0_4px_#f0fdf4] dark:shadow-[0_0_0_4px_#022c22]">
                1
              </div>
              <div className="ml-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm relative">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm mb-1">Data Ingestion</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">Implementing Agencies submit progress updates via standardized digital forms.</p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-[25px] top-2 w-12 h-12 rounded-full bg-teal-500 text-white flex items-center justify-center font-black shadow-[0_0_0_4px_#f0fdf4] dark:shadow-[0_0_0_4px_#022c22]">
                2
              </div>
              <div className="ml-12 mr-8 md:mr-0 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm relative right-16 md:right-32 lg:right-4 xl:right-12">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm mb-1">AI Risk Triage</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">PRAGYA models scan data for anomalies and assign predictive risk scores.</p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-[25px] top-2 w-12 h-12 rounded-full bg-teal-500 text-white flex items-center justify-center font-black shadow-[0_0_0_4px_#f0fdf4] dark:shadow-[0_0_0_4px_#022c22]">
                3
              </div>
              <div className="ml-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm relative">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm mb-1">Human Review</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">Monitoring Officers review AI flags, request clarifications, and enforce accountability.</p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-[17px] top-3 w-8 h-8 rounded-full bg-teal-500 text-white flex items-center justify-center font-black shadow-[0_0_0_4px_#f0fdf4] dark:shadow-[0_0_0_4px_#022c22]">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div className="ml-12 bg-teal-600 dark:bg-teal-700 text-white p-5 rounded-2xl shadow-sm relative">
                <h4 className="font-bold text-white text-sm mb-1">Public Transparency</h4>
                <p className="text-xs text-teal-100">Approved data is published to this dashboard for citizen visibility.</p>
              </div>
            </div>
            
          </div>
          
          <div className="mt-12 text-center">
            <button className="bg-white dark:bg-slate-900 border border-teal-200 dark:border-teal-800 text-teal-700 dark:text-teal-400 font-bold px-6 py-3 rounded-full hover:bg-teal-50 dark:hover:bg-teal-900/30 transition shadow-sm w-full">
              Explore Projects
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
