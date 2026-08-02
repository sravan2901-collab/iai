import React from 'react';
import { BookOpen, Flame, Award, LogIn, LogOut, User, Compass } from 'lucide-react';
import VoiceGuide from './VoiceGuide';

export default function Navbar({ activeTab, setActiveTab, learner, onOpenAuth, onLogout }) {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-700/60 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('catalog')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-bold text-white shadow-md shadow-emerald-500/20 text-xl">
            A
          </div>
          <div>
            <h1 className="font-bold text-lg text-white leading-tight flex items-center gap-1.5">
              AksharAI
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Milestone 1
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 hidden sm:block">AI-Powered Multilingual Literacy Platform</p>
          </div>
        </div>

        {/* Global Controls & Gamification Counters */}
        <div className="flex items-center gap-3">
          <VoiceGuide />

          {learner?.isLoggedIn ? (
            <>
              <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700 text-xs">
                <Flame size={15} className="text-amber-500 fill-amber-500 animate-bounce" />
                <span className="font-bold text-amber-400">{learner?.streak_count || 1} Day Streak</span>
              </div>

              <button
                onClick={onLogout}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-xl flex items-center gap-1.5 text-xs font-semibold"
                title="Logout"
              >
                <LogOut size={16} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl flex items-center gap-2 text-xs font-bold shadow-md shadow-emerald-600/30 transition-all"
            >
              <LogIn size={16} />
              <span>Login / Register</span>
            </button>
          )}

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('catalog')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'catalog' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Curriculum
            </button>

            <button
              onClick={() => setActiveTab('diagnostic')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'diagnostic' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Diagnostic Test
            </button>

            <button
              onClick={() => setActiveTab('learning-path')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'learning-path' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Learning Path
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'dashboard' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Dashboard
            </button>
          </div>
        </div>

      </div>
    </header>
  );
}
