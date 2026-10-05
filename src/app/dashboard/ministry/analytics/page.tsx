"use client";

import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from "recharts";

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
const RISK_COLORS = { 'Low': '#10b981', 'Medium': '#f59e0b', 'High': '#f97316', 'Critical': '#ef4444' };

export default function MinistryAnalytics() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
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

  if (loading) return <div className="p-8 text-center text-slate-500">Loading analytics...</div>;

  // Compute Data for Charts
  // 1. Sector Distribution
  const sectorMap: any = {};
  projects.forEach(p => {
    sectorMap[p.sector] = (sectorMap[p.sector] || 0) + 1;
  });
  const sectorData = Object.keys(sectorMap).map(k => ({ name: k, value: sectorMap[k] }));

  // 2. Risk Distribution
  const riskMap: any = { 'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0 };
  projects.forEach(p => {
    if (riskMap[p.risk_level] !== undefined) {
      riskMap[p.risk_level]++;
    }
  });
  const riskData = Object.keys(riskMap).map(k => ({ name: k, value: riskMap[k] }));

  // 3. Cost vs Expenditure by Sector
  const costExpMap: any = {};
  projects.forEach(p => {
    if (!costExpMap[p.sector]) costExpMap[p.sector] = { name: p.sector, ApprovedCost: 0, Expenditure: 0 };
    costExpMap[p.sector].ApprovedCost += (p.original_cost_cr || 0);
    costExpMap[p.sector].Expenditure += (p.expenditure_cr || 0);
  });
  const costExpData = Object.values(costExpMap);

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Portfolio Analytics</h1>
        <p className="text-slate-500 font-medium mt-1">Visualize distribution, risk, and financial tracking for {MINISTRY_NAME}.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Risk Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(RISK_COLORS as any)[entry.name] || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Projects by Sector</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sectorData} cx="50%" cy="50%" innerRadius={0} outerRadius={80} dataKey="value" label>
                  {sectorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Cost vs Expenditure */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 mb-4">Cost vs Expenditure by Sector (Cr)</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={costExpData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{fontSize: 12}} />
              <YAxis tick={{fontSize: 12}} />
              <Tooltip cursor={{fill: '#f8fafc'}} />
              <Legend />
              <Bar dataKey="ApprovedCost" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Expenditure" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="text-center text-xs text-slate-400 font-medium pb-8">
        Note: The analytics provided above are for demonstration purposes based on prototype dataset and rule-based insights.
      </div>
    </div>
  );
}
