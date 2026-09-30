"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Building2, 
  Activity, 
  ShieldCheck, 
  Mail, 
  Lock, 
  Eye, 
  ArrowRight,
  Briefcase,
  User,
  Globe,
  ChevronDown,
  AlertTriangle
} from "lucide-react";

export default function LandingLoginPage() {
  const router = useRouter();
  const [role, setRole] = useState("officer");
  const [loading, setLoading] = useState(false);

  const handleLogin = (e?: React.FormEvent, selectedRole?: string) => {
    if (e) e.preventDefault();
    const loginRole = selectedRole || role;
    
    setLoading(true);
    // Simulate API call and redirect based on role
    setTimeout(() => {
      if (loginRole === "officer") router.push("/dashboard/officer");
      else if (loginRole === "ministry") router.push("/dashboard/ministry");
      else if (loginRole === "agency") router.push("/dashboard/agency");
      else if (loginRole === "admin") router.push("/dashboard/admin");
      else router.push("/dashboard/public");
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#F0F2F5] font-sans overflow-hidden flex flex-col relative">
      
      {/* Floating Header */}
      <div className="w-full flex justify-center pt-6 z-20 absolute top-0">
        <div className="bg-white/80 backdrop-blur-md px-4 py-3 rounded-full flex items-center justify-between w-[90%] max-w-6xl shadow-sm border border-white/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600 font-bold text-sm border border-emerald-100">
              PR
            </div>
            <span className="font-bold text-slate-800 text-sm md:text-base hidden sm:block">
              Smart Government Project Monitoring <span className="text-emerald-600 font-bold">and Risk Management System</span>
            </span>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex gap-6 text-sm font-semibold text-slate-600">
              <a href="#" className="hover:text-slate-900 transition-colors">Capabilities</a>
              <a href="#" className="hover:text-slate-900 transition-colors">Workflows</a>
            </div>
            <button className="bg-[#0B132B] text-white px-6 py-2.5 rounded-full text-sm font-medium flex items-center gap-2 hover:bg-slate-800 transition-all">
              Access Portal
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 w-full max-w-7xl mx-auto px-6 pt-32 pb-12 grid grid-cols-1 lg:grid-cols-12 gap-12 relative">
        
        {/* Left Content Area */}
        <div className="lg:col-span-6 flex flex-col justify-center z-10">
          <h1 className="text-6xl md:text-7xl font-black text-[#0B132B] leading-[1.1] tracking-tight mb-2">
            Smarter<br/>Monitoring.
          </h1>
          <h1 className="text-6xl md:text-7xl font-black text-[#00C48C] leading-[1.1] tracking-tight mb-8">
            Stronger<br/>Infrastructure.
          </h1>
          
          <div className="bg-slate-200/50 backdrop-blur-sm rounded-2xl p-6 mb-12 max-w-lg border border-slate-200">
            <p className="text-slate-700 leading-relaxed font-medium">
              Smart Government Project Monitoring and Risk Management System leverages continuous project data to predict cost overruns, explain risk factors, detect anomalies and generate early warnings — empowering faster, data-driven decisions.
            </p>
          </div>
          
          {/* Stat Cards */}
          <div className="flex flex-wrap gap-4">
            <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex-1 min-w-[140px]">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-600 mb-4">
                <Activity className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-black text-slate-800 tracking-tight">1,981+</h3>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">Active Projects</p>
            </div>
            <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex-1 min-w-[140px]">
              <div className="w-10 h-10 rounded-xl bg-cyan-100 flex items-center justify-center text-cyan-600 mb-4">
                <Building2 className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-black text-slate-800 tracking-tight">17</h3>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">Ministries</p>
            </div>
            <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex-1 min-w-[140px]">
              <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600 mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-black text-slate-800 tracking-tight">98%</h3>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">AI Accuracy</p>
            </div>
          </div>
        </div>

        {/* Center Floating Elements (Decorative) */}
        <div className="hidden lg:block lg:col-span-2 relative pointer-events-none z-0">
          <div className="absolute top-[20%] left-[-40%] w-full">
            
            {/* Circular Risk Card */}
            <div className="bg-white p-5 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 absolute transform rotate-[-5deg] w-48 animate-[float_6s_ease-in-out_infinite]">
              <p className="text-xs font-bold text-slate-800 mb-3 text-center">AI Risk Prediction</p>
              <div className="relative w-24 h-24 mx-auto mb-2">
                <svg className="w-full h-full" viewBox="0 0 36 36">
                  <path className="text-slate-100" strokeWidth="4" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <path className="text-red-500" strokeWidth="4" strokeDasharray="82, 100" strokeLinecap="round" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-black text-slate-800 tracking-tighter">82</span>
                </div>
              </div>
              <p className="text-[10px] font-bold text-red-500 text-center uppercase tracking-widest mt-3">High Risk</p>
            </div>

            {/* SHAP Factors Card */}
            <div className="bg-white p-4 rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 absolute top-32 left-24 w-56 transform rotate-[3deg] animate-[float_7s_ease-in-out_infinite_0.5s]">
              <div className="flex justify-between items-center mb-3">
                <p className="text-xs font-bold text-slate-800">SHAP Factors</p>
                <Activity className="w-3 h-3 text-emerald-500" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center text-[10px] font-semibold text-slate-500">
                  <span>Milestone Delay</span><span className="text-blue-600 font-bold">+0.28</span>
                </div>
                <div className="flex justify-between items-center text-[10px] font-semibold text-slate-500">
                  <span>Progress Gap</span><span className="text-blue-600 font-bold">+0.22</span>
                </div>
                <div className="flex justify-between items-center text-[10px] font-semibold text-slate-500">
                  <span>Cost Growth</span><span className="text-blue-600 font-bold">+0.16</span>
                </div>
              </div>
            </div>

            {/* Anomaly Card */}
            <div className="bg-white p-4 rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 absolute top-80 left-0 w-60 transform rotate-[-2deg] animate-[float_8s_ease-in-out_infinite_1s]">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center text-red-500">
                  <AlertTriangle className="w-3 h-3" />
                </div>
                <p className="text-[11px] font-bold text-slate-800">Anomaly Detected</p>
              </div>
              <p className="text-[10px] text-slate-500 leading-tight">Unusual cost increase in last 2 updates detected by AI models.</p>
            </div>
          </div>
        </div>

        {/* Right Auth Area */}
        <div className="lg:col-span-4 flex items-center justify-center z-10 lg:justify-end">
          <div className="bg-white w-full max-w-[400px] p-8 md:p-10 rounded-[2rem] shadow-2xl shadow-slate-300/60 border border-slate-100">
            <h2 className="text-3xl font-black text-[#0B132B] mb-2 tracking-tight">Secure Access</h2>
            <p className="text-sm font-medium text-slate-500 mb-8">Sign in to the intelligent monitoring portal</p>
            
            <form onSubmit={(e) => handleLogin(e)} className="space-y-4">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  type="email"
                  className="block w-full pl-12 pr-3 py-3.5 border-0 bg-slate-50 text-slate-900 rounded-2xl ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-inset focus:ring-emerald-500 sm:text-sm sm:leading-6 transition-all"
                  placeholder="Email Address"
                  defaultValue="officer@gov.in"
                />
              </div>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  type="password"
                  className="block w-full pl-12 pr-10 py-3.5 border-0 bg-slate-50 text-slate-900 rounded-2xl ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-inset focus:ring-emerald-500 sm:text-sm sm:leading-6 transition-all"
                  placeholder="Password"
                  defaultValue="••••••••"
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center cursor-pointer">
                  <Eye className="h-5 w-5 text-slate-400 hover:text-slate-600" />
                </div>
              </div>

              <div className="pt-2 pb-1">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">Select Active Role</p>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Briefcase className="h-5 w-5 text-slate-600" />
                  </div>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="block w-full pl-12 pr-10 py-3.5 border-0 bg-slate-50 text-slate-900 font-semibold rounded-2xl ring-1 ring-inset ring-slate-200 focus:ring-2 focus:ring-inset focus:ring-emerald-500 sm:text-sm sm:leading-6 appearance-none cursor-pointer transition-all"
                  >
                    <option value="officer">Choose your role...</option>
                    <option value="officer">Monitoring Officer</option>
                    <option value="ministry">Ministry / Policymaker</option>
                    <option value="agency">Implementing Agency</option>
                    <option value="admin">System Administrator</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                    <ChevronDown className="h-5 w-5 text-slate-400" />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#0B132B] hover:bg-slate-800 text-white font-semibold py-4 rounded-2xl transition-all shadow-lg shadow-[#0B132B]/20 flex items-center justify-center gap-2 group mt-4"
              >
                {loading ? "Authenticating..." : (
                  <>
                    Authenticate to Portal
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>

            <div className="relative mt-8 mb-6">
              <div className="absolute inset-0 flex items-center" aria-hidden="true">
                <div className="w-full border-t border-slate-200 border-dashed" />
              </div>
              <div className="relative flex justify-center">
                <span className="bg-white px-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  1-Click Demo Login
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button onClick={() => handleLogin(undefined, "admin")} className="flex items-center justify-center gap-2 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:text-slate-900 transition-colors">
                <ShieldCheck className="w-4 h-4" /> Admin
              </button>
              <button onClick={() => handleLogin(undefined, "ministry")} className="flex items-center justify-center gap-2 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:text-slate-900 transition-colors">
                <Building2 className="w-4 h-4" /> Ministry
              </button>
              <button onClick={() => handleLogin(undefined, "officer")} className="flex items-center justify-center gap-2 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:text-slate-900 transition-colors">
                <User className="w-4 h-4" /> Officer
              </button>
              <button onClick={() => handleLogin(undefined, "public")} className="flex items-center justify-center gap-2 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:text-slate-900 transition-colors">
                <Globe className="w-4 h-4" /> Public
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 w-full flex flex-col items-center justify-center text-emerald-600 animate-bounce">
        <span className="text-[10px] font-bold uppercase tracking-widest mb-1">Scroll to Explore</span>
        <ChevronDown className="w-4 h-4" />
      </div>

    </div>
  );
}
