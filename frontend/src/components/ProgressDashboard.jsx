import React, { useState, useEffect, useCallback } from 'react';
import { 
  Flame, Award, TrendingUp, BookOpen, Mic, Brain, 
  CheckCircle2, Lock, Unlock, Clock, Sparkles, RefreshCw, 
  AlertCircle, ChevronRight, BarChart3, Star, Layers, Activity
} from 'lucide-react';
import { apiRequest } from '../services/api';

/**
 * Custom SVG Circular Progress Ring (Zero external charting dependencies)
 */
function CircularProgress({ percentage = 0, size = 110, strokeWidth = 10, color = "#10b981", label = "" }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(Math.max(percentage, 0), 100) / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1e293b"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress fill */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-xl font-black text-white tracking-tight">{Math.round(percentage)}%</span>
        {label && <span className="text-[10px] text-slate-400 font-medium -mt-0.5">{label}</span>}
      </div>
    </div>
  );
}

/**
 * Custom Mini Sparkline / Bar Visualization for Voice Scores
 */
function VoiceScoreBarChart({ history = [] }) {
  if (!history || history.length === 0) {
    return (
      <div className="py-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800">
        <Mic size={24} className="mx-auto text-slate-600 mb-2 opacity-60" />
        <p>No voice practice sessions recorded yet.</p>
        <p className="text-slate-500 mt-1">Practice pronunciation in the Curriculum to see phoneme accuracy trends here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Bars row */}
      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
        <span className="text-xs text-slate-400 font-semibold mb-3 block">
          Recent Pronunciation Accuracy Trends (Last {history.length} attempts):
        </span>
        <div className="flex items-end justify-between gap-2 h-28 pt-2 px-1">
          {history.map((item, idx) => {
            const score = Number(item.overall_score) || 0;
            const heightPct = Math.max(score, 8);
            let barColor = "bg-rose-500 hover:bg-rose-400";
            let textColor = "text-rose-400";

            if (score >= 80) {
              barColor = "bg-emerald-500 hover:bg-emerald-400";
              textColor = "text-emerald-400";
            } else if (score >= 50) {
              barColor = "bg-amber-500 hover:bg-amber-400";
              textColor = "text-amber-400";
            }

            return (
              <div key={item.score_id || idx} className="flex-1 flex flex-col items-center h-full justify-end group relative">
                {/* Tooltip on hover */}
                <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col items-center z-20 pointer-events-none">
                  <div className="bg-slate-950 text-white text-[11px] p-2 rounded-lg shadow-xl border border-slate-700 whitespace-nowrap space-y-0.5">
                    <p className="font-bold text-emerald-300">Score: {score}%</p>
                    {item.phoneme_accuracy !== undefined && <p className="text-slate-300">Phonemes: {item.phoneme_accuracy}%</p>}
                    {item.syllable_score !== undefined && <p className="text-slate-300">Syllables: {item.syllable_score}%</p>}
                    {item.recognized_text && <p className="text-slate-400 italic truncate max-w-[140px]">"{item.recognized_text}"</p>}
                  </div>
                  <div className="w-2 h-2 bg-slate-950 rotate-45 -mt-1 border-r border-b border-slate-700"></div>
                </div>

                <span className={`text-[10px] font-bold ${textColor} mb-1 opacity-90`}>
                  {Math.round(score)}%
                </span>
                <div 
                  className={`w-full max-w-[32px] rounded-t-md ${barColor} transition-all duration-500 shadow-sm`}
                  style={{ height: `${heightPct}%` }}
                />
                <span className="text-[9px] text-slate-500 mt-1 font-mono">
                  #{history.length - idx}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* History table list */}
      <div className="space-y-2">
        {history.slice(0, 5).map((item, idx) => (
          <div key={item.score_id || idx} className="bg-slate-900/40 hover:bg-slate-900/70 p-3 rounded-xl border border-slate-800 flex items-center justify-between gap-3 text-xs transition-all">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                (item.overall_score || 0) >= 80 
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                  : (item.overall_score || 0) >= 50 
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
                  : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
              }`}>
                {Math.round(item.overall_score || 0)}%
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-slate-200 truncate">
                  {item.recognized_text ? `"${item.recognized_text}"` : `Voice Practice #${item.score_id}`}
                </p>
                <div className="flex items-center gap-3 text-[10px] text-slate-400 mt-0.5">
                  <span>Phoneme Acc: <strong className="text-slate-300">{item.phoneme_accuracy || 0}%</strong></span>
                  <span>Syllables: <strong className="text-slate-300">{item.syllable_score || 0}%</strong></span>
                </div>
              </div>
            </div>

            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
              (item.overall_score || 0) >= 80 
                ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/20' 
                : (item.overall_score || 0) >= 50 
                ? 'bg-amber-950/60 text-amber-400 border border-amber-500/20' 
                : 'bg-rose-950/60 text-rose-400 border border-rose-500/20'
            }`}>
              {(item.overall_score || 0) >= 80 ? 'Mastered' : (item.overall_score || 0) >= 50 ? 'Proficient' : 'Developing'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ProgressDashboard({ learner, onSelectLesson }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [lessonHistory, setLessonHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);
    setErrorMsg('');

    try {
      // 1. Fetch main progress dashboard aggregation
      const data = await apiRequest('/progress/dashboard');
      setDashboardData(data);

      // 2. Fetch completed lesson history
      try {
        const historyData = await apiRequest('/progress/history');
        if (Array.isArray(historyData)) {
          setLessonHistory(historyData);
        } else if (historyData && Array.isArray(historyData.history)) {
          setLessonHistory(historyData.history);
        }
      } catch (hErr) {
        console.warn('Lesson history notice:', hErr.message);
      }
    } catch (err) {
      console.error('Progress dashboard fetch error:', err);
      setErrorMsg(err.message || 'Failed to load progress analytics. Please check server connectivity.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="glass-panel max-w-5xl mx-auto rounded-2xl p-12 text-center my-8 space-y-4 border border-slate-800">
        <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-500 animate-spin mx-auto" />
        <h3 className="text-xl font-bold text-white">Aggregating Learner Analytics...</h3>
        <p className="text-xs text-slate-400">Loading skill mastery, voice practice history, and learning path progress.</p>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="glass-panel max-w-xl mx-auto rounded-2xl p-8 text-center my-8 space-y-4 border border-rose-500/30 bg-rose-950/20">
        <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto border border-rose-500/30">
          <AlertCircle size={24} />
        </div>
        <h3 className="text-lg font-bold text-white">Unable to Load Progress Dashboard</h3>
        <p className="text-xs text-rose-300">{errorMsg}</p>
        <button
          onClick={() => fetchDashboardData(true)}
          className="glass-button px-6 py-2.5 rounded-xl font-bold text-xs text-emerald-300 hover:text-white flex items-center gap-2 mx-auto"
        >
          <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  const profile = dashboardData?.profile || {};
  const pathStats = dashboardData?.path_stats || {};
  const moduleProgress = dashboardData?.module_progress || [];
  const voiceHistory = dashboardData?.voice_history || [];
  const achievements = dashboardData?.achievements || [];
  const streakCount = dashboardData?.streak_count ?? profile.streak_count ?? 1;
  const totalPoints = dashboardData?.total_points ?? profile.total_points ?? 0;

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto pb-12">
      
      {/* 0. Header & Control Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-700/60 bg-gradient-to-r from-slate-900/90 via-emerald-950/20 to-slate-900/90 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="space-y-1 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2 flex-wrap">
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <Activity size={12} /> Live Learning Analytics
            </span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Language: {dashboardData?.language || 'English'}
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            {dashboardData?.learner_name || learner?.name || 'Learner'}'s Progress Dashboard
          </h2>
          <p className="text-xs md:text-sm text-slate-300">
            Real-time multi-tier phonemic scores, skill mastery breakdown, and curriculum milestones.
          </p>
        </div>

        <button
          onClick={() => fetchDashboardData(true)}
          disabled={refreshing}
          className="glass-button px-4 py-2.5 rounded-xl font-semibold text-xs text-slate-300 hover:text-white flex items-center gap-2 self-center md:self-auto"
          title="Refresh latest progress data"
        >
          <RefreshCw size={14} className={refreshing ? "animate-spin text-emerald-400" : "text-slate-400"} />
          <span>{refreshing ? 'Updating...' : 'Sync Stats'}</span>
        </button>
      </div>

      {/* 1. Stat Tiles Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Streak Tile */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/70 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl group-hover:bg-amber-500/20 transition-all" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Daily Streak</span>
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30">
              <Flame size={18} />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-3xl font-extrabold text-white">{streakCount}</h3>
            <p className="text-[11px] text-amber-300 font-medium">Days active & practicing</p>
          </div>
        </div>

        {/* Total Points / XP Tile */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/70 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-all" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Points</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
              <Star size={18} />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-3xl font-extrabold text-white">{totalPoints}</h3>
            <p className="text-[11px] text-emerald-300 font-medium">Earned Literacy XP</p>
          </div>
        </div>

        {/* Literacy Level Tier */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/70 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-teal-500/10 rounded-full blur-2xl group-hover:bg-teal-500/20 transition-all" />
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Proficiency Tier</span>
            <div className="w-8 h-8 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center border border-teal-500/30">
              <Award size={18} />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-xl md:text-2xl font-extrabold text-white capitalize truncate">
              {profile.literacy_level || 'FOUNDATIONAL'}
            </h3>
            <p className="text-[11px] text-teal-300 font-medium">Bilingual placement tier</p>
          </div>
        </div>

        {/* Overall Mastery Ring */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/70 flex items-center justify-between relative overflow-hidden group">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">Overall Mastery</span>
            <h3 className="text-2xl font-extrabold text-white">{profile.overall_pct || 0}%</h3>
            <p className="text-[11px] text-emerald-300 font-medium">Composite score</p>
          </div>
          <CircularProgress 
            percentage={profile.overall_pct || 0} 
            size={68} 
            strokeWidth={7} 
            color="#10b981" 
          />
        </div>
      </div>

      {/* 2. Skill Breakdown Row (3 Core Pillars) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart3 size={20} className="text-emerald-400" />
            <span>3-Pillar Skill Mastery Breakdown</span>
          </h3>
          <span className="text-xs text-slate-400">Diagnostic & practice evaluated</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Reading & Phonics */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center border border-blue-500/30">
                  <BookOpen size={18} />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white">Reading & Phonics</h4>
                  <span className="text-[10px] text-slate-400">Alphabet & sight words</span>
                </div>
              </div>
              <span className="text-lg font-black text-blue-400">{profile.reading_pct || 0}%</span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-blue-600 to-cyan-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${Math.min(profile.reading_pct || 0, 100)}%` }}
              />
            </div>
            <p className="text-xs text-slate-400">
              {(profile.reading_pct || 0) >= 80 ? '🌟 Excellent letter & word recognition' : (profile.reading_pct || 0) >= 50 ? '👍 Good foundational decoding' : '🎯 Practice reading modules recommended'}
            </p>
          </div>

          {/* Comprehension & Syntax */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30">
                  <Brain size={18} />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white">Comprehension</h4>
                  <span className="text-[10px] text-slate-400">Vocabulary & context</span>
                </div>
              </div>
              <span className="text-lg font-black text-purple-400">{profile.comprehension_pct || 0}%</span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-purple-600 to-pink-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${Math.min(profile.comprehension_pct || 0, 100)}%` }}
              />
            </div>
            <p className="text-xs text-slate-400">
              {(profile.comprehension_pct || 0) >= 80 ? '🧠 Strong contextual understanding' : (profile.comprehension_pct || 0) >= 50 ? '📚 Steady comprehension progression' : '🎯 Complete story & sentence exercises'}
            </p>
          </div>

          {/* Pronunciation & Voice */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                  <Mic size={18} />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white">Pronunciation & Voice</h4>
                  <span className="text-[10px] text-slate-400">Sarvam Saaras STT evaluated</span>
                </div>
              </div>
              <span className="text-lg font-black text-emerald-400">{profile.voice_pct || 0}%</span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-emerald-600 to-teal-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${Math.min(profile.voice_pct || 0, 100)}%` }}
              />
            </div>
            <p className="text-xs text-slate-400">
              {(profile.voice_pct || 0) >= 80 ? '🎙️ High phonemic acoustic clarity' : (profile.voice_pct || 0) >= 50 ? '🗣️ Clear pronunciation rhythm' : '🎯 Use Voice Coach in lesson practice'}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Learning Path Progress Track */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp size={20} className="text-teal-400" />
              <span>Personalized Learning Path Milestones</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Adaptive curriculum progression dynamically generated for your proficiency tier.
            </p>
          </div>
          <span className="text-xs font-bold px-3 py-1 bg-teal-500/20 text-teal-300 rounded-full border border-teal-500/30">
            {pathStats.current_level || 'FOUNDATIONAL'} Tier Path
          </span>
        </div>

        {/* Main completion bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-slate-300">Curriculum Completion</span>
            <span className="text-emerald-400 font-bold text-sm">{Math.round(pathStats.completion_percentage || 0)}%</span>
          </div>
          <div className="w-full bg-slate-800/90 rounded-full h-3.5 p-0.5 border border-slate-700/60 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 h-full rounded-full transition-all duration-1000 shadow-md shadow-emerald-500/30"
              style={{ width: `${Math.min(pathStats.completion_percentage || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* 4 Status Breakdown Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
          <div className="bg-slate-900/90 p-3 rounded-xl border border-emerald-500/20 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">
              <CheckCircle2 size={16} />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Completed</span>
              <span className="text-base font-extrabold text-white">{pathStats.completed_lessons || 0}</span>
            </div>
          </div>

          <div className="bg-slate-900/90 p-3 rounded-xl border border-amber-500/20 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-sm">
              <Activity size={16} />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">In Progress</span>
              <span className="text-base font-extrabold text-white">{pathStats.in_progress_lessons || 0}</span>
            </div>
          </div>

          <div className="bg-slate-900/90 p-3 rounded-xl border border-blue-500/20 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">
              <Unlock size={16} />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Unlocked</span>
              <span className="text-base font-extrabold text-white">{pathStats.unlocked_lessons || 0}</span>
            </div>
          </div>

          <div className="bg-slate-900/90 p-3 rounded-xl border border-slate-700/60 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 flex items-center justify-center font-bold text-sm">
              <Lock size={16} />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Locked</span>
              <span className="text-base font-extrabold text-white">{pathStats.locked_lessons || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4 & 5. Module Progress & Voice Practice History (2-column layout on desktop) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Module-by-Module Progress */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Layers size={18} className="text-emerald-400" />
              <span>Module-by-Module Mastery</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">
              {moduleProgress.length} Modules Active
            </span>
          </div>

          {moduleProgress.length === 0 ? (
            <div className="py-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800">
              <Layers size={24} className="mx-auto text-slate-600 mb-2 opacity-60" />
              <p>No module tracking entries yet.</p>
              <p className="text-slate-500 mt-1">Start practicing in the Curriculum to track module completion.</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {moduleProgress.map((mod, idx) => (
                <div key={mod.module_id || idx} className="bg-slate-900/50 hover:bg-slate-900/80 p-3.5 rounded-xl border border-slate-800/80 space-y-2 transition-all">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-xs font-bold text-slate-200 truncate">{mod.module_name}</span>
                      <span className="text-[9px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-emerald-300 border border-emerald-500/20 whitespace-nowrap">
                        {mod.skill_type || 'LITERACY'}
                      </span>
                    </div>
                    <span className="text-xs font-black text-emerald-400">{Math.round(mod.completion_percent || 0)}%</span>
                  </div>

                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-700"
                      style={{ width: `${Math.min(mod.completion_percent || 0, 100)}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <Clock size={11} className="text-slate-500" />
                      <span>{mod.time_spent_min || 0} min spent</span>
                    </span>
                    <span>{mod.completion_percent >= 100 ? '✅ Completed' : '🔄 In Progress'}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Voice Practice & Phoneme Analytics */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Mic size={18} className="text-emerald-400" />
              <span>Voice & Pronunciation History</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">
              Sarvam AI Powered
            </span>
          </div>

          <VoiceScoreBarChart history={voiceHistory} />
        </div>
      </div>

      {/* 6. Recent Lesson Activity Stream */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Clock size={18} className="text-teal-400" />
            <span>Completed Lesson History</span>
          </h3>
          <span className="text-xs text-slate-400">{lessonHistory.length} Recent Activities</span>
        </div>

        {lessonHistory.length === 0 ? (
          <div className="py-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800">
            <BookOpen size={24} className="mx-auto text-slate-600 mb-2 opacity-60" />
            <p>No completed lessons recorded yet.</p>
            <p className="text-slate-500 mt-1">Select a lesson in Curriculum to begin your interactive literacy journey.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {lessonHistory.slice(0, 6).map((item, idx) => (
              <div key={idx} className="bg-slate-900/50 p-3.5 rounded-xl border border-slate-800 flex items-center justify-between gap-3 text-xs">
                <div className="space-y-0.5 min-w-0">
                  <h5 className="font-bold text-slate-200 truncate">{item.lesson_title || item.title || `Lesson #${item.lesson_id}`}</h5>
                  <p className="text-[10px] text-slate-400 truncate">{item.module_name || 'Curriculum Module'}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {item.score !== undefined ? `${Math.round(item.score)}%` : 'Passed'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 7. Earned Badges & Achievements */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Award size={18} className="text-amber-400" />
            <span>Earned Achievements & Literacy Badges</span>
          </h3>
          <span className="text-xs text-slate-400">{achievements.length} Badges Unlocked</span>
        </div>

        {achievements.length === 0 ? (
          <div className="py-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800/80 space-y-2">
            <Award size={32} className="mx-auto text-amber-500/40" />
            <p className="font-bold text-slate-300">Complete milestones to unlock badges!</p>
            <p className="text-[11px] text-slate-500 max-w-md mx-auto">
              Earn badges for daily practice streaks, scoring 100% on pronunciation practice, and completing curriculum tiers.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {achievements.map((ach, idx) => (
              <div key={ach.achievement_id || idx} className="bg-gradient-to-br from-slate-900/90 to-amber-950/20 p-4 rounded-xl border border-amber-500/30 space-y-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30 shadow-md">
                    <Award size={20} />
                  </div>
                  <div>
                    <h5 className="font-bold text-sm text-white">{ach.achievement_name}</h5>
                    <span className="text-[10px] text-amber-300 font-mono">
                      {ach.earned_on ? new Date(ach.earned_on).toLocaleDateString() : 'Earned'}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{ach.description || ach.criteria}</p>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
