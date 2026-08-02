import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

export default function VoiceGuide({ currentLang = 'en-US' }) {
  const [enabled, setEnabled] = useState(true);

  const speakText = (text) => {
    if (!enabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel(); // stop previous
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLang;
    utterance.rate = 0.9; // clear speech for learners
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => {
          const nextState = !enabled;
          setEnabled(nextState);
          if (nextState) speakText("Voice assistance is enabled");
        }}
        className={`px-3 py-1.5 rounded-full flex items-center gap-2 text-xs font-medium transition-all ${
          enabled 
            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-sm shadow-emerald-500/20' 
            : 'bg-slate-800/80 text-slate-400 border border-slate-700'
        }`}
        title="Voice Guide for Accessibility"
      >
        {enabled ? <Volume2 size={16} className="animate-pulse" /> : <VolumeX size={16} />}
        <span>{enabled ? "Voice Assistant ON" : "Voice Assistant OFF"}</span>
      </button>
    </div>
  );
}
