"use client";

import { useEffect, useState } from "react";
import { Search, Info, BarChart2 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ZAxis } from "recharts";

export default function OfficerBenchmarking() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSector, setSelectedSector] = useState("All");

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        setProjects(data);
        setLoading(false);
      });
  }, []);

  const sectors = ["All", ...Array.from(new Set(projects.map(p => p.sector)))];
  
  const filteredProjects = selectedSector === "All" 
    ? projects 
    : projects.filter(p => p.sector === selectedSector);

  // Scatter data: Cost vs Physical Progress
  const scatterData = filteredProjects.map(p => ({
    name: p.name,
    cost: p.original_cost_cr || 0,
    progress: p.physical_progress_pct || 0,
    risk: p.risk_level
  }));

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-indigo-600">Project Benchmarking</h1>
        <p className="text-slate-500 font-medium mt-1">
          Compare projects within your authorized scope using available metrics.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl flex items-start text-sm text-blue-800">
        <Info className="w-5 h-5 mr-3 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Benchmarking Notice:</span> Comparisons are descriptive and depend on available sample data. 
          Correlation does not establish causation.
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="font-bold text-slate-900 flex items-center"><BarChart2 className="w-5 h-5 mr-2 text-indigo-500"/> Progress vs. Approved Cost Distribution</h3>
          <select 
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:ring-2 focus:ring-indigo-500" 
            value={selectedSector} 
            onChange={e => setSelectedSector(e.target.value)}
          >
            {sectors.map(s => <option key={s as string} value={s as string}>{s === 'All' ? 'All Sectors' : s}</option>)}
          </select>
        </div>
        
        {loading ? (
          <div className="h-80 flex items-center justify-center text-slate-400">Loading benchmark data...</div>
        ) : (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis type="number" dataKey="progress" name="Physical Progress (%)" unit="%" tick={{fontSize: 12}} />
                <YAxis type="number" dataKey="cost" name="Cost (Cr)" unit="Cr" tick={{fontSize: 12}} />
                <ZAxis type="category" dataKey="name" name="Project" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Projects" data={scatterData} fill="#4f46e5" fillOpacity={0.6} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

    </div>
  );
}
