"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Briefcase, 
  Settings, 
  LogOut,
  TrendingUp,
  FileText
} from "lucide-react";
import clsx from "clsx";

export default function Sidebar() {
  const pathname = usePathname();

  // Basic mock role extraction from pathname for the prototype
  const role = pathname.split('/')[2] || "officer";

  const navigation = [
    { name: "Overview", href: `/dashboard/${role}`, icon: LayoutDashboard },
    { name: "Alerts Queue", href: `/dashboard/${role}/alerts`, icon: AlertTriangle },
    { name: "Projects", href: `/dashboard/${role}/projects`, icon: Briefcase },
    { name: "Reports", href: `/dashboard/${role}/reports`, icon: FileText },
  ];

  return (
    <div className="flex h-full w-64 flex-col bg-slate-900 border-r border-slate-800">
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-slate-800">
        <TrendingUp className="text-blue-500 w-6 h-6 mr-2" />
        <span className="text-xl font-bold text-white tracking-tight">PRAGYA AI</span>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto pt-6 px-4">
        <div className="mb-6 px-2">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {role.toUpperCase()} MENU
          </p>
        </div>
        
        <nav className="flex-1 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(
                  "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                  isActive
                    ? "bg-blue-600 text-white shadow-md shadow-blue-900/20"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                )}
              >
                <item.icon
                  className={clsx(
                    "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                    isActive ? "text-white" : "text-slate-400 group-hover:text-white"
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
      
      <div className="flex shrink-0 border-t border-slate-800 p-4">
        <Link
          href="/login"
          className="group block w-full flex-shrink-0 rounded-lg p-2 transition-all hover:bg-slate-800"
        >
          <div className="flex items-center">
            <div>
              <div className="inline-block h-9 w-9 rounded-full bg-slate-700 flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {role.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-white group-hover:text-white">
                {role.charAt(0).toUpperCase() + role.slice(1)} User
              </p>
              <p className="text-xs font-medium text-slate-400 flex items-center mt-0.5">
                <LogOut className="w-3 h-3 mr-1" />
                Sign out
              </p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}
