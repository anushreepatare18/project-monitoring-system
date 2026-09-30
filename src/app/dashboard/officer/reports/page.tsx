"use client";
import { FileText, Download } from "lucide-react";

export default function ReportsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Reports & Exports</h1>
        <p className="text-sm font-medium text-slate-500">
          Generate formal audit reports and download project data extracts.
        </p>
      </div>

      <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 mt-12 max-w-4xl mx-auto text-center">
        <div className="w-16 h-16 bg-slate-50 text-slate-500 rounded-full flex items-center justify-center mb-4 mx-auto border border-slate-200">
          <FileText className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Report Generation</h2>
        <p className="text-slate-500 text-sm mb-6">Select a reporting period to generate standard PDF or CSV reports.</p>
        <button className="bg-slate-900 text-white px-6 py-3 rounded-full font-bold text-sm flex items-center gap-2 hover:bg-slate-800 transition-colors mx-auto">
          <Download className="w-4 h-4" /> Export Latest Report
        </button>
      </div>
    </div>
  );
}
