"use client";

import { useEffect, useState } from "react";
import { Search, Filter, ChevronRight, CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";

export default function AdminProjects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [sectorFilter, setSectorFilter] = useState("All");
  const [riskFilter, setRiskFilter] = useState("All");
  
  const [selectedProject, setSelectedProject] = useState<any | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/projects")
      .then(res => res.json())
      .then(data => {
        setProjects(data);
        setLoading(false);
      });
  }, []);

  const sectors = ["All", ...Array.from(new Set(projects.map(p => p.sector)))];
  const risks = ["All", "Low", "Medium", "High", "Critical"];

  const filteredProjects = projects.filter(p => {
    const matchesSearch = p.name?.toLowerCase().includes(searchQuery.toLowerCase()) || p.id?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSector = sectorFilter === "All" || p.sector === sectorFilter;
    const matchesRisk = riskFilter === "All" || p.risk_level === riskFilter;
    
    return matchesSearch && matchesSector && matchesRisk;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-500 tracking-tight">All Projects</h1>
        <p className="text-slate-500 font-medium mt-1">
          Monitor and manage all system projects as Admin.
        </p>
      </div>

      <div className="flex gap-6 relative">
        <div className={`transition-all duration-300 ${selectedProject ? 'w-2/3 hidden md:block' : 'w-full'}`}>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex flex-wrap gap-4 items-center">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input 
                  type="text"
                  placeholder="Search ID or Name..."
                  className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                />
              </div>
              
              <div className="flex gap-2 w-full sm:w-auto">
                <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white" value={sectorFilter} onChange={e => setSectorFilter(e.target.value)}>
                  {sectors.map(s => <option key={s as string} value={s as string}>{s === 'All' ? 'All Sectors' : s}</option>)}
                </select>
                <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white" value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
                  {risks.map(r => <option key={r} value={r}>{r === 'All' ? 'All Risks' : r}</option>)}
                </select>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100">
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Ministry</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Cost (Cr)</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Progress</th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Risk Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr><td colSpan={5} className="p-8 text-center text-slate-500">Loading projects...</td></tr>
                  ) : filteredProjects.map(p => (
                    <tr 
                      key={p.id} 
                      className={`hover:bg-slate-50 transition cursor-pointer ${selectedProject?.id === p.id ? 'bg-emerald-50 border-l-4 border-emerald-500' : 'border-l-4 border-transparent'}`}
                      onClick={() => setSelectedProject(p)}
                    >
                      <td className="p-4">
                        <div className="font-bold text-sm text-slate-900 truncate max-w-[200px]">{p.name}</div>
                        <div className="text-xs text-slate-500 mt-1">{p.id} • {p.sector}</div>
                      </td>
                      <td className="p-4 text-sm text-slate-700">{p.ministry}</td>
                      <td className="p-4 text-sm font-bold">₹{p.original_cost_cr?.toLocaleString()}</td>
                      <td className="p-4">
                        <div className="text-[10px] font-bold text-slate-500 mb-1">Phy: {p.physical_progress_pct}%</div>
                        <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500" style={{ width: `${Math.min(100, p.physical_progress_pct)}%` }}></div>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                          p.risk_level === 'Critical' ? 'bg-rose-100 text-rose-700' : 
                          p.risk_level === 'High' ? 'bg-orange-100 text-orange-700' :
                          'bg-emerald-100 text-emerald-700'
                        }`}>
                          {p.risk_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {!loading && filteredProjects.length === 0 && (
                    <tr><td colSpan={5} className="p-8 text-center text-slate-500">No projects match filters.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Project Details Panel */}
        {selectedProject && (
          <div className="w-full md:w-1/3 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[calc(100vh-140px)] sticky top-24">
            <div className="p-4 border-b border-slate-100 bg-emerald-600 text-white flex justify-between items-center">
              <h3 className="font-bold text-sm truncate pr-4">{selectedProject.name}</h3>
              <button onClick={() => setSelectedProject(null)} className="text-emerald-200 hover:text-white transition text-xs font-bold uppercase">Close</button>
            </div>
            <div className="p-5 flex-1 overflow-y-auto space-y-6">
              
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Project Overview</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div><span className="text-slate-500 block text-xs">ID</span><span className="font-medium text-slate-900">{selectedProject.id}</span></div>
                  <div><span className="text-slate-500 block text-xs">Sector</span><span className="font-medium text-slate-900">{selectedProject.sector}</span></div>
                  <div><span className="text-slate-500 block text-xs">Ministry</span><span className="font-medium text-slate-900">{selectedProject.ministry}</span></div>
                  <div><span className="text-slate-500 block text-xs">State</span><span className="font-medium text-slate-900">{selectedProject.state}</span></div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Financials & Progress</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-100 pb-2 text-sm">
                    <span className="text-slate-500">Approved Cost</span>
                    <span className="font-bold text-slate-900">₹{selectedProject.original_cost_cr} Cr</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-slate-100 pb-2 text-sm">
                    <span className="text-slate-500">Expenditure</span>
                    <span className="font-bold text-blue-600">₹{selectedProject.expenditure_cr} Cr</span>
                  </div>
                  <div className="pt-2">
                    <div className="flex justify-between text-xs mb-1 font-bold text-slate-600"><span>Physical Progress</span><span>{selectedProject.physical_progress_pct}%</span></div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden mb-3"><div className="h-full bg-blue-500" style={{ width: `${selectedProject.physical_progress_pct}%` }}></div></div>
                    
                    <div className="flex justify-between text-xs mb-1 font-bold text-slate-600"><span>Financial Progress</span><span>{selectedProject.financial_progress_pct || 0}%</span></div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-indigo-500" style={{ width: `${selectedProject.financial_progress_pct || 0}%` }}></div></div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-sm">
                <div className="flex items-center text-slate-700 font-bold mb-2">
                  <ShieldAlert className="w-4 h-4 mr-2 text-orange-500" /> Current Risk Level
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600">System assessment:</span>
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${selectedProject.risk_level === 'Critical' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                    {selectedProject.risk_level}
                  </span>
                </div>
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}
