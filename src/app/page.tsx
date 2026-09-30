"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  Building2, 
  BarChart3, 
  ShieldCheck, 
  User, 
  Lock, 
  Eye, 
  Briefcase, 
  ChevronDown,
  ArrowRight,
  AlertTriangle,
  Activity
} from "lucide-react";

export default function LandingPage() {
  const router = useRouter();

  const handleDemoLogin = (role: string) => {
    router.push(`/dashboard/${role.toLowerCase()}`);
  };

  return (
    <div className="min-h-screen bg-[#f4f7f9] text-slate-800 font-sans selection:bg-emerald-200 selection:text-emerald-900 overflow-x-hidden relative">
      
      {/* Navbar */}
      <div className="pt-6 px-6 flex justify-center w-full z-50">
        <nav className="bg-white/90 backdrop-blur-md rounded-full px-4 py-3 flex items-center justify-between w-full max-w-7xl shadow-sm border border-slate-200">
          <div className="flex items-center space-x-3 pl-2">
            <div className="bg-emerald-100 text-emerald-700 font-bold rounded-full w-8 h-8 flex items-center justify-center text-xs">
              PR
            </div>
            <span className="font-bold text-sm tracking-tight hidden md:block text-slate-800">
              Smart Government Project Monitoring <span className="text-emerald-600">and Risk Management System</span>
            </span>
          </div>
          
          <div className="flex items-center space-x-6 pr-2">
            <Link href="#capabilities" className="text-sm font-semibold text-slate-600 hover:text-emerald-600 transition-colors hidden md:block">Capabilities</Link>
            <Link href="#workflows" className="text-sm font-semibold text-slate-600 hover:text-emerald-600 transition-colors hidden md:block">Workflows</Link>
            <button className="bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold py-2 px-6 rounded-full transition-transform hover:scale-105 active:scale-95 shadow-md flex items-center">
              Access Portal
              <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full ml-2"></div>
            </button>
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <main className="max-w-[1400px] mx-auto px-4 sm:px-6 pt-16 pb-24 md:pt-20 flex flex-col lg:flex-row items-center justify-between relative gap-8 lg:gap-6 xl:gap-2">
        
        {/* Left Column (Text & Stats) */}
        <div className="lg:w-[50%] xl:w-[40%] z-20 shrink-0">
          <h1 className="text-6xl lg:text-5xl xl:text-7xl font-extrabold tracking-tight leading-[1.05] mb-6">
            <span className="block text-slate-900">Smarter</span>
            <span className="block text-slate-900 mb-2">Monitoring.</span>
            <span className="block text-emerald-500">Stronger</span>
            <span className="block text-emerald-500">Infrastructure.</span>
          </h1>
          
          <p className="text-slate-600 text-base xl:text-lg leading-relaxed mb-10 max-w-lg font-medium">
            Smart Government Project Monitoring and Risk Management System leverages continuous project data to predict cost overruns, explain risk factors, detect anomalies and generate early warnings — empowering faster, data-driven decisions.
          </p>
          
          <div className="flex space-x-3 xl:space-x-4">
            <div className="bg-white p-4 xl:p-5 rounded-2xl shadow-sm border border-slate-100 flex-1 hover:-translate-y-1 transition-transform">
              <div className="bg-emerald-50 w-8 h-8 xl:w-10 xl:h-10 rounded-xl flex items-center justify-center mb-3 xl:mb-4">
                <BarChart3 className="text-emerald-500 w-4 h-4 xl:w-5 xl:h-5" />
              </div>
              <div className="text-xl xl:text-2xl font-extrabold text-slate-900">1,981+</div>
              <div className="text-[9px] xl:text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Active Projects</div>
            </div>
            
            <div className="bg-white p-4 xl:p-5 rounded-2xl shadow-sm border border-slate-100 flex-1 hover:-translate-y-1 transition-transform">
              <div className="bg-blue-50 w-8 h-8 xl:w-10 xl:h-10 rounded-xl flex items-center justify-center mb-3 xl:mb-4">
                <Building2 className="text-blue-500 w-4 h-4 xl:w-5 xl:h-5" />
              </div>
              <div className="text-xl xl:text-2xl font-extrabold text-slate-900">17</div>
              <div className="text-[9px] xl:text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Ministries</div>
            </div>
            
            <div className="bg-white p-4 xl:p-5 rounded-2xl shadow-sm border border-slate-100 flex-1 hover:-translate-y-1 transition-transform">
              <div className="bg-purple-50 w-8 h-8 xl:w-10 xl:h-10 rounded-xl flex items-center justify-center mb-3 xl:mb-4">
                <ShieldCheck className="text-purple-500 w-4 h-4 xl:w-5 xl:h-5" />
              </div>
              <div className="text-xl xl:text-2xl font-extrabold text-slate-900">98%</div>
              <div className="text-[9px] xl:text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">AI Accuracy</div>
            </div>
          </div>
        </div>

        {/* Center Decorative Floating Cards (Hidden on small screens) */}
        <div className="hidden xl:flex relative z-10 w-[240px] h-[500px] pointer-events-none shrink-0 items-center justify-center scale-90 2xl:scale-100 origin-center">
          {/* AI Risk Prediction Card */}
          <div className="absolute top-4 -left-4 bg-white p-4 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 w-44 animate-[float_6s_ease-in-out_infinite]">
            <div className="text-xs font-bold text-slate-700 mb-4 text-center">AI Risk Prediction</div>
            <div className="relative w-20 h-20 mx-auto mb-3">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#f1f5f9" strokeWidth="4" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#ef4444" strokeWidth="4" strokeDasharray="82, 100" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-extrabold text-slate-800">82</span>
              </div>
            </div>
            <div className="text-[10px] font-extrabold text-red-500 text-center uppercase tracking-widest bg-red-50 py-1 rounded-md">High Risk</div>
          </div>

          {/* SHAP Factors Card */}
          <div className="absolute top-36 -right-6 bg-white p-4 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 w-48 animate-[float_7s_ease-in-out_infinite_reverse]">
            <div className="flex justify-between items-center mb-3">
              <div className="text-xs font-bold text-slate-700">SHAP Factors</div>
              <Activity className="w-3 h-3 text-emerald-500" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center border-b border-slate-50 pb-2">
                <span className="text-[10px] font-medium text-slate-500">Milestone Delay</span>
                <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">+0.28</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-50 pb-2">
                <span className="text-[10px] font-medium text-slate-500">Progress Gap</span>
                <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">+0.22</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-medium text-slate-500">Cost Growth</span>
                <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">+0.16</span>
              </div>
            </div>
          </div>

          {/* Anomaly Detected Card */}
          <div className="absolute bottom-10 -left-2 bg-white p-4 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 w-52 animate-[float_8s_ease-in-out_infinite]">
            <div className="flex items-center space-x-2 mb-2">
              <div className="bg-red-50 p-1.5 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-red-500" />
              </div>
              <div className="text-[11px] font-bold text-slate-800">Anomaly Detected</div>
            </div>
            <p className="text-[9px] text-slate-500 leading-relaxed font-medium">
              Unusual cost increase in last 2 updates detected by AI models.
            </p>
          </div>
        </div>

        {/* Right Column (Login Panel) */}
        <div className="w-full max-w-md lg:max-w-none lg:w-[45%] xl:w-[35%] mt-16 lg:mt-0 z-20 shrink-0">
          <div className="bg-white rounded-[2rem] p-8 shadow-2xl shadow-slate-200/50 border border-slate-100 relative overflow-hidden">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-1">Secure Access</h2>
            <p className="text-sm font-medium text-slate-500 mb-8">Sign in to the intelligent monitoring portal</p>
            
            <form className="space-y-4 mb-6">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <User className="h-4 w-4 text-slate-400" />
                </div>
                <input 
                  type="email" 
                  placeholder="Email Address" 
                  className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border-none rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all outline-none"
                  defaultValue="demo@pragya.gov.in"
                />
              </div>
              
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-400" />
                </div>
                <input 
                  type="password" 
                  placeholder="Password" 
                  className="w-full pl-11 pr-12 py-3.5 bg-slate-50 border-none rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all outline-none"
                  defaultValue="password123"
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center cursor-pointer">
                  <Eye className="h-4 w-4 text-slate-400 hover:text-slate-600" />
                </div>
              </div>

              <div className="pt-2">
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Select Active Role</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Briefcase className="h-4 w-4 text-slate-400" />
                  </div>
                  <select className="w-full pl-11 pr-10 py-3.5 bg-slate-50 border-none rounded-xl text-sm font-semibold text-slate-800 appearance-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all outline-none cursor-pointer">
                    <option value="" disabled>Choose your role...</option>
                    <option value="admin">System Administrator</option>
                    <option value="ministry">Ministry Official</option>
                    <option value="officer">Field Officer</option>
                    <option value="public">Public Citizen</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
                    <ChevronDown className="h-4 w-4 text-slate-400" />
                  </div>
                </div>
              </div>

              <button 
                type="button"
                className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold py-4 rounded-xl mt-4 transition-transform hover:scale-[1.02] active:scale-95 flex items-center justify-center shadow-lg shadow-slate-900/20"
                onClick={() => handleDemoLogin('admin')}
              >
                Authenticate to Portal <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </form>

            <div className="relative flex items-center py-4">
              <div className="flex-grow border-t border-slate-100 border-dashed"></div>
              <span className="flex-shrink-0 mx-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest">1-Click Demo Login</span>
              <div className="flex-grow border-t border-slate-100 border-dashed"></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button onClick={() => handleDemoLogin('admin')} className="flex items-center justify-center space-x-2 py-3 border border-slate-200 rounded-xl hover:border-emerald-500 hover:bg-emerald-50 transition-colors group">
                <ShieldCheck className="w-4 h-4 text-slate-500 group-hover:text-emerald-600" />
                <span className="text-xs font-bold text-slate-700 group-hover:text-emerald-700">Admin</span>
              </button>
              <button onClick={() => handleDemoLogin('ministry')} className="flex items-center justify-center space-x-2 py-3 border border-slate-200 rounded-xl hover:border-emerald-500 hover:bg-emerald-50 transition-colors group">
                <Building2 className="w-4 h-4 text-slate-500 group-hover:text-emerald-600" />
                <span className="text-xs font-bold text-slate-700 group-hover:text-emerald-700">Ministry</span>
              </button>
              <button onClick={() => handleDemoLogin('officer')} className="flex items-center justify-center space-x-2 py-3 border border-slate-200 rounded-xl hover:border-emerald-500 hover:bg-emerald-50 transition-colors group">
                <Briefcase className="w-4 h-4 text-slate-500 group-hover:text-emerald-600" />
                <span className="text-xs font-bold text-slate-700 group-hover:text-emerald-700">Officer</span>
              </button>
              <button onClick={() => handleDemoLogin('public')} className="flex items-center justify-center space-x-2 py-3 border border-slate-200 rounded-xl hover:border-emerald-500 hover:bg-emerald-50 transition-colors group">
                <User className="w-4 h-4 text-slate-500 group-hover:text-emerald-600" />
                <span className="text-xs font-bold text-slate-700 group-hover:text-emerald-700">Public</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Scroll Down Indicator */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center animate-bounce opacity-70">
        <span className="text-[10px] font-extrabold text-emerald-600 uppercase tracking-widest mb-1">Scroll to Explore</span>
        <ChevronDown className="w-4 h-4 text-emerald-600" />
      </div>
    </div>
  );
}
