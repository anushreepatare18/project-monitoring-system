"use client";

import { useState, useEffect } from "react";
import { Save, Send, AlertCircle, FileUp, CheckCircle2 } from "lucide-react";

export default function AgencySubmitUpdate() {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState({
    reporting_month: "2026-10",
    expenditure_cr: "",
    financial_progress_pct: "",
    physical_progress_pct: "",
    current_stage: "",
    issue_category: "",
    issue_description: ""
  });

  const AGENCY_NAME = "Agency_1";

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/projects`)
      .then(res => res.json())
      .then(data => {
        const agencyProjects = data.filter((p: any) => p.implementing_agency === AGENCY_NAME);
        setProjects(agencyProjects);
        setLoading(false);
      });
  }, []);

  const selectedProject = projects.find(p => p.id === selectedProjectId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId) return;
    
    setSubmitting(true);
    // Mock submission latency
    setTimeout(() => {
      setSubmitting(false);
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setFormData({ ...formData, expenditure_cr: "", financial_progress_pct: "", physical_progress_pct: "", current_stage: "", issue_description: "" });
      }, 3000);
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Submit Project Update</h1>
        <p className="text-slate-500 font-medium mt-1">
          Provide periodic progress reporting for your assigned projects.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        
        {success ? (
          <div className="p-12 text-center flex flex-col items-center">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-4">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Update Submitted Successfully</h2>
            <p className="text-slate-500 max-w-md mx-auto">Your progress report for {selectedProject?.name} has been securely recorded and is under review by the Ministry.</p>
            <button onClick={() => setSuccess(false)} className="mt-6 text-emerald-600 font-bold hover:underline">Submit another update</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="divide-y divide-slate-100">
            {/* Project Selection */}
            <div className="p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center">
                1. Project Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Select Project *</label>
                  <select 
                    required 
                    value={selectedProjectId} 
                    onChange={e => setSelectedProjectId(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="">-- Choose Project --</option>
                    {projects.map(p => <option key={p.id} value={p.id}>{p.id} - {p.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Reporting Month *</label>
                  <input 
                    type="month" 
                    required 
                    value={formData.reporting_month}
                    onChange={e => setFormData({...formData, reporting_month: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50"
                  />
                </div>
              </div>
              {selectedProject && (
                <div className="mt-2 p-3 bg-blue-50 border border-blue-100 rounded-lg text-sm text-blue-800 flex items-start">
                  <AlertCircle className="w-4 h-4 mr-2 mt-0.5 shrink-0" />
                  <div>
                    Last reported physical progress was <strong>{selectedProject.physical_progress_pct}%</strong> on <strong>{selectedProject.last_update_date || 'N/A'}</strong>. Ensure new values are cumulative.
                  </div>
                </div>
              )}
            </div>

            {/* Progress Data */}
            <div className="p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center">
                2. Progress & Financials
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Physical Progress (%) *</label>
                  <input 
                    type="number" min="0" max="100" step="0.1" required
                    value={formData.physical_progress_pct}
                    onChange={e => setFormData({...formData, physical_progress_pct: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                    placeholder={`e.g. ${selectedProject ? selectedProject.physical_progress_pct + 5 : 45}`}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Financial Progress (%) *</label>
                  <input 
                    type="number" min="0" max="100" step="0.1" required
                    value={formData.financial_progress_pct}
                    onChange={e => setFormData({...formData, financial_progress_pct: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                    placeholder="e.g. 40"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Cum. Expenditure (Cr) *</label>
                  <input 
                    type="number" min="0" step="0.01" required
                    value={formData.expenditure_cr}
                    onChange={e => setFormData({...formData, expenditure_cr: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                    placeholder={`e.g. ${selectedProject?.expenditure_cr || 100}`}
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Current Stage of Work</label>
                <textarea 
                  rows={2}
                  value={formData.current_stage}
                  onChange={e => setFormData({...formData, current_stage: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                  placeholder="Describe the physical work completed during this reporting period..."
                />
              </div>
            </div>

            {/* Issues */}
            <div className="p-6 space-y-4 bg-slate-50">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center">
                3. Issues & Constraints (Optional)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Issue Category</label>
                  <select 
                    value={formData.issue_category}
                    onChange={e => setFormData({...formData, issue_category: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="">None</option>
                    <option value="Land Acquisition">Land Acquisition</option>
                    <option value="Environmental Clearance">Environmental Clearance</option>
                    <option value="Funding">Funding / Approvals</option>
                    <option value="Weather">Weather / Site Conditions</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Supporting Document</label>
                  <div className="relative">
                    <input type="file" className="hidden" id="file_upload" disabled />
                    <label htmlFor="file_upload" className="w-full flex items-center justify-center px-3 py-2 border border-dashed border-slate-300 rounded-lg text-sm bg-white text-slate-400 cursor-not-allowed">
                      <FileUp className="w-4 h-4 mr-2" /> Attach File (Not implemented in prototype)
                    </label>
                  </div>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs font-bold text-slate-700 mb-1">Issue Description</label>
                  <textarea 
                    rows={2}
                    value={formData.issue_description}
                    onChange={e => setFormData({...formData, issue_description: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                    placeholder="Describe any blockers delaying progress..."
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="p-6 bg-white flex justify-end gap-3">
              <button type="button" className="px-4 py-2 border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:bg-slate-50 transition flex items-center">
                <Save className="w-4 h-4 mr-2" /> Save Draft
              </button>
              <button type="submit" disabled={submitting || !selectedProjectId} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-bold hover:bg-emerald-700 transition flex items-center disabled:opacity-50">
                {submitting ? 'Submitting...' : <><Send className="w-4 h-4 mr-2" /> Submit Update</>}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
