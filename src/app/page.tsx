"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  BarChart3,
  FileText,
  Activity,
  ArrowRight
} from "lucide-react";

const API_URL = "https://project-monitoring-system-rykj.onrender.com/api";

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/portfolio/summary`),
      fetch(`${API_URL}/projects`)
    ])
      .then(async ([resSummary, resProjects]) => {
        if (!resSummary.ok || !resProjects.ok) {
          throw new Error("Failed to fetch data");
        }
        setSummary(await resSummary.json());
        const projData = await resProjects.json();
        setProjects(projData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50/50">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-emerald-700 font-medium animate-pulse">Loading AI Insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-300/20 rounded-full blur-[120px] pointer-events-none animate-slow-zoom"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-300/20 rounded-full blur-[150px] pointer-events-none animate-slow-zoom" style={{ animationDelay: '1s' }}></div>

      <nav className="glass-panel mx-6 mt-6 px-8 py-4 flex justify-between items-center z-10 relative animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-br from-emerald-500 to-indigo-600 p-2 rounded-xl shadow-lg">
            <Activity className="w-6 h-6 text-white animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">
            PRAGYA <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-indigo-600">AI</span>
            <span className="text-sm font-medium text-slate-500 ml-3 tracking-wide uppercase">Project Monitoring System</span>
          </h1>
        </div>
        <div className="flex space-x-6">
          <Link href="/projects" className="text-sm font-semibold text-slate-600 hover:text-emerald-600 transition-colors">Projects</Link>
          <Link href="/alerts" className="text-sm font-semibold text-slate-600 hover:text-emerald-600 transition-colors">Alerts</Link>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-10 relative z-10">
        <div className="flex justify-between items-end mb-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <div>
            <h2 className="text-3xl font-extrabold text-slate-800 mb-1">Portfolio Overview</h2>
            <p className="text-slate-500">Real-time AI analysis of nationwide infrastructure projects</p>
          </div>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          {[
            { label: 'Total Projects', value: summary?.total_projects || 0, icon: FileText, color: 'text-blue-600', bg: 'bg-blue-100', delay: '0.3s' },
            { label: 'Total Approved Cost', value: `₹${(summary?.total_cost || 0).toLocaleString()} Cr`, icon: BarChart3, color: 'text-emerald-600', bg: 'bg-emerald-100', delay: '0.4s' },
            { label: 'Critical Risk Projects', value: summary?.risk_distribution?.Critical || 0, icon: AlertTriangle, color: 'text-rose-600', bg: 'bg-rose-100', delay: '0.5s' },
            { label: 'High Risk Projects', value: summary?.risk_distribution?.High || 0, icon: Clock, color: 'text-amber-500', bg: 'bg-amber-100', delay: '0.6s' }
          ].map((stat, idx) => (
            <div key={idx} className="glass-panel glass-panel-hover p-6 flex flex-col justify-between animate-fade-in-up" style={{ animationDelay: stat.delay }}>
              <div className="flex justify-between items-start mb-4">
                <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">{stat.label}</span>
                <div className={`${stat.bg} p-2 rounded-xl`}>
                  <stat.icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
              <span className="text-4xl font-extrabold text-slate-800 tracking-tight">{stat.value}</span>
            </div>
          ))}
        </div>

        {/* Project List */}
        <div className="flex justify-between items-end mb-6 animate-fade-in-up" style={{ animationDelay: '0.7s' }}>
          <h2 className="text-2xl font-bold text-slate-800">Tracked Projects</h2>
          <Link href="/projects" className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center group">
            View All <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
        
        <div className="glass-panel overflow-hidden animate-fade-in-up" style={{ animationDelay: '0.8s' }}>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50/50 backdrop-blur-md border-b border-slate-200/50">
                <tr>
                  <th className="px-8 py-5 text-xs font-bold text-slate-500 uppercase tracking-wider">Project Name</th>
                  <th className="px-8 py-5 text-xs font-bold text-slate-500 uppercase tracking-wider">Agency</th>
                  <th className="px-8 py-5 text-xs font-bold text-slate-500 uppercase tracking-wider">Progress</th>
                  <th className="px-8 py-5 text-xs font-bold text-slate-500 uppercase tracking-wider">Cost (Cr)</th>
                  <th className="px-8 py-5 text-xs font-bold text-slate-500 uppercase tracking-wider">AI Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100/50">
                {projects.slice(0, 10).map((project, idx) => (
                  <tr key={project.id} className="table-row-hover group">
                    <td className="px-8 py-5">
                      <div className="font-bold text-slate-800 group-hover:text-emerald-700 transition-colors">{project.name}</div>
                      <div className="text-xs font-medium text-slate-400 mt-1">{project.sector}</div>
                    </td>
                    <td className="px-8 py-5 text-sm font-medium text-slate-600">{project.implementing_agency}</td>
                    <td className="px-8 py-5 text-sm font-medium text-slate-600">
                      <div className="flex items-center space-x-3">
                        <div className="w-full bg-slate-100 rounded-full h-2.5 max-w-[120px] shadow-inner overflow-hidden">
                          <div 
                            className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full relative" 
                            style={{ width: `${Math.min(100, project.physical_progress_pct)}%` }}
                          >
                            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                          </div>
                        </div>
                        <span className="font-bold text-slate-700">{project.physical_progress_pct}%</span>
                      </div>
                    </td>
                    <td className="px-8 py-5 text-sm font-bold text-slate-700">₹{project.original_cost_cr.toLocaleString()}</td>
                    <td className="px-8 py-5">
                      <span className={`px-4 py-1.5 rounded-full text-xs font-bold shadow-sm ${
                        project.risk_level === 'Critical' ? 'bg-rose-100/80 text-rose-700 border border-rose-200' :
                        project.risk_level === 'High' ? 'bg-amber-100/80 text-amber-700 border border-amber-200' :
                        project.risk_level === 'Medium' ? 'bg-yellow-100/80 text-yellow-700 border border-yellow-200' :
                        'bg-emerald-100/80 text-emerald-700 border border-emerald-200'
                      }`}>
                        {project.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {projects.length === 0 && (
            <div className="p-12 text-center text-slate-500 font-medium flex flex-col items-center">
              <Activity className="w-12 h-12 mb-4 text-slate-300 animate-pulse" />
              Waiting for AI models to synchronize project data...
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
