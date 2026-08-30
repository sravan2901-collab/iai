import React, { useState, useEffect, useCallback } from 'react';
import { 
  FileText, Sparkles, AlertCircle, RefreshCw, Calendar, 
  Award, TrendingUp, BookOpen, Mic, Brain, Flame, Star, 
  ChevronRight, CheckCircle2, Layers, Clock, ArrowRight, User
} from 'lucide-react';
import { apiRequest } from '../services/api';
import RecommendationsPanel from './RecommendationsPanel';

export default function LearningReportView({ learner, onSelectLesson }) {
  const [activeReport, setActiveReport] = useState(null);
  const [reportHistory, setReportHistory] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [historyError, setHistoryError] = useState('');

  // Fetch report history on mount
  const fetchReportHistory = useCallback(async () => {
    setLoadingHistory(true);
    setHistoryError('');
    try {
      const history = await apiRequest('/reports/history');
      if (Array.isArray(history)) {
        setReportHistory(history);
        // If no active report yet, auto-load the most recent one
        if (history.length > 0) {
          loadReportDetail(history[0].report_id);
        }
      }
    } catch (err) {
      console.error('Report history error:', err);
      setHistoryError(err.message || 'Failed to load report history.');
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  const loadReportDetail = async (reportId) => {
    try {
      const detail = await apiRequest(`/reports/${reportId}`);
      if (detail && detail.report_id) {
        setActiveReport(detail);
      }
    } catch (err) {
      console.error('Load report detail error:', err);
    }
  };

  useEffect(() => {
    fetchReportHistory();
  }, [fetchReportHistory]);

  // Generate new report
  const handleGenerateReport = async () => {
    setGenerating(true);
    setErrorMsg('');
    try {
      const newReport = await apiRequest('/reports/generate', {
        method: 'POST'
      });
      if (newReport && newReport.report_id) {
        setActiveReport(newReport);
        // Prepend to history
        setReportHistory(prev => [
          {
            report_id: newReport.report_id,
            reporting_period: newReport.reporting_period,
            overall_progress: newReport.overall_progress,
            generated_at: newReport.generated_at,
            has_narrative: bool(newReport.narrative)
          },
          ...prev.filter(r => r.report_id !== newReport.report_id)
        ]);
      }
    } catch (err) {
      console.error('Generate report error:', err);
      setErrorMsg(err.message || 'Unable to generate report. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const bool = (val) => !!val;

  const snapshot = activeReport?.snapshot || {};
  const profile = snapshot.profile || {};
  const pathStats = snapshot.path_stats || {};
  const streak = snapshot.streak_count ?? profile.streak_count ?? 1;
  const points = snapshot.total_points ?? profile.total_points ?? 0;

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto pb-12">
      
      {/* 1. Header & Generate Report Action Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-700/60 bg-gradient-to-r from-slate-900/95 via-teal-950/30 to-slate-900/95 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2 flex-wrap">
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-400 border border-teal-500/30 flex items-center gap-1">
              <FileText size={12} /> AI Pedagogical Evaluation
            </span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
              Language: {snapshot.language || learner?.preferred_lang?.toUpperCase() || 'EN'}
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Learning Reports & AI Interventions
          </h2>
          <p className="text-xs md:text-sm text-slate-300 max-w-2xl">
            Synthesizes your pronunciation acoustic clarity, reading accuracy, and curriculum completion into comprehensive pedagogical assessments.
          </p>
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={generating}
          className="py-3.5 px-6 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-2 flex-shrink-0 disabled:opacity-50 cursor-pointer"
        >
          <Sparkles size={18} className={generating ? 'animate-spin' : ''} />
          <span>{generating ? 'Generating AI Report...' : 'Generate New Learning Report'}</span>
        </button>
      </div>

      {errorMsg && (
        <div className="glass-panel p-4 rounded-xl border border-rose-500/30 bg-rose-950/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle size={16} className="text-rose-400 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 2. Active Report Display */}
      {activeReport ? (
        <div className="space-y-6">
          
          {/* AI Narrative Card */}
          <div className="glass-panel p-6 md:p-8 rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-slate-900/90 via-emerald-950/20 to-slate-900/90 shadow-xl space-y-4 relative overflow-hidden">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h3 className="font-extrabold text-lg text-white">AI Pedagogical Narrative</h3>
                  <span className="text-[11px] text-slate-400">
                    Generated on {new Date(activeReport.generated_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
                  </span>
                </div>
              </div>
              <span className="text-xs font-mono font-bold px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30">
                Overall: {Math.round(activeReport.overall_progress || 0)}%
              </span>
            </div>

            <div className="bg-slate-950/70 p-5 rounded-xl border border-slate-800 text-slate-200 text-sm leading-relaxed italic border-l-4 border-l-emerald-500">
              "{activeReport.narrative || 'The learner continues to demonstrate positive engagement across literacy modules. Consistent daily practice in phonetics and sight words will accelerate progression toward functional literacy.'}"
            </div>
          </div>

          {/* Key Metrics Snapshot Tiles */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-xl border border-slate-800 bg-slate-900/70">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase text-slate-400">Proficiency Tier</span>
                <Award size={16} className="text-teal-400" />
              </div>
              <p className="text-xl font-extrabold text-white capitalize">{profile.literacy_level || 'Foundational'}</p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-slate-800 bg-slate-900/70">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase text-slate-400">Daily Streak</span>
                <Flame size={16} className="text-amber-400" />
              </div>
              <p className="text-xl font-extrabold text-white">{streak} <span className="text-xs font-normal text-slate-400">Days</span></p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-slate-800 bg-slate-900/70">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase text-slate-400">Total Points</span>
                <Star size={16} className="text-emerald-400" />
              </div>
              <p className="text-xl font-extrabold text-white">{points} <span className="text-xs font-normal text-slate-400">XP</span></p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-slate-800 bg-slate-900/70">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase text-slate-400">Path Completion</span>
                <TrendingUp size={16} className="text-cyan-400" />
              </div>
              <p className="text-xl font-extrabold text-white">{Math.round(pathStats.completion_percentage || 0)}%</p>
            </div>
          </div>

          {/* 3 Skill Pillars */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
            <h4 className="font-bold text-sm text-white">Skill Benchmark Snapshot at Report Time</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-blue-300 flex items-center gap-1.5"><BookOpen size={14} /> Reading</span>
                  <span className="font-extrabold text-white">{profile.reading_pct || 0}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-500 h-full rounded-full" style={{ width: `${profile.reading_pct || 0}%` }} />
                </div>
              </div>

              <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-purple-300 flex items-center gap-1.5"><Brain size={14} /> Comprehension</span>
                  <span className="font-extrabold text-white">{profile.comprehension_pct || 0}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="bg-purple-500 h-full rounded-full" style={{ width: `${profile.comprehension_pct || 0}%` }} />
                </div>
              </div>

              <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-emerald-300 flex items-center gap-1.5"><Mic size={14} /> Voice & Speech</span>
                  <span className="font-extrabold text-white">{profile.voice_pct || 0}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${profile.voice_pct || 0}%` }} />
                </div>
              </div>
            </div>
          </div>

        </div>
      ) : (
        <div className="glass-panel p-10 rounded-2xl border border-slate-800 text-center space-y-3">
          <FileText size={36} className="mx-auto text-slate-600" />
          <h4 className="font-bold text-lg text-white">No Learning Reports Generated Yet</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click "Generate New Learning Report" above to trigger an AI pedagogical evaluation of your literacy scores and learning milestones.
          </p>
        </div>
      )}

      {/* 3. Report History Archive */}
      {reportHistory.length > 0 && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Clock size={18} className="text-teal-400" />
              <span>Past Learning Reports Archive</span>
            </h3>
            <span className="text-xs text-slate-400">{reportHistory.length} Reports</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {reportHistory.map((rep) => (
              <div
                key={rep.report_id}
                onClick={() => loadReportDetail(rep.report_id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between space-y-2 ${
                  activeReport?.report_id === rep.report_id
                    ? 'bg-emerald-950/40 border-emerald-500/60 shadow-md shadow-emerald-950/40'
                    : 'bg-slate-900/60 hover:bg-slate-900/90 border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Report #{rep.report_id}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">
                    {Math.round(rep.overall_progress || 0)}% Mastery
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>{new Date(rep.generated_at).toLocaleDateString()}</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-0.5">
                    View <ChevronRight size={12} />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. AI Next-Lesson Recommendations Section */}
      <RecommendationsPanel onActionClick={(rec) => {
        if (onSelectLesson) {
          onSelectLesson(rec);
        }
      }} />

    </div>
  );
}
