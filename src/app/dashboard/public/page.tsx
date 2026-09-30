"use client";
import { Globe, Search, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function PublicDashboard() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-emerald-600 mb-2">Public Transparency Portal</h1>
        <p className="text-sm font-medium text-slate-500">
          Open access to execution metrics and financials for national infrastructure projects.
        </p>
      </div>

      <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col items-center justify-center text-center mt-12 max-w-2xl mx-auto">
        <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-4">
          <Globe className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Citizen Visibility</h2>
        <p className="text-slate-500 text-sm mb-6">Explore the status of major infrastructure investments across the country.</p>
        <Link href="/dashboard/public/about" className="bg-emerald-600 text-white px-6 py-3 rounded-full font-bold text-sm flex items-center gap-2 hover:bg-emerald-700 transition-colors">
          Learn How It Works <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
