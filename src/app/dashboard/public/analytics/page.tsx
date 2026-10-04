"use client";

import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from "recharts";

const sectorData = [
  { name: "Road Transport & Highways", value: 58, fill: "#f59e0b" },
  { name: "Housing & Urban Affairs", value: 3, fill: "#3b82f6" },
  { name: "Water Resources", value: 3, fill: "#8b5cf6" },
  { name: "Petroleum & Natural Gas", value: 6, fill: "#06b6d4" },
  { name: "Health", value: 2, fill: "#10b981" },
  { name: "Infrastructure", value: 10, fill: "#ef4444" },
  { name: "Railways", value: 6, fill: "#f97316" },
  { name: "Power", value: 5, fill: "#84cc16" },
  { name: "Coal", value: 6, fill: "#3b82f6" },
  { name: "Telecommunications", value: 1, fill: "#6366f1" },
  { name: "Mines", value: 0, fill: "#8b5cf6" },
  { name: "Education", value: 1, fill: "#14b8a6" },
  { name: "Steel", value: 1, fill: "#f43f5e" },
  { name: "Aviation", value: 1, fill: "#d946ef" },
];

const statusData = [
  { name: "On Track", value: 93, fill: "#10b981" },
  { name: "Completed", value: 7, fill: "#64748b" },
];

const costData = [
  { name: "A", value: 400000 },
  { name: "B", value: 500000 },
  { name: "C", value: 300000 },
  { name: "D", value: 200000 },
  { name: "E", value: 600000 },
  { name: "F", value: 100000 },
];

const progressData = [
  { name: "0-20", value: 50 },
  { name: "20-40", value: 100 },
  { name: "40-60", value: 250 },
  { name: "60-80", value: 400 },
  { name: "80-100", value: 950 },
];

export default function PublicAnalytics() {
  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold text-teal-600 dark:text-teal-500 tracking-tight">Public Analytics</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Visualized summaries of published infrastructure projects across the nation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Projects by Sector */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col min-h-[400px]">
          <h3 className="font-bold text-slate-900 dark:text-white mb-6">Projects by Sector</h3>
          <div className="flex-1 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={true}
                >
                  {sectorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number, name: string) => [`${value}%`, name]}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Execution Status */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col min-h-[400px]">
          <h3 className="font-bold text-slate-900 dark:text-white mb-6">Execution Status</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={110}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={true}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number, name: string) => [`${value}%`, name]}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="square" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Approved Cost by Sector */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col min-h-[400px]">
          <h3 className="font-bold text-slate-900 dark:text-white mb-6">Approved Cost by Sector (Cr)</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={costData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Physical Progress Distribution */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col min-h-[400px]">
          <h3 className="font-bold text-slate-900 dark:text-white mb-6">Physical Progress Distribution</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={progressData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
