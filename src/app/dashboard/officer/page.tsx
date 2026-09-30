"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  AlertTriangle, 
  Clock, 
  CheckCircle,
  FileSearch,
  ArrowRight,
  Filter
} from "lucide-react";

const API_URL = "https://project-monitoring-system-rykj.onrender.com/api";

export default function OfficerDashboard() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const res = await fetch(`${API_URL}/alerts`);
        if (res.ok) {
          const data = await res.json();
          data.sort((a: any, b: any) => b.risk_score - a.risk_score);
          setAlerts(data);
        }
      } catch (error) {
        console.error("Error fetching alerts:", error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchAlerts();
  }, []);

  const openAlerts = alerts.filter(a => a.status === 'Open').length;
  const criticalAlerts = alerts.filter(a => a.risk_score > 75 && a.status === 'Open').length;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Monitoring Officer Dashboard</h1>
        <p className="text-slate-500 mt-1">Prioritized alert queue and portfolio health.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-slate-500">Open Alerts</span>
            <div className="p-2 bg-blue-50 rounded-lg">
              <FileSearch className="text-blue-600 w-5 h-5" />
            </div>
          </div>
          <span className="text-4xl font-bold text-slate-800 mt-4 tracking-tight">{openAlerts}</span>
        </div>
        
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-slate-500">Critical Risks</span>
            <div className="p-2 bg-red-50 rounded-lg">
              <AlertTriangle className="text-red-600 w-5 h-5" />
            </div>
          </div>
          <span className="text-4xl font-bold text-red-600 mt-4 tracking-tight">{criticalAlerts}</span>
        </div>
        
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-slate-500">Average Age</span>
            <div className="p-2 bg-orange-50 rounded-lg">
              <Clock className="text-orange-600 w-5 h-5" />
            </div>
          </div>
          <span className="text-4xl font-bold text-slate-800 mt-4 tracking-tight">2.4 <span className="text-xl font-normal text-slate-500 tracking-normal">days</span></span>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-slate-500">Confirmed Rate</span>
            <div className="p-2 bg-green-50 rounded-lg">
              <CheckCircle className="text-green-600 w-5 h-5" />
            </div>
          </div>
          <span className="text-4xl font-bold text-slate-800 mt-4 tracking-tight">84<span className="text-xl font-normal text-slate-500 tracking-normal">%</span></span>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
        <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <h2 className="text-lg font-bold text-slate-800">Prioritized Alert Queue</h2>
          <button className="flex items-center text-sm font-medium text-slate-600 hover:text-slate-900 bg-white border border-slate-200 shadow-sm px-3 py-1.5 rounded-lg transition-colors hover:bg-slate-50">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
        </div>
        
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 flex justify-center items-center space-x-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              No alerts found. Your queue is clear!
            </div>
          ) : (
            <table className="w-full text-left">
              <thead className="bg-white border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Project</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">AI Insight</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Risk Score</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-slate-50/80 transition-colors group cursor-pointer">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900">{alert.project_name || "Unknown"}</div>
                      <div className="text-xs text-slate-500 font-mono mt-0.5">{alert.project_id}</div>
                    </td>
                    <td className="px-6 py-4 max-w-[300px]">
                      <div className="text-sm font-medium text-slate-800 truncate">{alert.message}</div>
                      <div className="text-xs text-slate-500 mt-1 line-clamp-1">Triggered by recent update anomaly</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-full text-xs font-bold
                          ${alert.risk_score >= 80 ? 'bg-red-50 text-red-700 ring-1 ring-red-600/20' : 
                            alert.risk_score >= 60 ? 'bg-orange-50 text-orange-700 ring-1 ring-orange-600/20' : 
                            'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-600/20'}`}>
                          {alert.risk_score.toFixed(1)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border
                        ${alert.status === 'Open' ? 'bg-blue-50 border-blue-200 text-blue-700' : 
                          alert.status === 'Verified' ? 'bg-green-50 border-green-200 text-green-700' : 
                          'bg-slate-50 border-slate-200 text-slate-700'}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link 
                        href={`/dashboard/officer/projects/${alert.project_id}`}
                        className="inline-flex items-center justify-center p-2 text-blue-600 opacity-0 group-hover:opacity-100 group-hover:bg-blue-50 rounded-lg transition-all"
                      >
                        <span className="sr-only">Review</span>
                        <ArrowRight className="w-5 h-5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
