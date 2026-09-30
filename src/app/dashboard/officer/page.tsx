"use client";

import { Target, ShieldAlert, AlertTriangle, CheckCircle, MessageSquare } from "lucide-react";

export default function OfficerDashboard() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)]">
      
      <div className="mb-8">
        <h1 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-emerald-500 to-indigo-600 mb-2">
          Monitoring Officer Dashboard
        </h1>
        <p className="text-sm font-medium text-slate-500">
          Review AI risk anomalies, investigate project delays, and resolve field alerts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        
        {/* Card 1 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center mb-6">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">2111</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Total Monitored</p>
          </div>
        </div>

        {/* Card 2 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="w-10 h-10 rounded-full bg-red-50 text-red-500 flex items-center justify-center mb-6">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">107</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Critical Risk</p>
          </div>
        </div>

        {/* Card 3 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="w-10 h-10 rounded-full bg-orange-50 text-orange-500 flex items-center justify-center mb-6">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">0</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">High Risk</p>
          </div>
        </div>

        {/* Card 4 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center mb-6">
            <CheckCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">1977</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Projects On Track</p>
          </div>
        </div>

      </div>

      {/* Alert Queue Overview */}
      <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex items-center justify-between">
        <div className="max-w-2xl pr-8">
          <h3 className="text-sm font-bold text-slate-900 mb-2">Alert Queue Overview</h3>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            You have <strong className="text-slate-800">0 new anomalies</strong> detected by the PRAGYA AI engine that require triage. There are <strong className="text-slate-800">0 alerts</strong> where implementing agencies have provided responses needing your final review.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-amber-50 text-amber-600 border border-amber-100 px-6 py-4 rounded-2xl flex flex-col items-center justify-center min-w-[120px]">
            <span className="text-2xl font-black">0</span>
            <span className="text-[9px] font-bold uppercase tracking-widest mt-1">Action Req.</span>
          </div>
          <div className="bg-slate-50 text-slate-500 border border-slate-200 px-6 py-4 rounded-2xl flex flex-col items-center justify-center min-w-[120px]">
            <span className="text-2xl font-black">0</span>
            <span className="text-[9px] font-bold uppercase tracking-widest mt-1">In Progress</span>
          </div>
        </div>
      </div>

      {/* Floating Chat Button */}
      <div className="fixed bottom-8 right-8 z-50">
        <button className="w-14 h-14 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full shadow-lg shadow-emerald-600/30 flex items-center justify-center transition-transform hover:scale-105 active:scale-95">
          <MessageSquare className="w-6 h-6" />
          <div className="absolute top-0 right-0 w-3 h-3 bg-white rounded-full border-2 border-emerald-600"></div>
        </button>
      </div>

    </div>
  );
}
