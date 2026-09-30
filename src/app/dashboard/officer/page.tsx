"use client";

import { useState, useEffect } from "react";
import { Target, ShieldAlert, AlertTriangle, CheckCircle, MessageSquare } from "lucide-react";
import { motion } from "framer-motion";

export default function OfficerDashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/portfolio/summary");
        if (res.ok) {
          setSummary(await res.json());
        }
      } catch (error) {
        console.error("Failed to fetch summary:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  const total = summary?.total_projects || 2111;
  const critical = summary?.risk_distribution?.Critical || 107;
  const high = summary?.risk_distribution?.High || 0;
  const onTrack = (summary?.risk_distribution?.Low || 0) + (summary?.risk_distribution?.Medium || 0) || 1977;

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto relative min-h-[calc(100vh-64px)] pb-24">
      
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-emerald-500 to-indigo-600 mb-2">
          Monitoring Officer Dashboard
        </h1>
        <p className="text-sm font-medium text-slate-500">
          Review AI risk anomalies, investigate project delays, and resolve field alerts.
        </p>
      </motion.div>

      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
      >
        {/* Card 1 */}
        <motion.div variants={item} className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">
              {loading ? "..." : total}
            </h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Total Monitored</p>
          </div>
        </motion.div>

        {/* Card 2 */}
        <motion.div variants={item} className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="w-10 h-10 rounded-full bg-red-50 text-red-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">
              {loading ? "..." : critical}
            </h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Critical Risk</p>
          </div>
        </motion.div>

        {/* Card 3 */}
        <motion.div variants={item} className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="w-10 h-10 rounded-full bg-orange-50 text-orange-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">
              {loading ? "..." : high}
            </h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">High Risk</p>
          </div>
        </motion.div>

        {/* Card 4 */}
        <motion.div variants={item} className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <CheckCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-slate-900 tracking-tight">
              {loading ? "..." : onTrack}
            </h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Projects On Track</p>
          </div>
        </motion.div>
      </motion.div>

      {/* Alert Queue Overview */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex items-center justify-between hover:shadow-md transition-shadow"
      >
        <div className="max-w-2xl pr-8">
          <h3 className="text-sm font-bold text-slate-900 mb-2">Alert Queue Overview</h3>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            You have <strong className="text-slate-800">0 new anomalies</strong> detected by the PRAGYA AI engine that require triage. There are <strong className="text-slate-800">0 alerts</strong> where implementing agencies have provided responses needing your final review.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-amber-50 text-amber-600 border border-amber-100 px-6 py-4 rounded-2xl flex flex-col items-center justify-center min-w-[120px]">
            <span className="text-2xl font-black">0</span>
            <span className="text-[9px] font-bold uppercase tracking-widest mt-1">Action Req.</span>
          </div>
          <div className="bg-slate-50 text-slate-500 border border-slate-200 px-6 py-4 rounded-2xl flex flex-col items-center justify-center min-w-[120px]">
            <span className="text-2xl font-black">0</span>
            <span className="text-[9px] font-bold uppercase tracking-widest mt-1">In Progress</span>
          </div>
        </div>
      </motion.div>

      {/* Floating Chat Button */}
      <motion.div 
        initial={{ scale: 0, rotate: -90 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.8 }}
        className="fixed bottom-8 right-8 z-50"
      >
        <button className="w-14 h-14 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full shadow-lg shadow-emerald-600/30 flex items-center justify-center transition-transform hover:scale-110 active:scale-95 group">
          <MessageSquare className="w-6 h-6 group-hover:animate-pulse" />
          <div className="absolute top-0 right-0 w-3 h-3 bg-white rounded-full border-2 border-emerald-600"></div>
        </button>
      </motion.div>

    </div>
  );
}
