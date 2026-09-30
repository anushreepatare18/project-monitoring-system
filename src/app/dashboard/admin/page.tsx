"use client";

import { Shield, Users, Database, Server, Activity, ArrowUpRight } from "lucide-react";

export default function AdminDashboard() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      
      <div className="mb-8">
        <h1 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 mb-2">
          System Administration
        </h1>
        <p className="text-sm font-medium text-slate-500">
          Manage users, view system health, and monitor AI model performance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {/* Card 1 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center mb-6">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">142</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Active Users</p>
          </div>
        </div>

        {/* Card 2 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center mb-6">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">99.9%</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">System Uptime</p>
          </div>
        </div>

        {/* Card 3 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center mb-6">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">8.4<span className="text-lg">TB</span></h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Data Indexed</p>
          </div>
        </div>

        {/* Card 4 */}
        <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between">
          <div className="w-10 h-10 rounded-full bg-purple-50 text-purple-500 flex items-center justify-center mb-6">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">v1.2</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">AI Model Version</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
          <div className="flex items-center gap-2 mb-6">
            <Shield className="w-5 h-5 text-slate-700" />
            <h2 className="text-lg font-black text-slate-900">Recent Audit Logs</h2>
          </div>
          
          <div className="space-y-4">
            {[
              { action: "User Login", actor: "officer_01", time: "2 mins ago" },
              { action: "Model Updated", actor: "system", time: "1 hour ago" },
              { action: "Project Flagged", actor: "AI_Agent", time: "3 hours ago" },
              { action: "User Created", actor: "admin", time: "1 day ago" }
            ].map((log, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-slate-800">{log.action}</span>
                  <span className="text-xs text-slate-500">by {log.actor}</span>
                </div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{log.time}</span>
              </div>
            ))}
          </div>
          
          <button className="w-full mt-6 py-3 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors flex items-center justify-center gap-2">
            View Full Audit Trail <ArrowUpRight className="w-3 h-3" />
          </button>
        </div>
      </div>

    </div>
  );
}
