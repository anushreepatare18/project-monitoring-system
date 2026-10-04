"use client";

import { 
  Search,
  Filter
} from "lucide-react";

export default function PublicProjects() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-teal-600 dark:text-teal-500 tracking-tight">Project Directory</h1>
        <p className="text-slate-500 dark:text-slate-400 font-medium mt-1">
          Search and explore approved data for major infrastructure projects.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        
        {/* Filters */}
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex flex-col md:flex-row gap-4 bg-slate-50 dark:bg-slate-800/50">
          <div className="relative flex-1 max-w-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            <input 
              type="text" 
              placeholder="Search by name or ID..."
              className="block w-full pl-10 pr-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          
          <div className="flex items-center space-x-2 text-slate-400 shrink-0">
            <Filter className="w-4 h-4" />
          </div>

          <div className="flex flex-col sm:flex-row flex-1 gap-4">
            <select className="block w-full py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500">
              <option>All Ministries</option>
            </select>
            <select className="block w-full py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500">
              <option>All Sectors</option>
            </select>
          </div>
        </div>
        
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
           <select className="block w-full py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500 max-w-4xl">
              <option>All States</option>
           </select>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800">
                <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Project</th>
                <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Ministry / Sector</th>
                <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Location</th>
                <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Financials (Cr)</th>
                <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest w-32">Progress</th>
                <th className="p-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Timeline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                <td className="p-4">
                  <div className="text-xs text-slate-500 mb-0.5">PRJ-611017</div>
                  <div className="font-bold text-teal-600 dark:text-teal-500 text-xs mb-1.5 truncate max-w-[200px]">2.5 MTPA PATHERDIH NLW ...</div>
                  <span className="bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                    ON TRACK
                  </span>
                </td>
                <td className="p-4">
                  <div className="text-sm font-semibold text-slate-900 dark:text-white mb-0.5">Coal</div>
                  <div className="text-[10px] text-slate-500">Coal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm text-slate-700 dark:text-slate-300">Jharkhand</div>
                </td>
                <td className="p-4">
                  <div className="text-sm font-bold text-slate-900 dark:text-white mb-0.5">A: ₹334.27 Cr</div>
                  <div className="text-[10px] text-slate-500">E: ₹162.75 Cr</div>
                </td>
                <td className="p-4">
                  <div className="flex items-center space-x-2 w-full">
                    <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: '51.8%' }}></div>
                    </div>
                    <div className="text-[10px] font-bold text-slate-600 dark:text-slate-400 w-8 text-right">51.8%</div>
                  </div>
                </td>
                <td className="p-4">
                  <div className="text-xs font-bold text-slate-900 dark:text-white mb-0.5">01 Jan 1970</div>
                  <div className="text-[9px] text-slate-400">As of Sept 2026</div>
                </td>
              </tr>

              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                <td className="p-4">
                  <div className="text-xs text-slate-500 mb-0.5">PRJ-615193</div>
                  <div className="font-bold text-teal-600 dark:text-teal-500 text-xs mb-1.5 truncate max-w-[200px]">BASUNDHARA WEST EXTEN...</div>
                  <span className="bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                    ON TRACK
                  </span>
                </td>
                <td className="p-4">
                  <div className="text-sm font-semibold text-slate-900 dark:text-white mb-0.5">Coal</div>
                  <div className="text-[10px] text-slate-500">Coal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm text-slate-700 dark:text-slate-300">Odisha</div>
                </td>
                <td className="p-4">
                  <div className="text-sm font-bold text-slate-900 dark:text-white mb-0.5">A: ₹479.15 Cr</div>
                  <div className="text-[10px] text-slate-500">E: ₹281.57 Cr</div>
                </td>
                <td className="p-4">
                  <div className="flex items-center space-x-2 w-full">
                    <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: '67.6%' }}></div>
                    </div>
                    <div className="text-[10px] font-bold text-slate-600 dark:text-slate-400 w-8 text-right">67.6%</div>
                  </div>
                </td>
                <td className="p-4">
                  <div className="text-xs font-bold text-slate-900 dark:text-white mb-0.5">01 Jan 1970</div>
                  <div className="text-[9px] text-slate-400">As of Sept 2026</div>
                </td>
              </tr>

              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                <td className="p-4">
                  <div className="text-xs text-slate-500 mb-0.5">PRJ-400182</div>
                  <div className="font-bold text-teal-600 dark:text-teal-500 text-xs mb-1.5 truncate max-w-[200px]">SIDULI [OC & UG]</div>
                  <span className="bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                    ON TRACK
                  </span>
                </td>
                <td className="p-4">
                  <div className="text-sm font-semibold text-slate-900 dark:text-white mb-0.5">Coal</div>
                  <div className="text-[10px] text-slate-500">Coal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm text-slate-700 dark:text-slate-300">West Bengal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm font-bold text-slate-900 dark:text-white mb-0.5">A: ₹535.18 Cr</div>
                  <div className="text-[10px] text-slate-500">E: ₹5.74 Cr</div>
                </td>
                <td className="p-4">
                  <div className="flex items-center space-x-2 w-full">
                    <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: '14.8%' }}></div>
                    </div>
                    <div className="text-[10px] font-bold text-slate-600 dark:text-slate-400 w-8 text-right">14.8%</div>
                  </div>
                </td>
                <td className="p-4">
                  <div className="text-xs font-bold text-slate-900 dark:text-white mb-0.5">01 Jan 1970</div>
                  <div className="text-[9px] text-slate-400">As of Sept 2026</div>
                </td>
              </tr>
              
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                <td className="p-4">
                  <div className="text-xs text-slate-500 mb-0.5">PRJ-611016</div>
                  <div className="font-bold text-teal-600 dark:text-teal-500 text-xs mb-1.5 truncate max-w-[200px]">2.0 MTPA BHOJUDIH NLW ...</div>
                  <span className="bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                    ON TRACK
                  </span>
                </td>
                <td className="p-4">
                  <div className="text-sm font-semibold text-slate-900 dark:text-white mb-0.5">Coal</div>
                  <div className="text-[10px] text-slate-500">Coal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm text-slate-700 dark:text-slate-300">West Bengal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm font-bold text-slate-900 dark:text-white mb-0.5">A: ₹384.57 Cr</div>
                  <div className="text-[10px] text-slate-500">E: ₹363.14 Cr</div>
                </td>
                <td className="p-4">
                  <div className="flex items-center space-x-2 w-full">
                    <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: '97.6%' }}></div>
                    </div>
                    <div className="text-[10px] font-bold text-slate-600 dark:text-slate-400 w-8 text-right">97.6%</div>
                  </div>
                </td>
                <td className="p-4">
                  <div className="text-xs font-bold text-slate-900 dark:text-white mb-0.5">01 Jan 1970</div>
                  <div className="text-[9px] text-slate-400">As of Sept 2026</div>
                </td>
              </tr>
              
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                <td className="p-4">
                  <div className="text-xs text-slate-500 mb-0.5">PRJ-612819</div>
                  <div className="font-bold text-teal-600 dark:text-teal-500 text-xs mb-1.5 truncate max-w-[200px]">300 MW SPP part of 510 M...</div>
                  <span className="bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                    ON TRACK
                  </span>
                </td>
                <td className="p-4">
                  <div className="text-sm font-semibold text-slate-900 dark:text-white mb-0.5">Coal</div>
                  <div className="text-[10px] text-slate-500">Coal</div>
                </td>
                <td className="p-4">
                  <div className="text-sm text-slate-700 dark:text-slate-300">Rajasthan</div>
                </td>
                <td className="p-4">
                  <div className="text-sm font-bold text-slate-900 dark:text-white mb-0.5">A: ₹1,813.00 Cr</div>
                  <div className="text-[10px] text-slate-500">E: ₹1,753.07 Cr</div>
                </td>
                <td className="p-4">
                  <div className="flex items-center space-x-2 w-full">
                    <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500" style={{ width: '100.0%' }}></div>
                    </div>
                    <div className="text-[10px] font-bold text-slate-600 dark:text-slate-400 w-8 text-right">100.0%</div>
                  </div>
                </td>
                <td className="p-4">
                  <div className="text-xs font-bold text-slate-900 dark:text-white mb-0.5">01 Jan 1970</div>
                  <div className="text-[9px] text-slate-400">As of Sept 2026</div>
                </td>
              </tr>
              
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
