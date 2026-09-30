"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Activity, 
  BarChart2, 
  Bot,
  Search,
  Settings,
  LogOut,
  Target,
  FileText,
  SearchCode
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();
  
  const menuItems = [
    { name: "Overview", icon: LayoutDashboard, path: "/dashboard/officer" },
    { name: "Alert Queue", icon: AlertTriangle, path: "/dashboard/officer/alerts" },
    { name: "Project Monitoring", icon: Target, path: "/dashboard/officer/monitoring" },
    { name: "AI Risk Insights", icon: Activity, path: "/dashboard/officer/projects" },
    { name: "Risk Assistant", icon: Bot, path: "/dashboard/officer/assistant" },
    { name: "Anomaly Review", icon: SearchCode, path: "/dashboard/officer/anomalies" },
    { name: "Project Benchmarking", icon: BarChart2, path: "/dashboard/officer/benchmarking" },
    { name: "Reports", icon: FileText, path: "/dashboard/officer/reports" },
  ];

  return (
    <div className="w-64 bg-[#0B132B] text-slate-300 flex flex-col h-screen fixed left-0 top-0 border-r border-slate-800 z-50">
      
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800/50">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 bg-emerald-500 rounded flex items-center justify-center text-white font-black text-xs">
            SG
          </div>
          <span className="font-bold text-white text-lg tracking-tight">Smart Gov <span className="text-emerald-400 font-normal">System</span></span>
        </div>
      </div>

      {/* Role Label */}
      <div className="px-6 py-5">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          <span className="text-[10px] font-black text-emerald-500 tracking-widest uppercase">Monitoring Officer</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = pathname === item.path || pathname.startsWith(item.path + '/');
          const Icon = item.icon;
          return (
            <Link 
              key={item.name} 
              href={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium ${
                isActive 
                  ? "bg-emerald-900/30 text-emerald-400 font-semibold" 
                  : "hover:bg-slate-800/50 hover:text-white"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 space-y-1 border-t border-slate-800/50">
        <button className="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium w-full hover:bg-slate-800/50 hover:text-white">
          <Bot className="w-4 h-4 text-slate-400" />
          Smart Gov Assistant
        </button>
        <button className="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium w-full hover:bg-slate-800/50 hover:text-white">
          <Settings className="w-4 h-4 text-slate-400" />
          Preferences
        </button>
      </div>
      
      <div className="p-4 pt-0">
        <div className="bg-red-500/20 text-red-400 rounded-xl px-3 py-2 flex items-center justify-between text-xs font-bold border border-red-500/30 cursor-pointer hover:bg-red-500/30 transition-colors">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-red-500 text-white flex items-center justify-center font-bold">N</div>
            <span>2 Issues</span>
          </div>
          <span>×</span>
        </div>
      </div>
    </div>
  );
}
