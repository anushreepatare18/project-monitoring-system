"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import Chatbot from "@/components/chat/Chatbot";
import {
  LayoutDashboard,
  Bell,
  FolderKanban,
  BrainCircuit,
  Bot,
  Activity,
  BarChart2,
  FileText,
  MessageSquare,
  Settings,
  LogOut,
  Globe,
  Search,
  Menu,
  User,
  ShieldCheck,
  X
} from "lucide-react";

const officerMenu = [
  { name: "Overview", icon: LayoutDashboard, href: "/dashboard/officer" },
  { name: "Alert Queue", icon: Bell, href: "/dashboard/officer/alerts" },
  { name: "Project Monitoring", icon: FolderKanban, href: "/dashboard/officer/monitoring" },
  { name: "AI Risk Insights", icon: BrainCircuit, href: "/dashboard/officer/insights" },
  { name: "Risk Assistant", icon: Bot, href: "/dashboard/officer/assistant" },
  { name: "Anomaly Review", icon: Activity, href: "/dashboard/officer/anomalies" },
  { name: "Project Benchmarking", icon: BarChart2, href: "/dashboard/officer/benchmarking" },
  { name: "Reports", icon: FileText, href: "/dashboard/officer/reports" },
];

const publicMenu = [
  { name: "Overview", icon: LayoutDashboard, href: "/dashboard/public" },
  { name: "Browse Projects", icon: FolderKanban, href: "/dashboard/public/projects" },
  { name: "Public Analytics", icon: BarChart2, href: "/dashboard/public/analytics" },
  { name: "About Smart Gov", icon: FileText, href: "/dashboard/public/about" },
];

const agencyMenu = [
  { name: "Overview", icon: LayoutDashboard, href: "/dashboard/agency" },
  { name: "My Projects", icon: FolderKanban, href: "/dashboard/agency/projects" },
  { name: "Submit Update", icon: Activity, href: "/dashboard/agency/update" },
  { name: "Milestones", icon: BarChart2, href: "/dashboard/agency/milestones" },
  { name: "Issues & Constraints", icon: MessageSquare, href: "/dashboard/agency/issues" },
  { name: "AI Risk Insights", icon: BrainCircuit, href: "/dashboard/agency/insights" },
  { name: "Alerts & Responses", icon: Bell, href: "/dashboard/agency/alerts" },
  { name: "Update History", icon: FileText, href: "/dashboard/agency/history" },
  { name: "PRAGYA Assistant", icon: Bot, href: "/dashboard/agency/assistant" },
];

const adminMenu = [
  { name: "Overview", icon: LayoutDashboard, href: "/dashboard/admin" },
  { name: "My Projects", icon: FolderKanban, href: "/dashboard/admin/projects" },
  { name: "Submit Update", icon: Activity, href: "/dashboard/admin/update" },
  { name: "Milestones", icon: BarChart2, href: "/dashboard/admin/milestones" },
  { name: "Issues & Constraints", icon: MessageSquare, href: "/dashboard/admin/issues" },
  { name: "AI Risk Insights", icon: BrainCircuit, href: "/dashboard/admin/insights" },
  { name: "Risk Assistant", icon: Bot, href: "/dashboard/admin/assistant" },
  { name: "Alerts & Responses", icon: Bell, href: "/dashboard/admin/alerts" },
  { name: "Update History", icon: FileText, href: "/dashboard/admin/history" },
];

const ministryMenu = [
  { name: "Overview", icon: LayoutDashboard, href: "/dashboard/ministry" },
  { name: "Project Portfolio", icon: FolderKanban, href: "/dashboard/ministry/portfolio" },
  { name: "Portfolio Analytics", icon: BarChart2, href: "/dashboard/ministry/analytics" },
  { name: "Alerts & Reviews", icon: Bell, href: "/dashboard/ministry/alerts" },
  { name: "Risk Assistant", icon: MessageSquare, href: "/dashboard/ministry/assistant" },
  { name: "Reports", icon: FileText, href: "/dashboard/ministry/reports" },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isPublic = pathname.startsWith("/dashboard/public");
  const isOfficer = pathname.startsWith("/dashboard/officer");
  const isAgency = pathname.startsWith("/dashboard/agency");
  const isMinistry = pathname.startsWith("/dashboard/ministry");
  const isAdmin = pathname.startsWith("/dashboard/admin");
  
  const menu = isPublic ? publicMenu : isOfficer ? officerMenu : isAgency ? agencyMenu : isMinistry ? ministryMenu : isAdmin ? adminMenu : [];
  const roleName = isPublic ? "PUBLIC DASHBOARD" : isOfficer ? "MONITORING OFFICER" : isAgency ? "IMPLEMENTING AGENCY" : isMinistry ? "MINISTRY / DEPT" : isAdmin ? "ADMIN" : "DASHBOARD";
  const userRole = isPublic ? "PUBLIC" : isOfficer ? "OFFICER" : isAgency ? "AGENCY" : isMinistry ? "MINISTRY" : isAdmin ? "AGENCY" : "USER";
  const userInitials = isPublic ? "PU" : isOfficer ? "MO" : isAgency ? "IA" : isMinistry ? "MN" : isAdmin ? "DU" : "US";

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const router = useRouter();

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    router.push("/");
  };

  return (
    <div className="flex h-screen bg-[#f8fafc] dark:bg-[#0f172a] text-slate-900 dark:text-slate-100 font-sans overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#0a0f1c] text-slate-300 transform transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} flex flex-col`}>
        <div className="p-6 flex items-center space-x-3">
          <div className="bg-emerald-500 text-white font-bold rounded-lg w-8 h-8 flex items-center justify-center text-xs">
            SG
          </div>
          <span className="font-extrabold text-white text-lg tracking-tight">
            Smart Gov <span className="text-emerald-500">System</span>
          </span>
        </div>

        <div className="px-6 py-2">
          <div className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-4 flex items-center">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-2"></div>
            {roleName}
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
          {menu.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link 
                key={item.name} 
                href={item.href}
                className={`flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-colors ${isActive ? 'bg-emerald-500/10 text-emerald-400' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button className="flex items-center w-full px-4 py-3 text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors">
            <MessageSquare className="w-5 h-5 mr-3" />
            Smart Gov Assistant
          </button>
          <button className="flex items-center w-full px-4 py-3 text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors">
            <Settings className="w-5 h-5 mr-3" />
            Preferences
          </button>
          <div className="mt-4 flex items-center justify-between px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-xl cursor-pointer hover:bg-red-500/20 transition-colors">
            <div className="flex items-center text-red-500">
              <div className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold mr-2">N</div>
              <span className="text-xs font-bold">2 Issues</span>
            </div>
            <X className="w-4 h-4 text-red-500" />
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="bg-white dark:bg-[#1a2332] border-b border-slate-200 dark:border-slate-800 h-16 flex items-center justify-between px-4 sm:px-6 shrink-0">
          <div className="flex items-center flex-1">
            <button 
              className="mr-4 lg:hidden text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="relative w-full max-w-xl hidden sm:block">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-slate-400" />
              </div>
              <input 
                type="text" 
                placeholder="Search projects, alerts, or queries..."
                className="block w-full pl-10 pr-3 py-2 border-none rounded-full bg-slate-100 dark:bg-slate-800 text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:text-slate-200"
              />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
              <Bell className="w-5 h-5" />
            </button>
            <div className="h-8 w-px bg-slate-200 dark:bg-slate-700"></div>
            <div className="flex items-center">
              <div className="hidden sm:flex flex-col items-end mr-3">
                <span className="text-xs font-bold text-slate-900 dark:text-white">Demo User</span>
                <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest">{userRole}</span>
              </div>
              <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 flex items-center justify-center font-bold text-xs">
                {userInitials}
              </div>
            </div>
            <button onClick={handleLogout} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Page Content Scrollable Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-8">
          {children}
        </div>
      </main>

      {/* Role-Aware AI Assistant Chatbot */}
      <Chatbot 
        role={isPublic ? "public" : isOfficer ? "officer" : isAgency ? "agency" : isMinistry ? "ministry" : isAdmin ? "agency" : "officer"}
        officerId={userInitials + "-001"}
        scope={isAgency || isAdmin ? { agency: "Agency_1" } : isMinistry ? { ministry: "Ministry_7" } : isPublic ? { public_only: true } : {}}
      />
    </div>
  );
}
