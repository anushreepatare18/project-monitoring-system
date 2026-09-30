"use client";
import { Target } from "lucide-react";

export default function ProjectMonitoringPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Project Monitoring</h1>
        <p className="text-sm font-medium text-slate-500">
          Track the physical and financial progress of all your assigned projects.
        </p>
      </div>

      <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col items-center justify-center text-center mt-12 max-w-2xl mx-auto">
        <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-4">
          <Target className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Monitoring Workspace</h2>
        <p className="text-slate-500 text-sm mb-6">Select a project from the list below to view detailed progress updates, milestones, and funding releases.</p>
        
        <div className="w-full bg-slate-50 rounded-xl border border-slate-100 p-4 text-left">
          <p className="text-sm text-slate-400 italic text-center py-8">Select a project to load its monitoring details...</p>
        </div>
      </div>
    </div>
  );
}
