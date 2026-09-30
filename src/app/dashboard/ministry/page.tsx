"use client";
import { Building2, FileText, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function MinistryDashboard() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Ministry Overview</h1>
        <p className="text-sm font-medium text-slate-500">
          Track portfolio performance and high-risk alerts across your ministry's projects.
        </p>
      </div>

      <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col items-center justify-center text-center mt-12 max-w-2xl mx-auto">
        <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-4">
          <Building2 className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Ministry Portfolio</h2>
        <p className="text-slate-500 text-sm mb-6">View aggregated reports and analytics for all active projects under your jurisdiction.</p>
        <Link href="/dashboard/officer" className="bg-blue-600 text-white px-6 py-3 rounded-full font-bold text-sm flex items-center gap-2 hover:bg-blue-700 transition-colors">
          View Detailed Reports <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
