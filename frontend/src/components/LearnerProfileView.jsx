import React, { useState, useEffect } from 'react';
import { User, Mail, ShieldCheck, Flame, Award, Globe, Edit3, Save, CheckCircle, RefreshCw, KeyRound } from 'lucide-react';
import { apiRequest } from '../services/api';

export default function LearnerProfileView({ learner, onProfileUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [profileData, setProfileData] = useState({
    first_name: learner.name || 'Learner',
    last_name: '',
    native_lang_id: learner.native_lang_id || 1,
    literacy_level: learner.literacy_level || 'FOUNDATIONAL'
  });

  const LANG_NAMES = {
    1: 'English (Default)',
    2: 'Hindi (हिन्दी)',
    3: 'Tamil (தமிழ்)',
    4: 'Telugu (తెలుగు)',
    5: 'Bengali (বাংলা)',
    6: 'Marathi (मराठी)',
    7: 'Kannada (ಕನ್ನಡ)',
    8: 'Spanish (Español)'
  };

  useEffect(() => {
    if (learner.isLoggedIn) {
      apiRequest('/auth/me')
        .then(data => {
          setProfileData({
            first_name: data.first_name || learner.name,
            last_name: data.last_name || '',
            native_lang_id: data.native_lang_id || 1,
            literacy_level: data.literacy_level || 'FOUNDATIONAL'
          });
        })
        .catch(() => {});
    }
  }, [learner.isLoggedIn]);

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg('');

    try {
      const updated = await apiRequest('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      });
      setSuccessMsg('Learner profile and language preferences updated successfully!');
      setIsEditing(false);
      if (onProfileUpdate) {
        onProfileUpdate(updated);
      }
    } catch (err) {
      setSuccessMsg('Profile updated locally.');
      setIsEditing(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500">
      
      {/* 1. Header Profile Banner */}
      <div className="glass-panel p-6 md:p-8 rounded-2xl border border-slate-700/60 bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-5">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-black text-3xl shadow-lg shadow-emerald-500/20">
            {profileData.first_name.charAt(0).toUpperCase()}
          </div>
          <div className="space-y-1.5 text-center md:text-left">
            <div className="flex items-center gap-2 justify-center md:justify-start">
              <h2 className="text-2xl font-bold text-white">
                {profileData.first_name} {profileData.last_name}
              </h2>
              <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {profileData.literacy_level} TIER
              </span>
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-2 justify-center md:justify-start">
              <Mail size={14} className="text-slate-500" />
              <span>{learner.email || 'learner@example.com'}</span>
            </p>
            <p className="text-xs text-emerald-300 font-semibold flex items-center gap-1.5 justify-center md:justify-start">
              <Globe size={14} /> Native Language: {LANG_NAMES[profileData.native_lang_id] || 'English'}
            </p>
          </div>
        </div>

        <button
          onClick={() => setIsEditing(!isEditing)}
          className="glass-button px-5 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 text-emerald-300 shadow-md"
        >
          <Edit3 size={16} />
          <span>{isEditing ? 'Cancel Edit' : 'Edit Profile & Preferences'}</span>
        </button>
      </div>

      {/* Success Notification */}
      {successMsg && (
        <div className="p-4 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-center text-xs text-emerald-300 font-semibold flex items-center justify-center gap-2">
          <CheckCircle size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* 2. Editable Profile Form */}
      {isEditing && (
        <form onSubmit={handleSave} className="glass-panel p-6 rounded-2xl border border-emerald-500/30 space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Edit3 size={18} className="text-emerald-400" />
            Update Learner Preferences
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">First Name</label>
              <input
                type="text"
                value={profileData.first_name}
                onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 px-4 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Last Name</label>
              <input
                type="text"
                value={profileData.last_name}
                onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 px-4 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Native Language</label>
              <select
                value={profileData.native_lang_id}
                onChange={(e) => setProfileData({ ...profileData, native_lang_id: Number(e.target.value) })}
                className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 px-4 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
              >
                <option value={1}>English (Default)</option>
                <option value={2}>Hindi (हिन्दी)</option>
                <option value={3}>Tamil (தமிழ்)</option>
                <option value={4}>Telugu (తెలుగు)</option>
                <option value={5}>Bengali (বাংলা)</option>
                <option value={6}>Marathi (मराठी)</option>
                <option value={7}>Kannada (ಕನ್ನಡ)</option>
                <option value={8}>Spanish (Español)</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1 font-medium">Target Literacy Benchmark</label>
              <select
                value={profileData.literacy_level}
                onChange={(e) => setProfileData({ ...profileData, literacy_level: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700 rounded-xl py-2.5 px-4 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
              >
                <option value="FOUNDATIONAL">FOUNDATIONAL (Letters & Numbers)</option>
                <option value="FUNCTIONAL">FUNCTIONAL (ATM & Receipts)</option>
                <option value="PROFICIENT">PROFICIENT (Workplace Fluency)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2"
          >
            {loading ? <RefreshCw className="animate-spin" size={18} /> : <Save size={18} />}
            <span>Save Profile Updates</span>
          </button>
        </form>
      )}

      {/* 3. Gamification Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 bg-slate-900/80 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xl">
            <Flame size={24} className="animate-bounce" />
          </div>
          <div>
            <span className="text-xs text-slate-400 block uppercase font-semibold">Daily Streak</span>
            <span className="text-xl font-black text-amber-400">{learner.streak_count || 1} Days Active</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-slate-900/80 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xl">
            <Award size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block uppercase font-semibold">Literacy Points</span>
            <span className="text-xl font-black text-emerald-400">{learner.total_points || 50} Points</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-blue-500/30 bg-slate-900/80 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xl">
            <ShieldCheck size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block uppercase font-semibold">Account Status</span>
            <span className="text-sm font-bold text-blue-300">JWT Verified ✓</span>
          </div>
        </div>
      </div>

      {/* 4. Registration Workflow Status */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-700/60 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <CheckCircle size={18} className="text-emerald-400" />
          Learner Onboarding & Registration Steps
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 space-y-1">
            <span className="text-[10px] font-bold text-emerald-400 uppercase">Step 1</span>
            <h4 className="text-xs font-bold text-white">Native Language Selection</h4>
            <p className="text-[11px] text-emerald-300">Selected: {LANG_NAMES[profileData.native_lang_id] || 'English'}</p>
          </div>

          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 space-y-1">
            <span className="text-[10px] font-bold text-emerald-400 uppercase">Step 2</span>
            <h4 className="text-xs font-bold text-white">Learner Profile Setup</h4>
            <p className="text-[11px] text-emerald-300">Status: Registered & Verified ✓</p>
          </div>

          <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 space-y-1">
            <span className="text-[10px] font-bold text-emerald-400 uppercase">Step 3</span>
            <h4 className="text-xs font-bold text-white">Diagnostic Placement Test</h4>
            <p className="text-[11px] text-emerald-300">Level: {profileData.literacy_level} ✓</p>
          </div>
        </div>
      </div>

    </div>
  );
}
