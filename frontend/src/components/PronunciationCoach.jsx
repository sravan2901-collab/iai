import React, { useState } from 'react';
import { Mic, Volume2, RotateCcw, Sparkles } from 'lucide-react';
import AudioVisualizer from './AudioVisualizer';

export default function PronunciationCoach({ lesson, onScoreUpdate }) {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaStream, setMediaStream] = useState(null);
  const [evaluation, setEvaluation] = useState(null);

  const targetText = lesson?.target_text || "Hello, how are you today?";

  const playBenchmarkAudio = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(targetText);
    utterance.lang = "en-US";
    utterance.rate = 0.85;
    window.speechSynthesis.speak(utterance);
  };

  const playSlowMotionAudio = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(targetText);
    utterance.lang = "en-US";
    utterance.rate = 0.5; // slow-motion breakdown
    window.speechSynthesis.speak(utterance);
  };

  const startRecording = async () => {
    setEvaluation(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMediaStream(stream);
      setIsRecording(true);

      // Simulate sending audio blob to STT & backend phoneme scorer
      setTimeout(() => {
        setIsRecording(false);
        stream.getTracks().forEach(track => track.stop());

        const mockEval = {
          overall_score: 92.0,
          phoneme_accuracy: 94.5,
          syllable_score: 90.0,
          word_feedback: {
            "Hello,": "green",
            "how": "green",
            "are": "green",
            "you": "green",
            "today?": "yellow"
          },
          remediation_tip: "Excellent pronunciation! Pay slight attention to stressing the word 'today'."
        };

        setEvaluation(mockEval);
        if (onScoreUpdate) onScoreUpdate(mockEval.overall_score);
      }, 3500);
    } catch (err) {
      alert("Microphone permission required for speech practice.");
    }
  };

  return (
    <div className="glass-panel max-w-2xl mx-auto rounded-2xl p-6 md:p-8 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-4">
        <div>
          <span className="text-xs uppercase tracking-wider font-semibold text-emerald-400">
            AI Pronunciation & Speech Coach
          </span>
          <h3 className="text-xl font-bold text-slate-100">{lesson?.title || "Speech Practice Module"}</h3>
        </div>
        <button
          onClick={playBenchmarkAudio}
          className="p-3 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 rounded-xl flex items-center gap-2 text-sm font-medium transition-all"
        >
          <Volume2 size={18} />
          <span>Listen</span>
        </button>
      </div>

      {/* Target Word Highlight Card */}
      <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-700/80 text-center space-y-4 shadow-inner">
        <span className="text-xs text-slate-400">Target Practice Sentence:</span>
        <div className="flex flex-wrap items-center justify-center gap-3 text-2xl md:text-3xl font-bold tracking-wide">
          {targetText.split(' ').map((word, idx) => {
            const status = evaluation?.word_feedback?.[word];
            let colorClass = "text-amber-300 border-b-2 border-amber-400/40";

            if (status === 'green') colorClass = "text-emerald-400 border-b-2 border-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded";
            if (status === 'yellow') colorClass = "text-amber-400 border-b-2 border-amber-400 bg-amber-500/10 px-2 py-0.5 rounded";
            if (status === 'red') colorClass = "text-rose-400 border-b-2 border-rose-400 bg-rose-500/10 px-2 py-0.5 rounded";

            return (
              <span key={idx} className={`${colorClass} transition-all`}>
                {word}
              </span>
            );
          })}
        </div>
      </div>

      <AudioVisualizer isRecording={isRecording} mediaStream={mediaStream} />

      {/* Recording Actions */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={startRecording}
          disabled={isRecording}
          className={`flex-1 py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
            isRecording 
              ? 'bg-rose-600 text-white mic-active' 
              : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/30'
          }`}
        >
          <Mic size={22} />
          <span>{isRecording ? "Listening to your voice..." : "Tap Microphone & Speak Aloud"}</span>
        </button>

        <button
          onClick={playSlowMotionAudio}
          className="p-4 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-xl flex items-center gap-2 text-xs font-semibold"
          title="Slow Motion Syllable Breakdown"
        >
          <RotateCcw size={16} />
          <span>Slow-Mo Breakdown</span>
        </button>
      </div>

      {/* Evaluation Results Card */}
      {evaluation && (
        <div className="glass-card rounded-xl p-5 border border-emerald-500/30 space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-bold">
              <Sparkles size={20} />
              <span>Pronunciation Accuracy Score</span>
            </div>
            <span className="text-2xl font-black text-emerald-400">{evaluation.overall_score}%</span>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center text-xs">
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block">Accuracy</span>
              <span className="text-sm font-bold text-emerald-300">{evaluation.phoneme_accuracy}%</span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block">Syllables</span>
              <span className="text-sm font-bold text-amber-300">{evaluation.syllable_score}%</span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block">Status</span>
              <span className="text-sm font-bold text-emerald-400">🟢 Excellent</span>
            </div>
          </div>

          <p className="text-xs text-slate-300 bg-emerald-950/30 p-3 rounded-lg border border-emerald-500/20">
            💡 <strong>AI Coaching Tip:</strong> {evaluation.remediation_tip}
          </p>
        </div>
      )}
    </div>
  );
}
