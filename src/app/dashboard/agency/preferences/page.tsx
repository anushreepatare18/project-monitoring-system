"use client";

import { User, Bell, Settings, Lock, ShieldCheck } from "lucide-react";

export default function AgencyPreferences() {
  const AGENCY_NAME = "Agency_1";
  
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight text-emerald-600">Preferences</h1>
        <p className="text-slate-500 font-medium mt-1">
          Manage your account profile, notifications, and application settings.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Navigation Sidebar */}
        <div className="md:col-span-1 space-y-2">
          <button className="w-full text-left px-4 py-3 bg-emerald-50 text-emerald-700 font-bold rounded-xl border border-emerald-100 flex items-center">
            <User className="w-4 h-4 mr-3" /> Profile
          </button>
          <button className="w-full text-left px-4 py-3 text-slate-600 font-semibold rounded-xl border border-transparent hover:bg-slate-50 transition flex items-center">
            <Bell className="w-4 h-4 mr-3 text-slate-400" /> Notifications
          </button>
          <button className="w-full text-left px-4 py-3 text-slate-600 font-semibold rounded-xl border border-transparent hover:bg-slate-50 transition flex items-center">
            <Settings className="w-4 h-4 mr-3 text-slate-400" /> Display
          </button>
          <button className="w-full text-left px-4 py-3 text-slate-600 font-semibold rounded-xl border border-transparent hover:bg-slate-50 transition flex items-center">
            <Lock className="w-4 h-4 mr-3 text-slate-400" /> Security
          </button>
        </div>

        {/* Settings Panel */}
        <div className="md:col-span-2 space-y-6">
          
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center">
              <User className="w-5 h-5 text-slate-500 mr-2" />
              <h3 className="font-bold text-slate-700">Account Profile</h3>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Name</label>
                  <input type="text" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50" defaultValue="Rahul Sharma" disabled />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Username / ID</label>
                  <input type="text" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50" defaultValue="rahul.agency1" disabled />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Organization</label>
                  <input type="text" className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 font-bold text-slate-700" defaultValue={AGENCY_NAME} disabled />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Assigned Role</label>
                  <div className="flex items-center px-3 py-2 border border-slate-200 rounded-lg text-sm bg-emerald-50 text-emerald-700 font-bold">
                    <ShieldCheck className="w-4 h-4 mr-2" /> Implementing Agency
                  </div>
                </div>
              </div>
              <div className="pt-4 border-t border-slate-100">
                <button className="bg-emerald-600 text-white px-6 py-2 rounded-lg text-sm font-bold hover:bg-emerald-700 transition">Save Changes</button>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center">
              <Bell className="w-5 h-5 text-slate-500 mr-2" />
              <h3 className="font-bold text-slate-700">Notification Preferences (Local Prototype)</h3>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-slate-100">
                <div>
                  <div className="font-bold text-sm text-slate-900">Update Reminders</div>
                  <div className="text-xs text-slate-500">Receive alerts when progress updates are due.</div>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-100">
                <div>
                  <div className="font-bold text-sm text-slate-900">New Alerts & Clarifications</div>
                  <div className="text-xs text-slate-500">Notify me when an officer requests clarification.</div>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="font-bold text-sm text-slate-900">Upcoming Milestone Deadlines</div>
                  <div className="text-xs text-slate-500">Get notified 7 days before a milestone is due.</div>
                </div>
                <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
