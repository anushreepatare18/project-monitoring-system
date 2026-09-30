"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { 
  ArrowLeft, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp,
  BarChart3,
  Calendar,
  IndianRupee,
  Activity,
  FileSearch,
  MessageSquare,
  ShieldCheck
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const API_URL = "https://project-monitoring-system-rykj.onrender.com/api";

export default function ProjectRiskDetail({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const { id } = resolvedParams;
  
  const [project, setProject] = useState<any>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [benchmark, setBenchmark] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [projRes, expRes, benchRes] = await Promise.all([
          fetch(`${API_URL}/projects/${id}`),
          fetch(`${API_URL}/projects/${id}/explanation`).catch(() => ({ ok: false })),
          fetch(`${API_URL}/projects/${id}/benchmark`).catch(() => ({ ok: false }))
        ]);
        
        if (projRes.ok) setProject(await projRes.json());
        if (expRes.ok) setExplanation(await expRes.json());
        if (benchRes.ok) setBenchmark(await benchRes.json());
      } catch (error) {
        console.error("Error fetching project details:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center space-x-2">
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
      </div>
    );
  }

  if (!project) {
    return <div className="p-12 text-center text-slate-500">Project not found.</div>;
  }

  // Parse SHAP data for chart
  const shapData = explanation?.shap_explanations?.map((item: any) => ({
    name: item.feature,
    impact: Math.abs(item.impact),
    originalImpact: item.impact,
    direction: item.impact > 0 ? "Risk Increasing" : "Risk Decreasing",
    fill: item.impact > 0 ? "#ef4444" : "#10b981" // red for increasing risk, green for decreasing
  })).sort((a: any, b: any) => b.impact - a.impact).slice(0, 5) || [];

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/dashboard/officer" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-900 mb-4 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Queue
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{project.name}</h1>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border
              ${project.risk_level === 'Critical' ? 'bg-red-50 text-red-700 border-red-200' : 
                project.risk_level === 'High' ? 'bg-orange-50 text-orange-700 border-orange-200' : 
                project.risk_level === 'Medium' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                'bg-green-50 text-green-700 border-green-200'}`}>
              {project.risk_level} Risk ({project.risk_score?.toFixed(1) || 0})
            </span>
            {project.is_anomalous && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200">
                Anomaly Flagged
              </span>
            )}
          </div>
          <div className="flex items-center text-sm text-slate-500 mt-2 gap-4">
            <span className="flex items-center"><Activity className="w-4 h-4 mr-1.5" /> ID: {project.id}</span>
            <span className="flex items-center"><BarChart3 className="w-4 h-4 mr-1.5" /> Sector: {project.sector}</span>
            <span className="flex items-center"><ShieldCheck className="w-4 h-4 mr-1.5" /> Agency: {project.implementing_agency}</span>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button className="bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 px-4 py-2 rounded-xl font-medium shadow-sm transition-all flex items-center">
            <MessageSquare className="w-4 h-4 mr-2" />
            Query Agency
          </button>
          <button className="bg-blue-600 text-white hover:bg-blue-700 px-6 py-2 rounded-xl font-medium shadow-sm shadow-blue-600/20 transition-all flex items-center">
            <CheckCircle className="w-4 h-4 mr-2" />
            Verify Alert
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Metrics & AI Insight */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* AI Insight Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-5">
              <TrendingUp className="w-24 h-24" />
            </div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4 flex items-center">
              <FileSearch className="w-4 h-4 mr-2" />
              AI Insight
            </h3>
            <p className="text-lg font-medium text-slate-800 leading-snug">
              "High probability of {project.delay_months > 0 ? 'schedule delay' : 'cost overrun'} driven by {shapData[0]?.name?.replace(/_/g, ' ').toLowerCase() || 'recent anomalies'}."
            </p>
            
            <div className="mt-6 pt-6 border-t border-slate-100">
              <h4 className="text-sm font-medium text-slate-700 mb-3">Key Risk Factors:</h4>
              <ul className="space-y-3">
                {shapData.slice(0,3).map((item: any, idx: number) => (
                  <li key={idx} className="flex items-start">
                    <AlertTriangle className={`w-4 h-4 mt-0.5 mr-2 flex-shrink-0 ${item.originalImpact > 0 ? 'text-red-500' : 'text-green-500'}`} />
                    <span className="text-sm text-slate-600">
                      <span className="font-medium text-slate-800">{item.name.replace(/_/g, ' ')}</span>
                      {item.originalImpact > 0 ? " is significantly increasing risk." : " is mitigating risk."}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-6 flex items-center">
              <BarChart3 className="w-4 h-4 mr-2" />
              Project Metrics
            </h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium text-slate-700 flex items-center"><IndianRupee className="w-3.5 h-3.5 mr-1 text-slate-400"/> Financial Progress</span>
                  <span className="font-bold text-slate-900">{project.expenditure_cr} / {project.original_cost_cr} Cr</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(100, (project.expenditure_cr / (project.original_cost_cr || 1)) * 100)}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium text-slate-700 flex items-center"><Activity className="w-3.5 h-3.5 mr-1 text-slate-400"/> Physical Progress</span>
                  <span className="font-bold text-slate-900">{project.physical_progress_pct}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${Math.min(100, project.physical_progress_pct)}%` }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium text-slate-700 flex items-center"><Calendar className="w-3.5 h-3.5 mr-1 text-slate-400"/> Schedule Variance</span>
                  <span className={`font-bold ${project.delay_months > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {project.delay_months > 0 ? `+${project.delay_months} Months` : 'On Track'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: SHAP Chart & Benchmarks */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Explainable AI (SHAP) Chart */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm h-[420px] flex flex-col">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-6 flex items-center">
              <TrendingUp className="w-4 h-4 mr-2" />
              Explainable AI (SHAP Value Contribution)
            </h3>
            <div className="flex-1 w-full relative">
              {shapData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={shapData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} stroke="#e2e8f0" />
                    <XAxis type="number" hide />
                    <YAxis 
                      dataKey="name" 
                      type="category" 
                      width={140}
                      tick={{ fill: '#64748b', fontSize: 12 }}
                      tickFormatter={(value) => value.replace(/_/g, ' ').substring(0, 18) + (value.length > 18 ? '...' : '')}
                    />
                    <Tooltip 
                      cursor={{fill: '#f8fafc'}}
                      contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value: any, name: any, props: any) => [
                        `${Number(props.payload.originalImpact).toFixed(4)}`, 
                        "Impact"
                      ]}
                    />
                    <Bar dataKey="impact" radius={[0, 4, 4, 0]} barSize={32}>
                      {shapData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center text-slate-400">
                  No SHAP explanation data available.
                </div>
              )}
            </div>
            <div className="mt-4 flex justify-center space-x-6 text-xs text-slate-500">
              <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-red-500 mr-2"></span> Increases Risk</div>
              <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-green-500 mr-2"></span> Decreases Risk</div>
            </div>
          </div>

          {/* Benchmark Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-6 flex items-center">
              <Activity className="w-4 h-4 mr-2" />
              Peer Benchmarking
            </h3>
            
            {benchmark ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-slate-500 mb-2">Cost Overrun Percentile</p>
                  <div className="flex items-end gap-3">
                    <span className="text-3xl font-bold text-slate-800">{benchmark.cost_overrun_percentile?.toFixed(0)}<span className="text-lg text-slate-500 font-normal">th</span></span>
                    <span className="text-sm text-slate-500 mb-1">among {benchmark.peer_count} peers</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5 mt-3">
                    <div className="bg-orange-500 h-1.5 rounded-full" style={{ width: `${benchmark.cost_overrun_percentile || 0}%` }}></div>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-slate-500 mb-2">Schedule Delay Percentile</p>
                  <div className="flex items-end gap-3">
                    <span className="text-3xl font-bold text-slate-800">{benchmark.delay_percentile?.toFixed(0)}<span className="text-lg text-slate-500 font-normal">th</span></span>
                    <span className="text-sm text-slate-500 mb-1">among {benchmark.peer_count} peers</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5 mt-3">
                    <div className="bg-red-500 h-1.5 rounded-full" style={{ width: `${benchmark.delay_percentile || 0}%` }}></div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-4 text-center text-slate-400">Benchmark data not available for this sector.</div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
