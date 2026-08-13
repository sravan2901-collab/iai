import React from 'react';
import { BookOpen, Flame, Award, LogIn, LogOut, User, Compass, ShieldCheck, Volume2, Lock } from 'lucide-react';
import VoiceGuide from './VoiceGuide';

export default function Navbar({ activeTab, setActiveTab, learner, isNewRegistration, onOpenAuth, onLogout }) {
  const handleTabClick = (tabKey) => {
    if (!learner?.isLoggedIn) {
      if (['diagnostic', 'learning-path', 'dashboard'].includes(tabKey)) {
        onOpenAuth();
        return;
      }
    }
    
    if (isNewRegistration && tabKey !== 'diagnostic') {
      alert("Mandatory Placement Test: Please complete your 9-question initial diagnostic test first to evaluate your literacy level and unlock all learning path features!");
      return;
    }
    
    setActiveTab(tabKey);
  };

  return (
    <header className="border-b border-slate-800 bg-[#0b132b]/95 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        
        {/* Brand Logo & Milestone Status */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => !isNewRegistration && setActiveTab('catalog')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-bold text-xl text-slate-950 shadow-lg shadow-emerald-500/20">
            A
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg text-white tracking-tight">AksharAI</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Milestone 1
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">AI-Powered Multilingual Literacy Platform</p>
          </div>
        </div>

        {/* Global Controls & Navbar Action Buttons */}
        <div className="flex items-center gap-3">
          <VoiceGuide />

          {/* User Auth Status Header Badge */}
          {learner?.isLoggedIn ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20 font-semibold">
                <Flame size={14} className="text-amber-400" />
                <span>{learner.streak_count || 1} Day Streak</span>
              </div>
              <button
                onClick={onLogout}
                className="flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-rose-300 hover:bg-rose-950/30 hover:border-rose-500/40 transition-all"
              >
                <LogOut size={14} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 text-xs font-bold px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/30 transition-all"
            >
              <LogIn size={16} />
              <span>Login / Register</span>
            </button>
          )}

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => handleTabClick('catalog')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                activeTab === 'catalog' 
                  ? 'bg-emerald-600 text-white' 
                  : isNewRegistration 
                  ? 'text-slate-500 opacity-50 cursor-not-allowed' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {isNewRegistration && <Lock size={10} className="text-amber-400" />}
              <span>Curriculum</span>
            </button>

            <button
              onClick={() => handleTabClick('diagnostic')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'diagnostic' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30' : 'text-slate-400 hover:text-white'
              }`}
            >
              Diagnostic Test
            </button>

            <button
              onClick={() => handleTabClick('benchmarks')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                activeTab === 'benchmarks' 
                  ? 'bg-emerald-600 text-white' 
                  : isNewRegistration 
                  ? 'text-slate-500 opacity-50 cursor-not-allowed' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {isNewRegistration && <Lock size={10} className="text-amber-400" />}
              <span>Benchmarks</span>
            </button>

            <button
              onClick={() => handleTabClick('learning-path')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                activeTab === 'learning-path' 
                  ? 'bg-emerald-600 text-white' 
                  : isNewRegistration 
                  ? 'text-slate-500 opacity-50 cursor-not-allowed' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {isNewRegistration && <Lock size={10} className="text-amber-400" />}
              <span>Learning Path</span>
            </button>

            <button
              onClick={() => handleTabClick('dashboard')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                activeTab === 'dashboard' 
                  ? 'bg-emerald-600 text-white' 
                  : isNewRegistration 
                  ? 'text-slate-500 opacity-50 cursor-not-allowed' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {isNewRegistration && <Lock size={10} className="text-amber-400" />}
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => handleTabClick('admin')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                activeTab === 'admin' 
                  ? 'bg-emerald-600 text-white' 
                  : isNewRegistration 
                  ? 'text-slate-500 opacity-50 cursor-not-allowed' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {isNewRegistration && <Lock size={10} className="text-amber-400" />}
              <span>Admin Panel</span>
            </button>
          </div>
        </div>

      </div>
    </header>
  );
}
