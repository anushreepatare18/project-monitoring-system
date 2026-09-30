"use client";

import { Eye, Activity, Shield, Database } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      
      <div className="mb-8">
        <h1 className="text-3xl font-black text-emerald-600 mb-2">About PRAGYA AI</h1>
        <p className="text-sm font-medium text-slate-500">
          Understanding how India monitors and protects public infrastructure investments.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column */}
        <div className="space-y-6">
          <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
            <h2 className="text-xl font-black text-slate-900 mb-4">Our Mission</h2>
            <p className="text-sm text-slate-600 leading-relaxed mb-8">
              PRAGYA AI is an advanced AI-powered Infrastructure Project Monitoring System developed to bring unparalleled transparency, efficiency, and predictive oversight to India's national infrastructure growth. By leveraging real-time data and predictive analytics, PRAGYA AI ensures that critical projects — from highways to airports — are completed on time and within budget.
            </p>

            <div className="space-y-3">
              <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                  <Eye className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold text-slate-900">Radical Transparency</span>
              </div>
              <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                  <Activity className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold text-slate-900">Predictive Risk Monitoring</span>
              </div>
              <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                  <Shield className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold text-slate-900">Inter-Ministerial Accountability</span>
              </div>
            </div>
          </div>

          <div className="bg-[#0B132B] p-8 rounded-[2rem] shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <Database className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-black text-white">Data & Privacy Policy</h2>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              The Public Transparency Portal provides access only to approved execution metrics and financials. Internal AI risk scores, predictive models, and Monitoring Officer audit logs are strictly shielded to protect sensitive governmental operations.
            </p>
          </div>
        </div>

        {/* Right Column */}
        <div>
          <div className="bg-emerald-50 border border-emerald-100 p-8 rounded-[2rem] h-full">
            <h2 className="text-lg font-black text-slate-900 mb-8">How It Works</h2>
            
            <div className="relative pl-6 space-y-10 before:absolute before:inset-0 before:ml-[1.4rem] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-emerald-300 before:to-transparent">
              
              {/* Step 1 */}
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500 text-white font-bold text-[10px] absolute left-[-1.85rem] z-10 shadow ring-4 ring-emerald-50">1</div>
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-emerald-100 ml-4 w-[90%] md:w-[280px]">
                  <h4 className="text-xs font-black text-slate-900 mb-1">Data Ingestion</h4>
                  <p className="text-[10px] text-emerald-700 font-medium">Implementing Agencies submit progress updates via standardized digital forms.</p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500 text-white font-bold text-[10px] absolute left-[-1.85rem] z-10 shadow ring-4 ring-emerald-50">2</div>
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-emerald-100 ml-4 w-[90%] md:w-[280px]">
                  <h4 className="text-xs font-black text-slate-900 mb-1">AI Risk Triage</h4>
                  <p className="text-[10px] text-emerald-700 font-medium">PRAGYA models scan data for anomalies and assign predictive risk scores.</p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500 text-white font-bold text-[10px] absolute left-[-1.85rem] z-10 shadow ring-4 ring-emerald-50">3</div>
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-emerald-100 ml-4 w-[90%] md:w-[280px]">
                  <h4 className="text-xs font-black text-slate-900 mb-1">Human Review</h4>
                  <p className="text-[10px] text-emerald-700 font-medium">Monitoring Officers review AI flags, request clarifications, and enforce accountability.</p>
                </div>
              </div>

              {/* Step 4 */}
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-600 text-white font-bold text-[10px] absolute left-[-1.85rem] z-10 shadow ring-4 ring-emerald-50">✓</div>
                <div className="bg-emerald-600 p-5 rounded-2xl shadow-md border border-emerald-500 ml-4 w-[90%] md:w-[280px]">
                  <h4 className="text-xs font-black text-white mb-1">Public Transparency</h4>
                  <p className="text-[10px] text-emerald-50 font-medium">Approved data is published to this dashboard for citizen visibility.</p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
