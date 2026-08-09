import React, { useState, useEffect } from 'react';
import { Compass, Sparkles, Lock, Play, Check, CheckCircle, XCircle, ArrowRight, BookOpen, RefreshCw, Globe, HelpCircle } from 'lucide-react';
import { apiRequest } from '../services/api';

export default function LearningPath({ assessmentResult, onSelectLesson, onRetakeAssessment, selectedLang = 'en' }) {
  const [loading, setLoading] = useState(false);
  const [pathData, setPathData] = useState(assessmentResult?.learning_path || null);
  const [showProgress, setShowProgress] = useState(0);

  useEffect(() => {
    if (assessmentResult?.learning_path) {
      setPathData(assessmentResult.learning_path);
      setLoading(false);
      setTimeout(() => setShowProgress(assessmentResult.learning_path.completion_percentage || 15), 100);
      return;
    }

    const fetchPath = async () => {
      try {
        setLoading(true);
        const data = await apiRequest(`/learning-path/active?lang=${selectedLang}`);
        setPathData(data);
        setTimeout(() => setShowProgress(data.completion_percentage || 15), 100);
      } catch (err) {
        // Fallback default path data if backend dropped connection
        const fallbackData = {
          path_id: 1,
          path_title: "Adaptive Learning Roadmap — Track: FOUNDATIONAL",
          current_level: "FOUNDATIONAL",
          completion_percentage: 15,
          milestones: [
            {
              step: 1,
              title: "Milestone 1: Foundational Phonics & Letter Recognition",
              category: "Everyday Essentials",
              status: "UNLOCKED",
              completion: 30,
              lessons: [
                { lesson_id: 1, title: "Greetings & Everyday Phrases", content_type: "Voice Practice", target_text: "Hello, how are you today?", status: "ACTIVE" },
                { lesson_id: 2, title: "Numbers One to Ten", content_type: "Voice Practice", target_text: "One Two Three Four Five Six Seven Eight Nine Ten", status: "UNLOCKED" }
              ]
            },
            {
              step: 2,
              title: "Milestone 2: Functional Reading & Financial Literacy",
              category: "Digital & Healthcare Literacy",
              status: "LOCKED",
              completion: 0,
              lessons: [
                { lesson_id: 3, title: "ATM PIN Security Guidelines", content_type: "Functional Reading", target_text: "Never share your ATM PIN with anyone", status: "LOCKED" },
                { lesson_id: 4, title: "Reading Digital Payment Receipts", content_type: "Functional Reading", target_text: "Payment successful One Hundred Rupees", status: "LOCKED" }
              ]
            },
            {
              step: 3,
              title: "Milestone 3: Workplace Literacy & Voice Fluency",
              category: "Workplace Communication",
              status: "LOCKED",
              completion: 0,
              lessons: [
                { lesson_id: 5, title: "Workplace Safety & Polite Communication", content_type: "Voice Practice", target_text: "Thank you for your assistance today", status: "LOCKED" }
              ]
            }
          ]
        };
        setPathData(fallbackData);
        setTimeout(() => setShowProgress(15), 100);
      } finally {
        setLoading(false);
      }
    };

    fetchPath();
  }, [assessmentResult, selectedLang]);

  if (loading) {
    return (
      <div className="glass-panel p-8 rounded-2xl flex flex-col items-center justify-center space-y-4 min-h-[400px]">
        <RefreshCw className="animate-spin text-emerald-400" size={32} />
        <p className="text-slate-300 font-medium">Loading your personalized learning path...</p>
      </div>
    );
  }

  const activePath = pathData || {
    path_title: "Adaptive Learning Roadmap — Track: FOUNDATIONAL",
    current_level: "FOUNDATIONAL",
    completion_percentage: 15,
    milestones: [
      {
        step: 1,
        title: "Milestone 1: Foundational Phonics & Letter Recognition",
        category: "Everyday Essentials",
        status: "UNLOCKED",
        completion: 30,
        lessons: [
          { lesson_id: 1, title: "Greetings & Everyday Phrases", content_type: "Voice Practice", target_text: "Hello, how are you today?", status: "ACTIVE" },
          { lesson_id: 2, title: "Numbers One to Ten", content_type: "Voice Practice", target_text: "One Two Three Four Five Six Seven Eight Nine Ten", status: "UNLOCKED" }
        ]
      },
      {
        step: 2,
        title: "Milestone 2: Functional Reading & Financial Literacy",
        category: "Digital & Healthcare Literacy",
        status: "LOCKED",
        completion: 0,
        lessons: [
          { lesson_id: 3, title: "ATM PIN Security Guidelines", content_type: "Functional Reading", target_text: "Never share your ATM PIN with anyone", status: "LOCKED" },
          { lesson_id: 4, title: "Reading Digital Payment Receipts", content_type: "Functional Reading", target_text: "Payment successful One Hundred Rupees", status: "LOCKED" }
        ]
      },
      {
        step: 3,
        title: "Milestone 3: Workplace Literacy & Voice Fluency",
        category: "Workplace Communication",
        status: "LOCKED",
        completion: 0,
        lessons: [
          { lesson_id: 5, title: "Workplace Safety & Polite Communication", content_type: "Voice Practice", target_text: "Thank you for your assistance today", status: "LOCKED" }
        ]
      }
    ]
  };

  const score = typeof assessmentResult?.total_score === 'number' ? assessmentResult.total_score : (activePath.total_score ?? 0);
  const level = assessmentResult?.proficiency_level || activePath.current_level || 'FOUNDATIONAL';
  const breakdown = assessmentResult?.skill_breakdown || {
    reading_score: Math.min(33, Math.round(score * 0.33)),
    reading_max: 33,
    writing_score: Math.min(33, Math.round(score * 0.33)),
    writing_max: 33,
    voice_score: Math.max(0, score - Math.min(33, Math.round(score * 0.33)) * 2),
    voice_max: 34
  };
  
  const getLevelColor = (lvl) => {
    if (lvl === 'FOUNDATIONAL') return 'text-orange-400 bg-orange-400/20 border-orange-400/30';
    if (lvl === 'FUNCTIONAL') return 'text-blue-400 bg-blue-400/20 border-blue-400/30';
    return 'text-emerald-400 bg-emerald-400/20 border-emerald-400/30';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* 1. Score Summary Section */}
      <div className="glass-panel rounded-2xl p-6 md:p-8 space-y-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 border-b border-slate-700/60 pb-6">
          <div className="space-y-2 text-center md:text-left">
            <div className="flex items-center gap-2 justify-center md:justify-start">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Compass className="text-emerald-400" />
                Your Personalized Learning Path
              </h2>
              <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                <Globe size={12} /> {selectedLang.toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-slate-400">Adaptive curriculum tailored to your current literacy level</p>
          </div>
          
          <div className="flex items-center gap-4 bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <div className="relative w-16 h-16 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path className="text-slate-700" strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path className="text-emerald-500 transition-all duration-1000 ease-out" strokeDasharray={`${score}, 100`} strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-sm font-bold text-white">{score}</span>
                <span className="text-[8px] text-slate-400 -mt-1">/100</span>
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-xs text-slate-400 block uppercase font-semibold">Proficiency Level</span>
              <span className={`text-sm font-bold px-2.5 py-0.5 rounded-full border ${getLevelColor(level)}`}>
                {level}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Reading Literacy</span>
              <span className="text-amber-400 font-bold">{breakdown.reading_score}/{breakdown.reading_max || 33}</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-amber-400 rounded-full transition-all duration-1000" style={{width: `${Math.min(100, Math.round((breakdown.reading_score / (breakdown.reading_max || 33)) * 100))}%`}}></div>
            </div>
          </div>

          <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Writing & Spelling</span>
              <span className="text-blue-400 font-bold">{breakdown.writing_score}/{breakdown.writing_max || 33}</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-blue-400 rounded-full transition-all duration-1000" style={{width: `${Math.min(100, Math.round((breakdown.writing_score / (breakdown.writing_max || 33)) * 100))}%`}}></div>
            </div>
          </div>

          <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-300 font-medium">Voice Pronunciation</span>
              <span className="text-emerald-400 font-bold">{breakdown.voice_score}/{breakdown.voice_max || 34}</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full transition-all duration-1000" style={{width: `${Math.min(100, Math.round((breakdown.voice_score / (breakdown.voice_max || 34)) * 100))}%`}}></div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Personalization Insight */}
      {(activePath.personalization_reason || pathData?.personalization_reason) && (
        <div className="glass-panel rounded-2xl p-4 md:p-5 border border-violet-500/30 bg-gradient-to-r from-violet-950/30 via-slate-900/80 to-indigo-950/30">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-violet-500/20 flex items-center justify-center shrink-0 border border-violet-500/30">
              <Sparkles className="text-violet-400" size={18} />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-violet-300 flex items-center gap-1.5">
                <span>AI-Powered Personalization</span>
                <span className="text-[9px] font-bold px-1.5 py-0.5 bg-violet-500/20 text-violet-300 rounded border border-violet-500/30">Sarvam AI</span>
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                {activePath.personalization_reason || pathData?.personalization_reason}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 2. Detailed Diagnostic Question & Answer Review Section */}
      {assessmentResult?.validated_details && assessmentResult.validated_details.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 md:p-8 space-y-6 border border-slate-700/60 bg-slate-900/90 shadow-xl text-left">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-700/60 pb-4">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <CheckCircle className="text-emerald-400" size={22} />
                Diagnostic Question & Correct Answer Review
              </h3>
              <p className="text-xs text-slate-300">Complete performance breakdown showing questions, your submitted answers, and correct answers.</p>
            </div>
            <span className="text-xs font-bold px-3.5 py-1.5 bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30 self-start sm:self-auto">
              {assessmentResult.correct_answers || 0} / {assessmentResult.total_questions || 9} Correct
            </span>
          </div>

          <div className="space-y-4">
            {assessmentResult.validated_details.map((item, index) => {
              const isOk = item.is_correct;
              const skillBadgeColor = item.skill_type === 'READ' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : (item.skill_type === 'WRITE' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30');

              return (
                <div 
                  key={index} 
                  className={`p-4 md:p-5 rounded-xl border ${isOk ? 'border-emerald-500/40 bg-emerald-950/20' : 'border-rose-500/40 bg-rose-950/20'} space-y-3 transition-all shadow-md`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-700/40 pb-2.5">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-bold text-white bg-slate-800 px-2.5 py-0.5 rounded border border-slate-700">
                        Q{item.question_id || (index + 1)}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${skillBadgeColor}`}>
                        {item.skill_type}
                      </span>
                      <h4 className="text-sm font-bold text-slate-100">{item.question_title || `Question ${index + 1}`}</h4>
                    </div>

                    <span className={`text-xs font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 self-start sm:self-auto ${isOk ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' : 'bg-rose-500/20 text-rose-400 border-rose-500/40'}`}>
                      {isOk ? <CheckCircle size={14} /> : <XCircle size={14} />}
                      <span>{isOk ? '✓ Correct' : '✗ Incorrect'}</span>
                    </span>
                  </div>

                  {item.question_text && (
                    <p className="text-xs md:text-sm text-slate-200 font-semibold bg-slate-900/80 p-3 rounded-lg border border-slate-800 whitespace-pre-line leading-relaxed">
                      {item.question_text}
                    </p>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800 space-y-1">
                      <span className="text-slate-400 font-medium block">Your Submitted Answer:</span>
                      <span className={`font-bold text-sm block ${isOk ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {item.user_answer || "No Answer Submitted"}
                      </span>
                    </div>

                    <div className="bg-emerald-950/40 p-3 rounded-lg border border-emerald-500/30 space-y-1">
                      <span className="text-emerald-300 font-medium block">Correct Answer:</span>
                      <span className="font-bold text-sm text-emerald-200 block">
                        {item.correct_answer || "N/A"}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. Overall Progress Bar */}
      <div className="space-y-2 px-2">
        <div className="flex items-center justify-between text-sm font-medium">
          <span className="text-slate-300">Course Progress</span>
          <span className="text-emerald-400">{activePath.completion_percentage}%</span>
        </div>
        <div className="w-full bg-slate-900 rounded-full h-3 border border-slate-800 overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-1000 ease-out"
            style={{ width: `${showProgress}%` }}
          />
        </div>
      </div>

      {/* 3. Milestone Roadmap */}
      <div className="relative pl-4 md:pl-8 space-y-8 before:absolute before:inset-0 before:ml-[35px] md:before:ml-[51px] before:-translate-x-px md:before:-translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-emerald-500/50 before:via-slate-700 before:to-slate-800">
        {activePath.milestones?.map((milestone, idx) => {
          const isLocked = milestone.status === 'LOCKED';
          return (
            <div 
              key={milestone.step} 
              className="relative flex flex-col md:flex-row gap-6 animate-in slide-in-from-right-4 fade-in fill-mode-both"
              style={{ animationDelay: `${idx * 150}ms` }}
            >
              {/* Timeline Node */}
              <div className={`absolute -left-[35px] md:-left-[51px] z-10 w-10 h-10 rounded-full border-4 border-[#0b132b] flex items-center justify-center font-bold text-sm shadow-lg shadow-black/20 ${isLocked ? 'bg-slate-800 text-slate-500' : 'bg-gradient-to-br from-emerald-400 to-teal-500 text-white'}`}>
                {milestone.step}
              </div>

              {/* Milestone Card */}
              <div className={`flex-1 glass-card p-5 rounded-2xl border transition-all ${isLocked ? 'bg-slate-900/40 border-slate-800/80' : 'bg-slate-800/50 border-emerald-500/30'}`}>
                {isLocked && <div className="absolute inset-0 bg-slate-950/20 backdrop-blur-[1px] rounded-2xl z-20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity"><Lock className="text-slate-500" size={32} /></div>}
                
                <div className="flex flex-wrap gap-2 items-start justify-between mb-4">
                  <div>
                    <h3 className={`text-lg font-bold ${isLocked ? 'text-slate-400' : 'text-slate-100'}`}>{milestone.title}</h3>
                    <span className="text-xs text-slate-400">{milestone.category}</span>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${isLocked ? 'bg-slate-800 text-slate-500 border-slate-700' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'}`}>
                    {isLocked ? '🔒 LOCKED' : '▶ UNLOCKED / ACTIVE'}
                  </span>
                </div>

                <div className="w-full bg-slate-900/80 rounded-full h-1.5 mb-5 border border-slate-800">
                  <div className={`h-full rounded-full ${isLocked ? 'bg-slate-700' : 'bg-emerald-500'}`} style={{ width: `${milestone.completion}%` }}></div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 relative z-10">
                  {milestone.lessons?.map((lesson) => (
                    <div 
                      key={lesson.lesson_id}
                      onClick={() => !isLocked && lesson.status !== 'LOCKED' && onSelectLesson(lesson)}
                      className={`p-3.5 rounded-xl border flex items-center gap-3 transition-all ${
                        isLocked || lesson.status === 'LOCKED' 
                          ? 'bg-slate-900/50 border-slate-800 cursor-not-allowed' 
                          : 'bg-slate-800/80 border-slate-700 hover:border-emerald-500/50 cursor-pointer hover:bg-slate-800'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center ${
                        lesson.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400' :
                        isLocked || lesson.status === 'LOCKED' ? 'bg-slate-800 text-slate-600' :
                        'bg-teal-500/20 text-teal-400'
                      }`}>
                        {lesson.status === 'COMPLETED' ? <Check size={14} /> : 
                         isLocked || lesson.status === 'LOCKED' ? <Lock size={14} /> : 
                         <Play size={14} className="ml-0.5" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-[9px] uppercase font-bold text-slate-400 tracking-wider">
                            {lesson.content_type}
                          </span>
                        </div>
                        <h4 className={`text-xs font-semibold truncate ${isLocked || lesson.status === 'LOCKED' ? 'text-slate-500' : 'text-slate-200'}`}>
                          {lesson.title}
                        </h4>
                        <p className="text-[10px] text-slate-500 truncate mt-0.5 italic">
                          "{lesson.target_text}"
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 4. Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 pt-4">
        <button onClick={onRetakeAssessment} className="w-full py-3.5 rounded-xl glass-button text-emerald-300 hover:text-white font-semibold text-sm flex items-center justify-center gap-2 transition-all border border-emerald-500/40">
          <RefreshCw size={16} />
          Retake Diagnostic Assessment
        </button>
      </div>

    </div>
  );
}
