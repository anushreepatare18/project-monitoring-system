"use client";

import { useEffect, useState } from "react";
import { Search, Filter, Download } from "lucide-react";

export default function MinistryProjects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [sectorFilter, setSectorFilter] = useState("All");
  const [agencyFilter, setAgencyFilter] = useState("All");
  const [riskFilter, setRiskFilter] = useState("All");

  const MINISTRY_NAME = "Ministry_7";

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || \'http://localhost:8000\'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        const ministryProjects = data.filter((p: any) => p.ministry === MINISTRY_NAME);
        setProjects(ministryProjects);
        setLoading(false);
      });
  }, []);

  const sectors = ["All", ...Array.from(new Set(projects.map(p => p.sector)))];
  const agencies = ["All", ...Array.from(new Set(projects.map(p => p.implementing_agency)))];
  const risks = ["All", "Low", "Medium", "High", "Critical"];

  const filteredProjects = projects.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || p.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSector = sectorFilter === "All" || p.sector === sectorFilter;
    const matchesAgency = agencyFilter === "All" || p.implementing_agency === agencyFilter;
    const matchesRisk = riskFilter === "All" || p.risk_level === riskFilter;
    
    return matchesSearch && matchesSector && matchesAgency && matchesRisk;
  });

  const exportCSV = () => {
    const headers = ["Project ID", "Name", "Sector", "Agency", "Cost (Cr)", "Expenditure (Cr)", "Physical %", "Financial %", "Risk Level", "Status"];
    const rows = filteredProjects.map(p => [
      p.id, p.name, p.sector, p.implementing_agency, p.original_cost_cr, p.expenditure_cr, p.physical_progress_pct, p.financial_progress_pct, p.risk_level, p.status
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `ministry_portfolio_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight text-emerald-600 dark:text-emerald-500">Project Portfolio</h1>
          <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
            Browse and filter all projects under {MINISTRY_NAME}.
          </p>
        </div>
        <button onClick={exportCSV} className="flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg font-bold text-sm hover:bg-emerald-700 transition">
          <Download className="w-4 h-4 mr-2" /> Export CSV
        </button>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        {/* Filters */}
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex flex-wrap gap-4 items-center">
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
          
          <div className="flex gap-2 w-full sm:w-auto overflow-x-auto pb-1">
            <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-emerald-500" value={sectorFilter} onChange={e => setSectorFilter(e.target.value)}>
              {sectors.map(s => <option key={s} value={s}>{s === 'All' ? 'All Sectors' : s}</option>)}
            </select>
            <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-emerald-500" value={agencyFilter} onChange={e => setAgencyFilter(e.target.value)}>
              {agencies.map(a => <option key={a} value={a}>{a === 'All' ? 'All Agencies' : a}</option>)}
            </select>
            <select className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-emerald-500" value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
              {risks.map(r => <option key={r} value={r}>{r === 'All' ? 'All Risk Levels' : r}</option>)}
            </select>
          </div>
        </div>
        
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Project</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Agency</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Cost/Exp (Cr)</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Progress (Phy/Fin)</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Loading portfolio data...</td></tr>
              ) : filteredProjects.map(p => (
                <tr key={p.id} className="hover:bg-slate-50 transition cursor-pointer">
                  <td className="p-4">
                    <div className="font-bold text-sm text-slate-900 truncate max-w-[250px]">{p.name}</div>
                    <div className="text-xs text-slate-500 mt-1">{p.id} • {p.sector}</div>
                  </td>
                  <td className="p-4 text-sm text-slate-700">{p.implementing_agency}</td>
                  <td className="p-4 text-sm">
                    <div className="font-bold text-slate-900">₹{p.original_cost_cr?.toLocaleString()}</div>
                    <div className="text-xs text-slate-500 mt-0.5">Exp: ₹{p.expenditure_cr?.toLocaleString()}</div>
                  </td>
                  <td className="p-4">
                    <div className="w-32 mb-2">
                      <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-1">
                        <span>P: {p.physical_progress_pct}%</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${Math.min(100, p.physical_progress_pct)}%` }}></div>
                      </div>
                    </div>
                    <div className="w-32">
                      <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-1">
                        <span>F: {p.financial_progress_pct || 0}%</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500" style={{ width: `${Math.min(100, p.financial_progress_pct || 0)}%` }}></div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                     <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                      p.risk_level === 'Critical' ? 'bg-rose-100 text-rose-700' : 
                      p.risk_level === 'High' ? 'bg-orange-100 text-orange-700' :
                      p.risk_level === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {p.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
              {!loading && filteredProjects.length === 0 && (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">No projects match the selected filters.</td></tr>
              )}
            </tbody>
          </table>
          <div className="p-4 border-t border-slate-100 text-xs text-slate-500 text-center">
            Showing {filteredProjects.length} projects out of {projects.length} total.
          </div>
        </div>
      </div>
    </div>
  );
}
