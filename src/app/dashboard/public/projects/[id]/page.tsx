"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FolderKanban, Activity, MapPin, Building2, CheckCircle2, Building, ArrowLeft } from "lucide-react";

export default function PublicProjectDetails({ params }: { params: { id: string } }) {
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/public/projects/${params.id}`)
      .then(res => res.json())
      .then(data => {
        setProject(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load project", err);
        setLoading(false);
      });
  }, [params.id]);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading project details...</div>;
  }

  if (!project || project.detail === "Project not found") {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <Link href="/dashboard/public/projects" className="inline-flex items-center text-sm font-semibold text-slate-500 hover:text-slate-900 transition">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Directory
        </Link>
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm">
          <div className="text-xl font-bold text-slate-900">Project Not Found</div>
          <p className="text-slate-500 mt-2">The requested project may not exist or is not approved for public visibility.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Link href="/dashboard/public/projects" className="inline-flex items-center text-sm font-semibold text-slate-500 hover:text-slate-900 transition mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Directory
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest bg-emerald-100 text-emerald-700">
                {project.status || "Ongoing"}
              </span>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{project.project_id}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {project.project_name}
            </h1>
          </div>
        </div>
      </div>

      {/* Key Info Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-start">
          <Building className="w-8 h-8 text-blue-500 mr-4 shrink-0 bg-blue-50 p-1.5 rounded-lg" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Sector</div>
            <div className="font-bold text-slate-900 text-sm leading-tight">{project.sector || "N/A"}</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-start">
          <Building2 className="w-8 h-8 text-indigo-500 mr-4 shrink-0 bg-indigo-50 p-1.5 rounded-lg" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Ministry / Dept</div>
            <div className="font-bold text-slate-900 text-sm leading-tight">{project.ministry || "N/A"}</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-start">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mr-4 shrink-0 bg-emerald-50 p-1.5 rounded-lg" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Executing Agency</div>
            <div className="font-bold text-slate-900 text-sm leading-tight">{project.agency || "N/A"}</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-start">
          <MapPin className="w-8 h-8 text-rose-500 mr-4 shrink-0 bg-rose-50 p-1.5 rounded-lg" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Location</div>
            <div className="font-bold text-slate-900 text-sm leading-tight">{project.state || "Not available"}</div>
          </div>
        </div>
      </div>

      {/* Financial & Physical Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex items-center">
              <FolderKanban className="w-5 h-5 text-slate-400 mr-2" />
              <h2 className="font-bold text-slate-900 text-lg">Project Progress</h2>
            </div>
            <div className="p-6 space-y-8">
              <div>
                <div className="flex justify-between items-end mb-2">
                  <div className="text-sm font-bold text-slate-700">Physical Progress</div>
                  <div className="text-2xl font-black text-emerald-600">{project.physical_progress || 0}%</div>
                </div>
                <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${Math.min(100, project.physical_progress || 0)}%` }}></div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Approved Cost</div>
                  <div className="text-xl font-black text-slate-900">₹{project.approved_cost?.toLocaleString() || "N/A"} Cr</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Expenditure</div>
                  <div className="text-xl font-black text-slate-900">₹{project.expenditure?.toLocaleString() || "N/A"} Cr</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 p-5 rounded-2xl shadow-sm text-sm text-blue-900">
            <h3 className="font-bold flex items-center mb-2 text-blue-800">
              <CheckCircle2 className="w-4 h-4 mr-2" /> Transparency Notice
            </h3>
            <p className="leading-relaxed text-blue-800/80">
              This page displays approved public information regarding the selected infrastructure project. Internal reviews, predictive analytics, and alerts are restricted to monitoring officers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
