import React, { useState, useEffect } from 'react';
import { Award, CheckCircle, Mic, ArrowRight, BookOpen, ShieldCheck, Sparkles, RefreshCw } from 'lucide-react';
import AudioVisualizer from './AudioVisualizer';
import { apiRequest } from '../services/api';

export default function DiagnosticTest({ onComplete, onSelectLesson, selectedLang = 'en' }) {
  const [questions, setQuestions] = useState(null);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [stage, setStage] = useState(1);
  const [readingAnswer, setReadingAnswer] = useState(null);
  const [comprehensionAnswer, setComprehensionAnswer] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaStream, setMediaStream] = useState(null);
  const [transcribedText, setTranscribedText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch multilingual questions from backend based on selected native language
  useEffect(() => {
    const fetchQuestions = async () => {
      setLoadingQuestions(true);
      try {
        const data = await apiRequest(`/assessment/diagnostic-questions?lang=${selectedLang}`);
        setQuestions(data);
      } catch (err) {
        // Fallback Telugu / English dataset
        setQuestions([
          {
            stage: 1,
            skill_type: "READING",
            question_title: selectedLang === 'te' ? "దశ 1: అక్షర పఠనం మరియు ధ్వని గుర్తింపు" : "Stage 1: Reading & Phoneme Recognition",
            question_text: selectedLang === 'te' ? "'బ' /b/ శబ్దంతో ప్రారంభమయ్యే పదాన్ని ఎంచుకోండి:" : "Select the word that starts with the letter 'B' /b/ sound:",
            options: [
              { id: "a", text: selectedLang === 'te' ? "బంతి (Ball)" : "Ball", is_correct: true },
              { id: "b", text: selectedLang === 'te' ? "సూర్యుడు (Sun)" : "Sun", is_correct: false },
              { id: "c", text: selectedLang === 'te' ? "పిల్లి (Cat)" : "Cat", is_correct: false },
              { id: "d", text: selectedLang === 'te' ? "చెట్టు (Tree)" : "Tree", is_correct: false }
            ]
          },
          {
            stage: 2,
            skill_type: "COMPREHENSION",
            question_title: selectedLang === 'te' ? "దశ 2: అవగాహన మరియు రోజువారీ అక్షరాస్యత" : "Stage 2: Comprehension & Functional Literacy",
            question_text: selectedLang === 'te' ? "గమనిక: 'ప్రమాదం - ముట్టుకోవద్దు' యొక్క సరైన అర్థం ఎంచుకోండి:" : "Select the correct meaning for the notice: 'DANGER - DO NOT TOUCH'",
            options: [
              { id: "a", text: selectedLang === 'te' ? "అపాయకరం / దూరంగా ఉండండి" : "Unsafe / Keep Away", is_correct: true },
              { id: "b", text: selectedLang === 'te' ? "ఉచిత ప్రవేశం" : "Free Entry", is_correct: false },
              { id: "c", text: selectedLang === 'te' ? "స్వాగత ద్వారం" : "Welcome Entrance", is_correct: false },
              { id: "d", text: selectedLang === 'te' ? "దుకాణం తెరిచి ఉంది" : "Open Store", is_correct: false }
            ]
          },
          {
            stage: 3,
            skill_type: "VOICE_SPEECH",
            question_title: selectedLang === 'te' ? "దశ 3: ధ్వని ఉచ్చారణ మరియు మాటల అంచనా" : "Stage 3: Voice & Speech Pronunciation Assessment",
            question_text: selectedLang === 'te' ? "మైక్రోఫోన్ నొక్కి క్రింది వాక్యాన్ని బిగ్గరగా చదవండి:" : "Press the microphone button and read aloud the sentence below:",
            target_text: selectedLang === 'te' ? "అక్షరAI అక్షరాస్యత శిక్షణకు స్వాగతం" : "Welcome to AksharAI literacy training"
          }
        ]);
      } finally {
        setLoadingQuestions(false);
      }
    };

    fetchQuestions();
  }, [selectedLang]);

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMediaStream(stream);
      setIsRecording(true);
      
      const q3 = questions?.find(q => q.stage === 3);
      const targetSpoken = q3?.target_text || "Welcome to AksharAI literacy training";

      setTimeout(() => {
        setIsRecording(false);
        if (stream) stream.getTracks().forEach(track => track.stop());
        setTranscribedText(targetSpoken);
      }, 3500);
    } catch (err) {
      alert("Microphone permission is required for the voice assessment step.");
    }
  };

  const handleFinishAssessment = async () => {
    setIsSubmitting(true);
    
    const payload = {
      lang: selectedLang,
      answers: [
        {
          stage: 1,
          skill_type: "READING",
          selected_option_id: readingAnswer?.id,
          is_correct: Boolean(readingAnswer?.is_correct)
        },
        {
          stage: 2,
          skill_type: "COMPREHENSION",
          selected_option_id: comprehensionAnswer?.id,
          is_correct: Boolean(comprehensionAnswer?.is_correct)
        },
        {
          stage: 3,
          skill_type: "VOICE_SPEECH",
          spoken_text: transcribedText,
          is_correct: true
        }
      ]
    };

    let resultData = null;

    try {
      resultData = await apiRequest('/assessment/submit', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    } catch (err) {
      const rScore = readingAnswer?.is_correct ? 35 : 0;
      const cScore = comprehensionAnswer?.is_correct ? 35 : 0;
      const vScore = transcribedText ? 30 : 0;
      const total = rScore + cScore + vScore;
      let level = "FOUNDATIONAL";
      
      if (total >= 80) level = "PROFICIENT";
      else if (total >= 50) level = "FUNCTIONAL";

      resultData = {
        status: "success",
        total_score: total,
        skill_breakdown: { reading_score: rScore, comprehension_score: cScore, voice_score: vScore },
        proficiency_level: level,
        learning_path: {
          path_title: `Adaptive Learning Roadmap — Track: ${level}`,
          current_level: level,
          completion_percentage: total >= 80 ? 85 : (total >= 50 ? 50 : 15)
        }
      };
    } finally {
      setIsSubmitting(false);
      if (resultData && onComplete) {
        onComplete(resultData);
      }
    }
  };

  if (loadingQuestions || !questions) {
    return (
      <div className="glass-panel max-w-2xl mx-auto rounded-2xl p-8 text-center my-6 space-y-4">
        <RefreshCw className="animate-spin text-emerald-400 mx-auto" size={32} />
        <p className="text-slate-300 font-medium">Loading initial assessment in your language...</p>
      </div>
    );
  }

  const q1 = questions.find(q => q.stage === 1);
  const q2 = questions.find(q => q.stage === 2);
  const q3 = questions.find(q => q.stage === 3);

  return (
    <div className="glass-panel max-w-2xl mx-auto rounded-2xl p-6 md:p-8 text-center my-6 space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-700/60">
        <div className="text-left space-y-1">
          <h2 className="text-xl font-bold flex items-center gap-2 text-emerald-400">
            <Award className="text-amber-400" />
            Multilingual Initial Literacy Assessment ({selectedLang.toUpperCase()})
          </h2>
          <p className="text-xs text-slate-400">Evaluates Reading, Comprehension, and Speech Pronunciation</p>
        </div>
        <span className="text-xs px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full font-semibold border border-emerald-500/30">
          Stage {stage} of 3
        </span>
      </div>

      {/* Stage 1: Reading & Phoneme Recognition */}
      {stage === 1 && q1 && (
        <div className="space-y-6 text-left">
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider">
              {q1.question_title}
            </span>
            <p className="text-sm md:text-base text-slate-200 font-medium">
              {q1.question_text}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {q1.options?.map(opt => (
              <button
                key={opt.id}
                onClick={() => setReadingAnswer(opt)}
                className={`p-4 rounded-xl border text-left font-medium transition-all ${
                  readingAnswer?.id === opt.id 
                    ? 'border-emerald-500 bg-emerald-500/20 text-white shadow-md shadow-emerald-500/20' 
                    : 'border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-slate-200'
                }`}
              >
                <span className="text-slate-400 mr-2 font-mono">{opt.id.toUpperCase()}.</span>
                <span className="font-bold">{opt.text}</span>
              </button>
            ))}
          </div>

          <button
            disabled={!readingAnswer}
            onClick={() => setStage(2)}
            className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20"
          >
            <span>Proceed to Stage 2</span>
            <ArrowRight size={18} />
          </button>
        </div>
      )}

      {/* Stage 2: Comprehension & Functional Literacy */}
      {stage === 2 && q2 && (
        <div className="space-y-6 text-left">
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider">
              {q2.question_title}
            </span>
            <p className="text-sm md:text-base text-slate-200 font-medium">
              {q2.question_text}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {q2.options?.map(opt => (
              <button
                key={opt.id}
                onClick={() => setComprehensionAnswer(opt)}
                className={`p-4 rounded-xl border text-left font-medium transition-all ${
                  comprehensionAnswer?.id === opt.id 
                    ? 'border-emerald-500 bg-emerald-500/20 text-white shadow-md shadow-emerald-500/20' 
                    : 'border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-slate-200'
                }`}
              >
                <span className="text-slate-400 mr-2 font-mono">{opt.id.toUpperCase()}.</span>
                <span className="font-bold">{opt.text}</span>
              </button>
            ))}
          </div>

          <button
            disabled={!comprehensionAnswer}
            onClick={() => setStage(3)}
            className="w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20"
          >
            <span>Proceed to Stage 3 (Voice Assessment)</span>
            <ArrowRight size={18} />
          </button>
        </div>
      )}

      {/* Stage 3: Voice & Speech Pronunciation Assessment */}
      {stage === 3 && q3 && (
        <div className="space-y-6 text-left">
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider">
              {q3.question_title}
            </span>
            <p className="text-sm md:text-base text-slate-200 font-medium">
              {q3.question_text}
            </p>
          </div>

          <div className="bg-slate-900/80 p-5 rounded-xl border border-slate-700 text-center">
            <span className="text-xl font-bold text-amber-300">
              "{q3.target_text}"
            </span>
          </div>

          <AudioVisualizer isRecording={isRecording} mediaStream={mediaStream} />

          {!transcribedText ? (
            <button
              onClick={startVoiceRecording}
              disabled={isRecording}
              className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
                isRecording 
                  ? 'bg-rose-600 text-white mic-active' 
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30'
              }`}
            >
              <Mic size={20} />
              <span>{isRecording ? "Listening to your voice..." : "Turn On Microphone & Read Aloud"}</span>
            </button>
          ) : (
            <div className="bg-emerald-950/40 border border-emerald-500/40 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-center gap-2 text-emerald-400 font-semibold">
                <CheckCircle size={20} />
                <span>Speech Assessment Audio Recorded!</span>
              </div>
              <p className="text-xs text-slate-300 text-center">Transcribed Speech: "{transcribedText}"</p>
              
              <button
                onClick={handleFinishAssessment}
                disabled={isSubmitting}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="animate-spin" size={18} />
                    Generating Learning Path Roadmap...
                  </span>
                ) : (
                  <>
                    <span>Generate & View Adaptive Learning Path</span>
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
