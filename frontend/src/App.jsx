import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DiagnosticTest from './components/DiagnosticTest';
import PronunciationCoach from './components/PronunciationCoach';
import LearningPath from './components/LearningPath';
import LearnerProfileView from './components/LearnerProfileView';
import ProficiencyBenchmarks from './components/ProficiencyBenchmarks';
import AuthModal from './components/AuthModal';
import { BookOpen, Type, Sparkles, Feather, Award, CheckCircle, ArrowRight, Play, User, LogIn, Globe } from 'lucide-react';
import { getAuthToken, removeAuthToken, apiRequest } from './services/api';

const LANG_MAP = {
  1: 'en',
  2: 'hi',
  3: 'ta',
  4: 'te',
  5: 'bn',
  6: 'mr',
  7: 'kn',
  8: 'es'
};

export default function App() {
  const [activeTab, setActiveTab] = useState('catalog');
  const [activeLesson, setActiveLesson] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [learner, setLearner] = useState({
    isLoggedIn: false,
    name: 'Guest Learner',
    email: '',
    native_lang_id: 1,
    literacy_level: 'FOUNDATIONAL',
    streak_count: 0,
    total_points: 0,
    preferred_lang: 'en'
  });

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      apiRequest('/auth/me')
        .then(data => {
          const userLang = LANG_MAP[data.native_lang_id] || data.current_lang_id || 'en';
          setLearner({
            isLoggedIn: true,
            name: data.first_name || data.username || data.email,
            email: data.email,
            native_lang_id: data.native_lang_id || 1,
            literacy_level: data.literacy_level || 'FOUNDATIONAL',
            streak_count: data.streak_count || 1,
            total_points: data.total_points || 50,
            preferred_lang: userLang
          });
          setIsAuthOpen(false);
        })
        .catch(() => {
          removeAuthToken();
          setIsAuthOpen(false);
        });
    }
  }, []);

  const handleAuthSuccess = (userData) => {
    const userLang = LANG_MAP[userData.native_lang_id] || userData.preferred_lang || 'en';
    setLearner({
      isLoggedIn: true,
      name: userData.username,
      email: userData.email || '',
      native_lang_id: userData.native_lang_id || 1,
      literacy_level: userData.literacy_level || 'FOUNDATIONAL',
      streak_count: 1,
      total_points: 50,
      preferred_lang: userLang
    });
    setIsAuthOpen(false);
  };

  const handleLogout = () => {
    removeAuthToken();
    setLearner({
      isLoggedIn: false,
      name: 'Guest Learner',
      email: '',
      native_lang_id: 1,
      literacy_level: 'FOUNDATIONAL',
      streak_count: 0,
      total_points: 0,
      preferred_lang: 'en'
    });
    setIsAuthOpen(false);
    setActiveTab('catalog');
  };

  const handleProfileUpdate = (updatedProfile) => {
    const userLang = LANG_MAP[updatedProfile.native_lang_id] || 'en';
    setLearner(prev => ({
      ...prev,
      name: updatedProfile.first_name || prev.name,
      native_lang_id: updatedProfile.native_lang_id || prev.native_lang_id,
      literacy_level: updatedProfile.literacy_level || prev.literacy_level,
      preferred_lang: userLang
    }));
  };

  const categories = [
    {
      id: 1,
      title: 'Phonemes & Alphabet Fundamentals',
      icon: BookOpen,
      color: 'from-emerald-500 to-teal-600',
      description: 'Alphabet sound associations, long/short vowels, and syllable stress',
      lessonsCount: 4
    },
    {
      id: 2,
      title: 'Vocabulary & Word Formation',
      icon: Type,
      color: 'from-blue-500 to-indigo-600',
      description: 'Prefixes, suffixes, root words, synonyms, and antonym mastery',
      lessonsCount: 4
    },
    {
      id: 3,
      title: 'Sentence Grammar & Syntax',
      icon: Sparkles,
      color: 'from-rose-500 to-pink-600',
      description: 'Noun-verb agreement, tenses, conjunctions, and complex sentence structure',
      lessonsCount: 3
    },
    {
      id: 4,
      title: 'Advanced Literary Fluency & Expression',
      icon: Feather,
      color: 'from-amber-500 to-orange-600',
      description: 'Prose & passage reading comprehension, articulate speech, and literary expression',
      lessonsCount: 3
    }
  ];

  const sampleLessons = [
    {
      lesson_id: 1,
      category_id: 1,
      title: 'Vowel Sounds & Phoneme Synthesis',
      content_type: 'Voice Practice',
      target_text: 'Language unlocks knowledge, wisdom, and human expression',
      difficulty_level: 'FOUNDATIONAL'
    },
    {
      lesson_id: 2,
      category_id: 2,
      title: 'Prefixes, Suffixes & Root Words',
      content_type: 'Language Practice',
      target_text: 'Understanding root words enhances vocabulary comprehension',
      difficulty_level: 'FUNCTIONAL'
    },
    {
      lesson_id: 3,
      category_id: 3,
      title: 'Noun-Verb Agreement & Tenses',
      content_type: 'Grammar Practice',
      target_text: 'She had written an eloquent essay before sunrise',
      difficulty_level: 'FUNCTIONAL'
    },
    {
      lesson_id: 4,
      category_id: 4,
      title: 'Literary Prose & Passage Reading',
      content_type: 'Literature Practice',
      target_text: 'Mastery over language transforms thought into eloquent communication',
      difficulty_level: 'PROFICIENT'
    }
  ];

  const handleDiagnosticComplete = (result) => {
    setAssessmentResult(result);
    setLearner(prev => ({
      ...prev,
      total_points: prev.total_points + 50,
      literacy_level: result.proficiency_level || result.level || prev.literacy_level
    }));
    setActiveTab('learning-path');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0b132b] text-slate-100">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        learner={learner} 
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />

      <AuthModal 
        isOpen={isAuthOpen} 
        onClose={() => setIsAuthOpen(false)} 
        onAuthSuccess={handleAuthSuccess}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 space-y-8">
        
        {/* Learner Welcome Banner */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-700/60 bg-gradient-to-r from-slate-900/90 via-emerald-950/30 to-slate-900/90 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2 flex-wrap">
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Level: {learner.literacy_level}
              </span>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1">
                <Globe size={12} /> Language: {learner.preferred_lang.toUpperCase()}
              </span>
              {learner.isLoggedIn && (
                <span className="text-xs font-semibold text-emerald-300 flex items-center gap-1">
                  <CheckCircle size={14} /> JWT Authenticated
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold text-white">{learner.name}</h2>
            <p className="text-xs md:text-sm text-slate-300">
              Master language phonetics, vocabulary, grammar, and literary expression with AI-driven voice guidance.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Quick Language Selector */}
            <div className="flex items-center gap-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-700 text-xs">
              <Globe size={14} className="text-emerald-400" />
              <select
                value={learner.preferred_lang}
                onChange={(e) => setLearner(prev => ({ ...prev, preferred_lang: e.target.value }))}
                className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer"
              >
                <option value="en" className="bg-slate-900 text-white">English</option>
                <option value="te" className="bg-slate-900 text-white">Telugu (తెలుగు)</option>
                <option value="hi" className="bg-slate-900 text-white">Hindi (हिन्दी)</option>
                <option value="ta" className="bg-slate-900 text-white">Tamil (தமிழ்)</option>
                <option value="bn" className="bg-slate-900 text-white">Bengali (বাংলা)</option>
                <option value="mr" className="bg-slate-900 text-white">Marathi (मराठी)</option>
                <option value="kn" className="bg-slate-900 text-white">Kannada (ಕನ್ನಡ)</option>
                <option value="es" className="bg-slate-900 text-white">Spanish (Español)</option>
              </select>
            </div>

            {!learner.isLoggedIn ? (
              <button
                onClick={() => setIsAuthOpen(true)}
                className="glass-button px-5 py-3 rounded-xl font-bold text-sm flex items-center gap-2 text-emerald-300"
              >
                <LogIn size={18} />
                <span>Login / Create Account</span>
              </button>
            ) : (
              <button
                onClick={() => setActiveTab('dashboard')}
                className="glass-button px-5 py-3 rounded-xl font-semibold text-sm flex items-center gap-2 text-emerald-300"
              >
                <User size={18} />
                <span>Learner Profile</span>
              </button>
            )}
          </div>
        </div>

        {/* Learner Profile Dashboard View */}
        {activeTab === 'dashboard' && (
          <LearnerProfileView learner={learner} onProfileUpdate={handleProfileUpdate} />
        )}

        {/* Learner Proficiency Benchmarks View */}
        {activeTab === 'benchmarks' && (
          <ProficiencyBenchmarks selectedLang={learner.preferred_lang} />
        )}

        {/* Tab 1: Diagnostic Test View */}
        {activeTab === 'diagnostic' && (
          <DiagnosticTest
            selectedLang={learner.preferred_lang}
            onComplete={handleDiagnosticComplete}
            onSelectLesson={(les) => { setActiveLesson(les); setActiveTab('catalog'); }}
          />
        )}

        {/* Learning Path View */}
        {activeTab === 'learning-path' && (
          <LearningPath
            assessmentResult={assessmentResult}
            selectedLang={learner.preferred_lang}
            onSelectLesson={(les) => { setActiveLesson(les); setActiveTab('catalog'); }}
            onRetakeAssessment={() => { setAssessmentResult(null); setActiveTab('diagnostic'); }}
          />
        )}

        {/* Tab 2: Pronunciation Practice Mode */}
        {activeLesson ? (
          <div className="space-y-4">
            <button
              onClick={() => { setActiveLesson(null); if (assessmentResult) setActiveTab('learning-path'); }}
              className="text-xs text-emerald-400 hover:underline font-semibold flex items-center gap-1"
            >
              ← Return to Learning Path
            </button>
            <PronunciationCoach
              lesson={activeLesson}
              onScoreUpdate={(score) => {
                setLearner(prev => ({
                  ...prev,
                  total_points: prev.total_points + Math.round(score / 10)
                }));
              }}
            />
          </div>
        ) : activeTab === 'catalog' ? (
          /* Catalog View */
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <BookOpen size={20} className="text-emerald-400" />
              Language Literacy Curriculum Modules
            </h3>

            {/* Category Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {categories.map(cat => {
                const IconComp = cat.icon;
                return (
                  <div key={cat.id} className="glass-panel p-5 rounded-2xl border border-slate-700/60 hover:border-emerald-500/40 transition-all group">
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cat.color} flex items-center justify-center text-white shadow-md`}>
                        <IconComp size={24} />
                      </div>
                      <div className="flex-1 space-y-1">
                        <h4 className="font-bold text-base text-slate-100 group-hover:text-emerald-400 transition-colors">
                          {cat.title}
                        </h4>
                        <p className="text-xs text-slate-400">{cat.description}</p>
                        <span className="text-[11px] text-emerald-400 font-semibold inline-block pt-1">
                          {cat.lessonsCount} Practice Lessons Available
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Sample Lessons List */}
            <div className="space-y-3 pt-4">
              <h4 className="text-md font-bold text-slate-300">Recommended Language Literacy Practice Lessons</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {sampleLessons.map(les => (
                  <div 
                    key={les.lesson_id}
                    onClick={() => setActiveLesson(les)}
                    className="glass-card p-4 rounded-xl border border-slate-700/80 hover:border-emerald-500/50 cursor-pointer transition-all flex items-center justify-between group"
                  >
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold uppercase text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                        {les.content_type}
                      </span>
                      <h5 className="font-bold text-sm text-slate-100 group-hover:text-emerald-300 transition-colors">
                        {les.title}
                      </h5>
                      <p className="text-xs text-slate-400 italic">"{les.target_text}"</p>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center group-hover:bg-emerald-500 group-hover:text-white transition-all shadow-md">
                      <Play size={16} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}

      </main>
    </div>
  );
}
