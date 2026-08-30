import React, { useState, useEffect, useCallback } from 'react';
import { 
  Sparkles, AlertCircle, RefreshCw, BookOpen, Mic, Brain, 
  ArrowRight, Compass, Flame, CheckCircle2, Award 
} from 'lucide-react';
import { apiRequest } from '../services/api';

export default function RecommendationsPanel({ onActionClick }) {
  const [recommendations, setRecommendations] = useState([]);
  const [provider, setProvider] = useState('');
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchRecommendations = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);
    setErrorMsg('');

    try {
      const data = await apiRequest('/recommendations');
      if (Array.isArray(data)) {
        setRecommendations(data);
      } else if (data && Array.isArray(data.recommendations)) {
        setRecommendations(data.recommendations);
        if (data.provider) setProvider(data.provider);
      } else {
        setRecommendations([]);
      }
    } catch (err) {
      console.error('Recommendations fetch error:', err);
      setErrorMsg(err.message || 'Unable to load personalized recommendations.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  const getPriorityBadge = (priority) => {
    const p = (priority || 'MEDIUM').toUpperCase();
    if (p === 'HIGH') {
      return (
        <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1">
          <Flame size={10} className="text-rose-400" /> High Priority
        </span>
      );
    }
    if (p === 'MEDIUM') {
      return (
        <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
          <Compass size={10} className="text-amber-400" /> Recommended
        </span>
      );
    }
    return (
      <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
        <CheckCircle2 size={10} className="text-emerald-400" /> Enrichment
      </span>
    );
  };

  const getSkillIcon = (skillFocus) => {
    const s = (skillFocus || 'READING').toUpperCase();
    if (s === 'VOICE' || s === 'SPOKEN') {
      return <Mic size={18} className="text-emerald-400" />;
    }
    if (s === 'COMPREHENSION') {
      return <Brain size={18} className="text-purple-400" />;
    }
    return <BookOpen size={18} className="text-blue-400" />;
  };

  if (loading) {
    return (
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-3">
        <div className="w-8 h-8 rounded-full border-2 border-emerald-500/20 border-t-emerald-500 animate-spin mx-auto" />
        <p className="text-xs text-slate-400">Analyzing literacy profile and querying AI recommendations engine...</p>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-rose-500/30 bg-rose-950/20 text-center space-y-3">
        <AlertCircle size={24} className="mx-auto text-rose-400" />
        <p className="text-xs text-rose-300">{errorMsg}</p>
        <button
          onClick={() => fetchRecommendations(true)}
          className="glass-button px-4 py-1.5 rounded-xl font-bold text-xs text-emerald-300 hover:text-white inline-flex items-center gap-1.5"
        >
          <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} />
          <span>Retry</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-500 to-teal-400 flex items-center justify-center text-slate-950 shadow-md">
            <Sparkles size={16} />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>AI Next-Lesson Recommendations</span>
              {provider && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {provider}
                </span>
              )}
            </h3>
            <p className="text-[11px] text-slate-400">
              Personalized interventions targeted to your lowest skill benchmark and completion pace.
            </p>
          </div>
        </div>

        <button
          onClick={() => fetchRecommendations(true)}
          disabled={refreshing}
          className="glass-button p-2 rounded-xl text-slate-400 hover:text-white transition-all"
          title="Refresh AI recommendations"
        >
          <RefreshCw size={14} className={refreshing ? 'animate-spin text-emerald-400' : ''} />
        </button>
      </div>

      {recommendations.length === 0 ? (
        <div className="glass-panel p-6 rounded-xl border border-slate-800 text-center text-xs text-slate-400 space-y-1">
          <p>No active recommendations right now.</p>
          <p className="text-slate-500">Complete an initial placement diagnostic or lesson to trigger personalized advice.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendations.map((rec, idx) => (
            <div 
              key={idx}
              className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/60 hover:bg-slate-900/90 transition-all flex flex-col justify-between space-y-4 relative overflow-hidden group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center border border-slate-700">
                      {getSkillIcon(rec.skill_focus)}
                    </div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      {rec.skill_focus || 'GENERAL'}
                    </span>
                  </div>
                  {getPriorityBadge(rec.priority)}
                </div>

                <div className="space-y-1.5">
                  <h4 className="font-bold text-sm text-white group-hover:text-emerald-300 transition-colors">
                    {rec.title}
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {rec.reason}
                  </p>
                </div>
              </div>

              {onActionClick && (
                <button
                  onClick={() => onActionClick(rec)}
                  className="w-full py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-emerald-600 text-slate-300 hover:text-white font-semibold text-xs transition-all flex items-center justify-center gap-1.5 border border-slate-700/60 hover:border-emerald-500"
                >
                  <span>Practice Target Skill</span>
                  <ArrowRight size={13} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
