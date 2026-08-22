import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DiagnosticTest from './components/DiagnosticTest';
import PronunciationCoach from './components/PronunciationCoach';
import InteractiveWritingCanvas from './components/InteractiveWritingCanvas';
import ReadingStudioCard from './components/ReadingStudioCard';
import LearningPath from './components/LearningPath';
import LearnerProfileView from './components/LearnerProfileView';
import ProficiencyBenchmarks from './components/ProficiencyBenchmarks';
import AuthModal from './components/AuthModal';
import AdminPanel from './components/AdminPanel';
import { BookOpen, Type, Sparkles, Feather, Award, CheckCircle, ArrowRight, Play, User, LogIn, Globe, Mic } from 'lucide-react';
import { getAuthToken, removeAuthToken, apiRequest } from './services/api';

const LANG_MAP = {
  1: 'hi',
  2: 'en',
  3: 'ta',
  4: 'te',
  5: 'mr',
  6: 'bn',
  7: 'kn',
  8: 'es'
};

const resolveLangCode = (input) => {
  if (!input) return 'en';
  if (typeof input === 'string') {
    const cleanStr = input.trim().toLowerCase();
    if (cleanStr.length === 2) return cleanStr;
    const parsed = parseInt(cleanStr, 10);
    if (!isNaN(parsed) && LANG_MAP[parsed]) return LANG_MAP[parsed];
  }
  if (typeof input === 'number' && LANG_MAP[input]) return LANG_MAP[input];
  return 'en';
};

const getCurriculumPillarType = (les) => {
  if (!les) return 'SPOKEN';
  
  const catId = Number(les.category_id);
  const skill = (les.skill_type || les.skill || les.category || '').toUpperCase();
  const cType = (les.content_type || '').toLowerCase();
  const title = (les.title || les.module_name || '').toLowerCase();

  // 1. Written Curriculum Check
  if (catId === 2 || skill === 'WRITTEN' || cType.includes('written') || title.includes('written') || title.includes('లేఖన') || title.includes('लेखन') || title.includes('எழுத்து') || title.includes('লিখন') || title.includes('ಬರಹ')) {
    return 'WRITTEN';
  }

  // 2. Reading Curriculum Check
  if (catId === 3 || skill === 'READING' || cType.includes('reading') || cType.includes('functional') || title.includes('reading') || title.includes('పఠన') || title.includes('पठन') || title.includes('வாசிப்பு') || title.includes('वाचन') || title.includes('ಓದುವ')) {
    return 'READING';
  }

  // 3. Default: Spoken Curriculum
  return 'SPOKEN';
};

export default function App() {
  const [activeTab, setActiveTab] = useState('catalog');
  const [activeLesson, setActiveLesson] = useState(null);
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(true);
  const [isNewRegistration, setIsNewRegistration] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [dbLessons, setDbLessons] = useState(null);
  const [learner, setLearner] = useState({
    isLoggedIn: false,
    name: 'Guest Learner',
    email: '',
    native_lang_id: 2,
    literacy_level: 'FOUNDATIONAL',
    streak_count: 0,
    total_points: 0,
    preferred_lang: 'en'
  });

  // Sync activeTab with URL Hash & enable browser Back/Forward navigation history arrows
  useEffect(() => {
    const getTabFromHash = () => {
      const hash = window.location.hash.replace('#', '').trim();
      const validTabs = ['catalog', 'diagnostic', 'benchmarks', 'learning-path', 'dashboard'];
      return validTabs.includes(hash) ? hash : 'catalog';
    };

    const initialTab = getTabFromHash();
    setActiveTab(initialTab);

    const handleHashOrPopState = () => {
      const currentTab = getTabFromHash();
      setActiveTab(currentTab);
    };

    window.addEventListener('popstate', handleHashOrPopState);
    window.addEventListener('hashchange', handleHashOrPopState);

    return () => {
      window.removeEventListener('popstate', handleHashOrPopState);
      window.removeEventListener('hashchange', handleHashOrPopState);
    };
  }, []);

  const changeTab = (tabKey) => {
    setActiveTab(tabKey);
    const targetHash = `#${tabKey}`;
    if (window.location.hash !== targetHash) {
      window.history.pushState({ tab: tabKey }, '', `${window.location.pathname}${targetHash}`);
    }
  };

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      apiRequest('/auth/me')
        .then(data => {
          const userLang = resolveLangCode(data.native_lang_id || data.current_lang_id || data.preferred_lang);
          setLearner({
            isLoggedIn: true,
            name: data.first_name || data.username || data.email || 'Learner',
            email: data.email || '',
            native_lang_id: data.native_lang_id || 2,
            literacy_level: data.literacy_level || 'FOUNDATIONAL',
            streak_count: data.streak_count || 1,
            total_points: data.total_points || 50,
            preferred_lang: userLang
          });
          setIsAuthOpen(false);
        })
        .catch(() => {
          removeAuthToken();
          setIsAuthOpen(true);
        });
    } else {
      setIsAuthOpen(true);
    }
  }, []);

  const handleAuthSuccess = (userData, authType = 'login') => {
    const userLang = resolveLangCode(userData.native_lang_id || userData.current_lang_id || userData.preferred_lang);
    setLearner({
      isLoggedIn: true,
      name: userData.username || userData.first_name || 'Learner',
      email: userData.email || '',
      native_lang_id: userData.native_lang_id || 2,
      literacy_level: userData.literacy_level || 'FOUNDATIONAL',
      streak_count: 1,
      total_points: 50,
      preferred_lang: userLang
    });
    setIsAuthOpen(false);

    if (authType === 'register') {
      setIsNewRegistration(true);
      changeTab('diagnostic');
    }
  };

  const handleLogout = () => {
    removeAuthToken();
    setLearner({
      isLoggedIn: false,
      name: 'Guest Learner',
      email: '',
      native_lang_id: 2,
      literacy_level: 'FOUNDATIONAL',
      streak_count: 0,
      total_points: 0,
      preferred_lang: 'en'
    });
    setIsAuthOpen(true);
    setActiveTab('catalog');
  };

  const handleProfileUpdate = (updatedProfile) => {
    const userLang = resolveLangCode(updatedProfile.native_lang_id || updatedProfile.preferred_lang);
    setLearner(prev => ({
      ...prev,
      name: updatedProfile.first_name || prev.name,
      native_lang_id: updatedProfile.native_lang_id || prev.native_lang_id,
      literacy_level: updatedProfile.literacy_level || prev.literacy_level,
      preferred_lang: userLang
    }));
  };

  useEffect(() => {
    const fetchLanguagePillars = async () => {
      try {
        setDbLessons(null); // Instantly reset lessons when changing language to avoid cross-language bleed
        const langToFetch = learner.preferred_lang || 'en';
        const data = await apiRequest(`/curriculum/pillars/${langToFetch}`);
        if (data && data.pillars && data.pillars.length > 0) {
          const parsedLessons = [];
          data.pillars.forEach(pillar => {
            const catId = pillar.skill_type === 'SPOKEN' ? 1 : (pillar.skill_type === 'WRITTEN' ? 2 : 3);
            (pillar.sub_modules || []).forEach(sub => {
              (sub.lessons || []).forEach(les => {
                parsedLessons.push({
                  lesson_id: les.lesson_id,
                  category_id: catId,
                  title: sub.module_name || les.title,
                  content_type: les.content_type,
                  target_text: les.target_text,
                  difficulty_level: les.difficulty_level || 'Zero',
                  lang: data.lang_code || langToFetch
                });
              });
            });
          });
          if (parsedLessons.length > 0) {
            setDbLessons(parsedLessons);
          }
        }
      } catch (err) {
        console.log('Error fetching language pillars:', err.message);
      }
    };
    fetchLanguagePillars();
  }, [learner.preferred_lang]);

  const categories = [
    {
      id: 1,
      title: 'Spoken Curriculum',
      icon: Mic,
      color: 'from-amber-500 to-orange-600',
      description: 'Zero Level foundational oral communication: Sound Inventory → Passive Listening → Survival Phrases → Numbers 0-10 → Self-Intro → Audio Shadowing.',
      lessonsCount: 6
    },
    {
      id: 2,
      title: 'Written Curriculum',
      icon: Type,
      color: 'from-blue-500 to-indigo-600',
      description: 'Zero Level foundational script writing: Letter Strokes → Vowel Marks → 2-Letter Combinations → Numbers 0-10 → Survival Words → Self-Intro Sentence.',
      lessonsCount: 6
    },
    {
      id: 3,
      title: 'Reading Curriculum',
      icon: BookOpen,
      color: 'from-emerald-500 to-teal-600',
      description: 'Zero Level foundational functional reading: Alphabet Recognition → Vowel Sight Reading → 2-Letter Sight Words → Numbers 0-10 → Survival Signs → Greetings.',
      lessonsCount: 6
    }
  ];

  const sampleLessons = [
    // 🗣️ SPOKEN CURRICULUM (Category 1: Zero Level Foundational Modules)
    {
      lesson_id: 101,
      category_id: 1,
      title: 'Module 1: Sound Inventory (Vowels & Unique Consonants)',
      content_type: 'Voice Practice',
      target_text: 'A-ah, B-buh, C-kuh, D-duh, E-eh, Th-sound, Ph-sound',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 102,
      category_id: 1,
      title: 'Module 2: Passive Listening Exposure (Rhythm & Intonation)',
      content_type: 'Voice Practice',
      target_text: 'Hello friend, how are you today? Welcome to our practice lesson.',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 103,
      category_id: 1,
      title: 'Module 3: Core Survival Phrases (Hello, Goodbye, Please, Thank You, Yes, No, Excuse Me, Sorry)',
      content_type: 'Voice Practice',
      target_text: 'Hello, Goodbye, Please, Thank You, Yes, No, Excuse Me, Sorry',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 104,
      category_id: 1,
      title: 'Module 4: Numbers 0 to 10 (Counting Sound Phonemes)',
      content_type: 'Voice Practice',
      target_text: 'Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 105,
      category_id: 1,
      title: 'Module 5: Fixed Self-Intro Chunks ("My name is...", "I am from...")',
      content_type: 'Voice Practice',
      target_text: 'Hello, my name is Alex. I am from New York.',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 106,
      category_id: 1,
      title: 'Module 6: Audio Shadowing Practice (Repeating Audio Clips)',
      content_type: 'Voice Practice',
      target_text: 'Repeat after me: I learn language with confidence and clarity.',
      difficulty_level: 'Zero'
    },

    // ✍️ WRITTEN CURRICULUM (Category 2: Zero Level Foundational Modules)
    {
      lesson_id: 201,
      category_id: 2,
      title: 'Module 1: Script Strokes & Letter Shapes',
      content_type: 'Written Practice',
      target_text: 'A, B, C, D, E — Basic Letter Strokes',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 202,
      category_id: 2,
      title: 'Module 2: Vowel Marks & Accent Symbols',
      content_type: 'Written Practice',
      target_text: 'Am, An, As, At — Vowel Mark Spelling',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 203,
      category_id: 2,
      title: 'Module 3: 2-Letter Syllable Combinations',
      content_type: 'Written Practice',
      target_text: 'In, On, It, To, Up, Go — Syllable Combinations',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 204,
      category_id: 2,
      title: 'Module 4: Writing Numbers 0 to 10',
      content_type: 'Written Practice',
      target_text: '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — Digits',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 205,
      category_id: 2,
      title: 'Module 5: Writing Survival Courtesy Words',
      content_type: 'Written Practice',
      target_text: 'Hello, Thank You, Yes, No — Survival Spelling',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 206,
      category_id: 2,
      title: 'Module 6: Writing Fixed Self-Intro Sentence',
      content_type: 'Written Practice',
      target_text: 'My name is Alex. I am from New York.',
      difficulty_level: 'Zero'
    },

    // 📖 READING CURRICULUM (Category 3: Zero Level Foundational Modules)
    {
      lesson_id: 301,
      category_id: 3,
      title: 'Module 1: Visual Alphabet & Symbol Recognition',
      content_type: 'Functional Reading',
      target_text: 'A, B, C, D, E, F — Visual Letter Recognition',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 302,
      category_id: 3,
      title: 'Module 2: Vowel Sound Sight Reading',
      content_type: 'Functional Reading',
      target_text: 'Ba, Ca, Da, Fa, Ga — Sight Reading',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 303,
      category_id: 3,
      title: 'Module 3: 2-Letter Sight Word Reading',
      content_type: 'Functional Reading',
      target_text: 'In, On, At, Is, It, Up — Short Word Reading',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 304,
      category_id: 3,
      title: 'Module 4: Reading Numbers 0 to 10',
      content_type: 'Functional Reading',
      target_text: '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — Digits',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 305,
      category_id: 3,
      title: 'Module 5: Reading Survival Signs & Labels',
      content_type: 'Functional Reading',
      target_text: 'Open, Closed, Exit, Stop, Push — Label Reading',
      difficulty_level: 'Zero'
    },
    {
      lesson_id: 306,
      category_id: 3,
      title: 'Module 6: Reading Fixed Greetings & Intro Chunks',
      content_type: 'Functional Reading',
      target_text: 'Hello, Welcome, Good Morning — Sight Reading',
      difficulty_level: 'Zero'
    }
  ];

  const handleDiagnosticComplete = (result) => {
    setAssessmentResult(result);
    setLearner(prev => ({
      ...prev,
      total_points: prev.total_points + 50,
      literacy_level: result.proficiency_level || result.level || prev.literacy_level
    }));
    changeTab('learning-path');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0b132b] text-slate-100">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={changeTab} 
        learner={learner} 
        isNewRegistration={isNewRegistration}
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
                <Globe size={12} /> Language: {(learner.preferred_lang || 'en').toString().toUpperCase()}
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
                onClick={() => changeTab('dashboard')}
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
          !learner.isLoggedIn ? (
            <div className="glass-panel max-w-xl mx-auto rounded-2xl p-8 text-center my-8 space-y-6 border border-slate-700 bg-slate-900/90 shadow-2xl animate-fade-in">
              <div className="w-16 h-16 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center mx-auto shadow-lg shadow-amber-500/20">
                <Lock size={32} />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white">Authentication Required</h3>
                <p className="text-sm text-slate-300">
                  You must log in or register an account before accessing the 9-level bilingual placement test.
                </p>
              </div>
              <div className="pt-2">
                <button
                  onClick={() => setIsAuthOpen(true)}
                  className="w-full py-4 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2"
                >
                  <LogIn size={18} />
                  <span>Login / Register Account to Access Diagnostic Test</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {isNewRegistration && (
                <div className="glass-panel p-6 rounded-2xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-slate-900/90 to-teal-950/40 space-y-4 text-left shadow-xl animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-emerald-400 font-bold text-lg">
                      <CheckCircle size={22} className="text-emerald-400" />
                      <span>Account Registered Successfully!</span>
                    </div>
                    <span className="text-xs px-3 py-1 bg-amber-500/20 text-amber-300 font-semibold rounded-full border border-amber-500/30">
                      Step 1 of 2: Placement Diagnostic
                    </span>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-white">Welcome, {learner.name}! Take Your Initial Placement Test</h3>
                    <p className="text-xs md:text-sm text-slate-300 mt-1">
                      An intimation email has been sent to <strong className="text-emerald-300">{learner.email}</strong>. 
                      Please complete this 9-question bilingual assessment to evaluate your proficiency tier and unlock your personalized learning path.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                    <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-700/60 text-xs space-y-1">
                      <span className="font-bold text-emerald-400 block">🎯 3-Tier Skill Benchmark</span>
                      <p className="text-slate-300">Determines your placement: Foundational, Functional, or Proficient tier.</p>
                    </div>
                    <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-700/60 text-xs space-y-1">
                      <span className="font-bold text-teal-400 block">🗣️ Multi-Skill Evaluation</span>
                      <p className="text-slate-300">Evaluates Reading (READ), Spelling (WRITE), and Pronunciation (SPEAK).</p>
                    </div>
                    <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-700/60 text-xs space-y-1">
                      <span className="font-bold text-amber-400 block">⏱️ 3-Minute Assessment</span>
                      <p className="text-slate-300">9 short questions across progressive difficulty levels (Level 1 to 9).</p>
                    </div>
                  </div>
                </div>
              )}

              <DiagnosticTest
                selectedLang={learner.preferred_lang}
                onComplete={(res) => {
                  setIsNewRegistration(false);
                  handleDiagnosticComplete(res);
                }}
                onSelectLesson={(les) => { setActiveLesson(les); changeTab('catalog'); }}
              />
            </div>
          )
        )}

        {/* Learning Path View */}
        {activeTab === 'learning-path' && (
          !learner.isLoggedIn ? (
            <div className="glass-panel max-w-xl mx-auto rounded-2xl p-8 text-center my-8 space-y-6 border border-slate-700 bg-slate-900/90 shadow-2xl animate-fade-in">
              <div className="w-16 h-16 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center mx-auto shadow-lg shadow-amber-500/20">
                <Lock size={32} />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white">Authentication Required</h3>
                <p className="text-sm text-slate-300">
                  Please log in or register an account to view your personalized learning path and progress.
                </p>
              </div>
              <div className="pt-2">
                <button
                  onClick={() => setIsAuthOpen(true)}
                  className="w-full py-4 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2"
                >
                  <LogIn size={18} />
                  <span>Login / Register to Access Learning Path</span>
                </button>
              </div>
            </div>
          ) : (
            <LearningPath
              assessmentResult={assessmentResult}
              selectedLang={learner.preferred_lang}
              onSelectLesson={(les) => { setActiveLesson(les); changeTab('catalog'); }}
              onRetakeAssessment={() => changeTab('diagnostic')}
            />
          )
        )}

        {/* Practice Mode based on Curriculum Category */}
        {activeLesson ? (
          <div className="space-y-4">
            <button
              onClick={() => { setActiveLesson(null); if (assessmentResult) setActiveTab('learning-path'); }}
              className="text-xs text-emerald-400 hover:underline font-semibold flex items-center gap-1"
            >
              ← Return to Curriculum Catalog
            </button>

            {getCurriculumPillarType(activeLesson) === 'WRITTEN' ? (
              <InteractiveWritingCanvas
                lesson={activeLesson}
                onClose={() => setActiveLesson(null)}
              />
            ) : getCurriculumPillarType(activeLesson) === 'READING' ? (
              <ReadingStudioCard
                lesson={activeLesson}
                onClose={() => setActiveLesson(null)}
              />
            ) : (
              <PronunciationCoach
                lesson={activeLesson}
                onScoreUpdate={async (score) => {
                  setLearner(prev => ({
                    ...prev,
                    total_points: prev.total_points + Math.round(score / 10)
                  }));

                  try {
                    const completionPayload = {
                      lesson_id: activeLesson.lesson_id || activeLesson.id,
                      score: score,
                      path_lesson_id: activeLesson.path_lesson_id || null
                    };

                    const result = await apiRequest('/progress/complete-lesson', {
                      method: 'POST',
                      body: JSON.stringify(completionPayload)
                    });

                    if (activeLesson.path_lesson_id) {
                      await apiRequest(`/learning-path/lesson/${activeLesson.path_lesson_id}/status`, {
                        method: 'PATCH',
                        body: JSON.stringify({ status: 'COMPLETED' })
                      });
                    }

                    setTimeout(() => {
                      setActiveLesson(null);
                      setActiveTab('learning-path');
                      setAssessmentResult(prev => prev ? { ...prev, learning_path: null } : null);
                    }, 2000);

                  } catch (err) {
                    console.log('Lesson completion API call skipped:', err.message);
                  }
                }}
              />
            )}
          </div>
        ) : activeTab === 'admin' ? (
          /* Admin Content Studio Panel */
          <AdminPanel />
        ) : activeTab === 'catalog' ? (
          /* Catalog View */
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                  <BookOpen size={20} className="text-emerald-400" />
                  Language Literacy Curriculum Core Pillars
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Click any curriculum pillar below to explore its 8 progressive difficulty sub-modules (Zero → Mastery).
                </p>
              </div>

              {/* Filter Tabs */}
              <div className="flex items-center gap-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-700 text-xs">
                <button
                  onClick={() => setSelectedCategoryFilter(null)}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                    selectedCategoryFilter === null ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  All (24 Sub-Modules)
                </button>
                <button
                  onClick={() => setSelectedCategoryFilter(1)}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                    selectedCategoryFilter === 1 ? 'bg-amber-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Spoken (8 Stages)
                </button>
                <button
                  onClick={() => setSelectedCategoryFilter(2)}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                    selectedCategoryFilter === 2 ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Written (8 Stages)
                </button>
                <button
                  onClick={() => setSelectedCategoryFilter(3)}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                    selectedCategoryFilter === 3 ? 'bg-teal-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Reading (8 Stages)
                </button>
              </div>
            </div>

            {/* Category Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {categories.map(cat => {
                const IconComp = cat.icon;
                const isSelected = selectedCategoryFilter === cat.id;
                const activeLessonsList = dbLessons || [];
                const catSubModules = activeLessonsList.filter(les => les.category_id === cat.id);

                return (
                  <div 
                    key={cat.id} 
                    onClick={() => setSelectedCategoryFilter(isSelected ? null : cat.id)}
                    className={`glass-panel p-5 rounded-2xl border transition-all cursor-pointer group ${
                      isSelected 
                        ? 'border-emerald-500 bg-slate-900/95 ring-2 ring-emerald-500/30 shadow-xl col-span-1 md:col-span-3' 
                        : 'border-slate-700/60 hover:border-emerald-500/50 hover:bg-slate-900/80 shadow-md'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${cat.color} flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform flex-shrink-0`}>
                        <IconComp size={24} />
                      </div>
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-bold text-base text-slate-100 group-hover:text-emerald-400 transition-colors">
                            {cat.title}
                          </h4>
                          <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border transition-all ${
                            isSelected 
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' 
                              : 'bg-slate-800 text-slate-400 border-slate-700 group-hover:border-emerald-500/30'
                          }`}>
                            {isSelected ? "▲ Hide 6 Zero Modules" : "▼ Click to Expand 6 Zero Modules"}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{cat.description}</p>
                        <span className="text-[11px] text-emerald-400 font-semibold inline-block pt-1">
                          {catSubModules.length} Zero Level Foundational Modules Available
                        </span>
                      </div>
                    </div>

                    {/* Expandable Sub-Modules Drawer when card is clicked */}
                    {isSelected && (
                      <div className="mt-5 pt-5 border-t border-slate-700/80 space-y-4 animate-fade-in" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                            <Sparkles size={14} className="text-amber-400" />
                            {cat.title} — 6 Zero Level Foundational Modules ({learner.preferred_lang.toUpperCase()}):
                          </span>
                          <span className="text-xs text-slate-400 font-medium">Click any sub-module below to start practicing</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[500px] overflow-y-auto pr-1">
                          {catSubModules.map((les, idx) => (
                            <div
                              key={les.lesson_id}
                              onClick={() => setActiveLesson(les)}
                              className="p-3.5 rounded-xl bg-slate-950/90 hover:bg-emerald-950/40 border border-slate-800 hover:border-emerald-500/60 transition-all flex items-center justify-between group/sub cursor-pointer shadow-sm hover:shadow-emerald-500/10"
                            >
                              <div className="space-y-1 pr-3">
                                <div className="flex items-center gap-2">
                                  <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">
                                    Module {idx + 1}: {les.difficulty_level}
                                  </span>
                                  <span className="text-[10px] font-semibold text-slate-400">
                                    {les.content_type}
                                  </span>
                                </div>
                                <h5 className="font-bold text-xs text-slate-100 group-hover/sub:text-emerald-300 transition-colors leading-relaxed">
                                  {les.title}
                                </h5>
                                <p className="text-[11px] text-slate-300 italic font-medium">"{les.target_text}"</p>
                              </div>
                              <button className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 shadow-md group-hover/sub:scale-105 transition-all flex-shrink-0">
                                <Play size={12} />
                                <span>Practice</span>
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Sub-Modules Practice Lessons List */}
            <div className="space-y-3 pt-4">
              <div className="flex items-center justify-between">
                <h4 className="text-md font-bold text-slate-200 flex items-center gap-2">
                  <Sparkles size={16} className="text-emerald-400" />
                  {selectedCategoryFilter === 1 
                    ? 'Spoken Curriculum: Zero Level Foundational Modules' 
                    : selectedCategoryFilter === 2 
                    ? 'Written Curriculum: Zero Level Foundational Modules' 
                    : selectedCategoryFilter === 3 
                    ? 'Reading Curriculum: Zero Level Foundational Modules' 
                    : 'Recommended Zero Level Foundational Modules'}
                </h4>
                {selectedCategoryFilter !== null && (
                  <button 
                    onClick={() => setSelectedCategoryFilter(null)}
                    className="text-xs text-emerald-400 hover:underline font-semibold"
                  >
                    Show All Curriculums
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {(dbLessons || sampleLessons)
                  .filter(les => selectedCategoryFilter === null || les.category_id === selectedCategoryFilter)
                  .map(les => (
                    <div 
                      key={les.lesson_id}
                      onClick={() => setActiveLesson(les)}
                      className="glass-card p-4 rounded-xl border border-slate-700/80 hover:border-emerald-500/60 cursor-pointer transition-all flex items-center justify-between group hover:bg-slate-800/90 shadow-md"
                    >
                      <div className="space-y-1.5 pr-2">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-bold uppercase text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                            {les.content_type}
                          </span>
                          <span className="text-[10px] font-extrabold uppercase text-amber-300 px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                            Stage: {les.difficulty_level}
                          </span>
                        </div>
                        <h5 className="font-bold text-sm text-slate-100 group-hover:text-emerald-300 transition-colors">
                          {les.title}
                        </h5>
                        <p className="text-xs text-slate-300 italic font-medium">"{les.target_text}"</p>
                      </div>
                      <div className="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center group-hover:bg-emerald-500 group-hover:text-white transition-all shadow-md flex-shrink-0">
                        <Play size={18} />
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
