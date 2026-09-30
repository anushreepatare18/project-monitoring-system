"use client";
import { Search, Bell, LogOut } from "lucide-react";
import Link from "next/link";

export default function Header() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-40">
      
      <div className="flex-1 max-w-2xl">
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search projects, alerts, or queries..."
            className="block w-full pl-10 pr-3 py-2 border-0 bg-slate-50 text-slate-900 rounded-xl ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-inset focus:ring-emerald-500 sm:text-sm sm:leading-6 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-5 pl-4">
        <button className="text-slate-400 hover:text-slate-600 transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
        </button>
        
        <div className="h-8 w-px bg-slate-200"></div>
        
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-bold text-slate-800 leading-tight">Demo User</p>
            <p className="text-[9px] font-black text-emerald-600 uppercase tracking-widest">Officer</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold border border-emerald-200">
            DU
          </div>
        </div>

        <Link href="/login" className="text-slate-400 hover:text-slate-600 transition-colors ml-2">
          <LogOut className="w-5 h-5" />
        </Link>
      </div>
    </header>
  );
}
