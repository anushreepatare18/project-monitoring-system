"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  BarChart3,
  FileText
} from "lucide-react";

const API_URL = "https://project-monitoring-system-rykj.onrender.com/api";

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [summaryRes, projectsRes] = await Promise.all([
          fetch(`${API_URL}/portfolio/summary`),
          fetch(`${API_URL}/projects`)
        ]);
        
        if (summaryRes.ok) setSummary(await summaryRes.json());
        if (projectsRes.ok) setProjects(await projectsRes.json());
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }
    
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <nav className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-2">
          <TrendingUp className="text-blue-600 w-6 h-6" />
          <h1 className="text-xl font-bold text-slate-800">PRAGYA AI <span className="text-sm font-normal text-slate-500 ml-2">Project Monitoring System</span></h1>
        </div>
        <div className="flex space-x-4">
          <Link href="/" className="text-sm font-medium text-slate-600 hover:text-blue-600 transition">Landing Page</Link>
          <Link href="/projects" className="text-sm font-medium text-slate-600 hover:text-blue-600 transition">Projects</Link>
          <Link href="/alerts" className="text-sm font-medium text-slate-600 hover:text-blue-600 transition">Alerts</Link>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-800">Portfolio Overview</h2>
          <span className="px-3 py-1 bg-slate-800 text-white rounded-full text-xs font-bold tracking-wider">ADMIN VIEW</span>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
            <span className="text-sm font-medium text-slate-500 mb-2">Total Projects</span>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-slate-800">{summary?.total_projects || 0}</span>
              <FileText className="text-blue-500 w-8 h-8 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
            <span className="text-sm font-medium text-slate-500 mb-2">Total Approved Cost</span>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-slate-800">₹{(summary?.total_cost || 0).toLocaleString()} Cr</span>
              <BarChart3 className="text-green-500 w-8 h-8 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
            <span className="text-sm font-medium text-slate-500 mb-2">Critical Risk Projects</span>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-red-600">{summary?.risk_distribution?.Critical || 0}</span>
              <AlertTriangle className="text-red-500 w-8 h-8 opacity-20" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
            <span className="text-sm font-medium text-slate-500 mb-2">High Risk Projects</span>
            <div className="flex items-center justify-between">
              <span className="text-3xl font-bold text-orange-500">{summary?.risk_distribution?.High || 0}</span>
              <Clock className="text-orange-500 w-8 h-8 opacity-20" />
            </div>
          </div>
        </div>

        {/* Project List */}
        <h2 className="text-xl font-bold text-slate-800 mb-4">Tracked Projects</h2>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Project Name</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Agency</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Progress</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">Cost (Cr)</th>
                <th className="px-6 py-4 text-sm font-semibold text-slate-600">AI Risk Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {projects.slice(0, 10).map((project) => (
                <tr key={project.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-800">{project.name}</div>
                    <div className="text-xs text-slate-500">{project.sector}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{project.implementing_agency}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    <div className="flex items-center space-x-2">
                      <div className="w-full bg-slate-200 rounded-full h-2 max-w-[100px]">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${Math.min(100, project.physical_progress_pct)}%` }}></div>
                      </div>
                      <span>{project.physical_progress_pct}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">₹{project.original_cost_cr.toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      project.risk_level === 'Critical' ? 'bg-red-100 text-red-700' :
                      project.risk_level === 'High' ? 'bg-orange-100 text-orange-700' :
                      project.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {project.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {projects.length === 0 && (
            <div className="p-8 text-center text-slate-500">No projects found. Check database connection.</div>
          )}
        </div>
      </main>
    </div>
  );
}
