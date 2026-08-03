import React, { useState, useEffect } from 'react';
import { ShieldCheck, Award, BookOpen, CheckCircle, ArrowRight, Globe, Sparkles, RefreshCw, Zap } from 'lucide-react';
import { apiRequest } from '../services/api';

export default function ProficiencyBenchmarks({ selectedLang = 'en' }) {
  const [activeLang, setActiveLang] = useState(selectedLang);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(true);

  const LANG_NAMES = {
    en: 'English',
    hi: 'Hindi (हिन्दी)',
    te: 'Telugu (తెలుగు)',
    ta: 'Tamil (தமிழ்)',
    mr: 'Marathi (मराठी)',
    bn: 'Bengali (বাংলা)',
    kn: 'Kannada (ಕನ್ನಡ)',
    es: 'Spanish (Español)'
  };

  useEffect(() => {
    setActiveLang(selectedLang);
  }, [selectedLang]);

  useEffect(() => {
    const fetchBenchmarks = async () => {
      setLoading(true);
      try {
        const data = await apiRequest(`/assessment/benchmarks?lang=${activeLang}`);
        setBenchmarkData(data);
      } catch (err) {
        // Fallback dataset
        setBenchmarkData({
          language_name: LANG_NAMES[activeLang] || 'English',
          tiers: [
            {
              tier: "FOUNDATIONAL",
              score_range: "0 – 44 Marks",
              title: activeLang === 'te' ? "అక్షరాలు మరియు గుణింతాల ప్రమాణం" : "Alphabet & Phonemes Benchmark",
              description: activeLang === 'te' ? "అచ్చులు, హల్లులు, గుణింతాల గుర్తులు మరియు ఒత్తులను గుర్తించి పలికే ప్రాథమిక సామర్థ్యం." : "Mastery over letter-sound associations, vowel phonemes, and basic syllable blends.",
              competencies: ["Phoneme Identification", "Single Syllable Reading", "Simple Word Spelling"]
            },
            {
              tier: "FUNCTIONAL",
              score_range: "45 – 74 Marks",
              title: activeLang === 'te' ? "పదజాలం మరియు వ్యాకరణ ప్రమాణం" : "Vocabulary & Grammar Benchmark",
              description: activeLang === 'te' ? "పర్యాయపదాలు, నానార్థాలు, సంధులు మరియు వాక్య వ్యాకరణంలో ప్రావీణ్యం సాధించే స్థాయి." : "Ability to form words with prefixes/suffixes, manage noun-verb agreement, and comprehend compound sentences.",
              competencies: ["Synonym & Antonym Usage", "Verb Tense Conjugation", "Compound Sentence Reading"]
            },
            {
              tier: "PROFICIENT",
              score_range: "75 – 100 Marks",
              title: activeLang === 'te' ? "ఉన్నత సాహిత్య ప్రవీణతా ప్రమాణం" : "Advanced Literary Fluency Benchmark",
              description: activeLang === 'te' ? "ఉన్నత సాహిత్య గద్యాలను అవగాహన చేసుకోవడం మరియు అనర్గళంగా భావ వ్యక్తీకరణ చేయడం." : "Full competence in prose passage comprehension, orthography, and articulate speech expression.",
              competencies: ["Literary Passage Analysis", "Orthographic Accuracy", "Fluent Articulate Speech"]
            }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchBenchmarks();
  }, [activeLang]);

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500">
      
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-700/60 bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1 text-center md:text-left">
          <h2 className="text-xl font-bold flex items-center justify-center md:justify-start gap-2 text-emerald-400">
            <Award size={22} className="text-amber-400" />
            Language Proficiency Benchmarks ({LANG_NAMES[activeLang] || activeLang.toUpperCase()})
          </h2>
          <p className="text-xs text-slate-300">
            Official performance bands, target score ranges, and skill competencies established for neo-learners.
          </p>
        </div>

        {/* Language Switcher */}
        <div className="flex items-center gap-2 bg-slate-900/90 px-3 py-2 rounded-xl border border-slate-700 text-xs">
          <Globe size={16} className="text-emerald-400" />
          <select
            value={activeLang}
            onChange={(e) => setActiveLang(e.target.value)}
            className="bg-transparent text-slate-100 font-bold focus:outline-none cursor-pointer"
          >
            {Object.entries(LANG_NAMES).map(([code, name]) => (
              <option key={code} value={code} className="bg-slate-900 text-white">
                {name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading || !benchmarkData ? (
        <div className="glass-panel p-8 text-center rounded-2xl space-y-3">
          <RefreshCw className="animate-spin text-emerald-400 mx-auto" size={28} />
          <p className="text-xs text-slate-300">Loading language benchmarks for {LANG_NAMES[activeLang]}...</p>
        </div>
      ) : (
        /* Benchmark Tiers Matrix */
        <div className="space-y-4">
          {benchmarkData.tiers?.map((tierItem, idx) => {
            const isFoundational = tierItem.tier === 'FOUNDATIONAL';
            const isFunctional = tierItem.tier === 'FUNCTIONAL';
            const isProficient = tierItem.tier === 'PROFICIENT';

            const borderColor = isFoundational ? 'border-emerald-500/40' : (isFunctional ? 'border-blue-500/40' : 'border-amber-500/40');
            const badgeBg = isFoundational ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : (isFunctional ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' : 'bg-amber-500/20 text-amber-300 border-amber-500/30');

            return (
              <div 
                key={idx}
                className={`glass-panel p-6 rounded-2xl border ${borderColor} bg-slate-900/80 space-y-4 transition-all hover:border-emerald-400/60 shadow-lg`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-700/60 pb-3">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-black px-3 py-1 rounded-full border ${badgeBg}`}>
                      {tierItem.tier} TIER
                    </span>
                    <h3 className="text-base font-bold text-slate-100">{tierItem.title}</h3>
                  </div>

                  <span className="text-xs font-black text-amber-400 bg-amber-950/60 px-3 py-1 rounded-lg border border-amber-500/30 self-start sm:self-auto">
                    Score Range: {tierItem.score_range}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">{tierItem.description}</p>

                {/* Competencies Badges */}
                <div className="space-y-2 pt-1">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Core Target Competencies:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {tierItem.competencies?.map((comp, cIdx) => (
                      <span 
                        key={cIdx}
                        className="text-xs font-semibold px-3 py-1 rounded-xl bg-slate-800 border border-slate-700 text-slate-200 flex items-center gap-1.5"
                      >
                        <CheckCircle size={14} className="text-emerald-400" />
                        <span>{comp}</span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
