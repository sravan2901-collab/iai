import React, { useState } from 'react';
import { BookOpen, Volume2, CheckCircle, Sparkles, Eye, ArrowLeft, ArrowRight, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

export default function ReadingStudioCard({ lesson, onClose }) {
  const targetText = lesson?.target_text || "Open, Closed, Exit, Stop";
  const words = (targetText || "").split(/[\s,–—]+/).filter(Boolean);

  const [selectedWordIdx, setSelectedWordIdx] = useState(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [completedWords, setCompletedWords] = useState(new Set());
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizScore, setQuizScore] = useState(null);
  const [quizTargetIdx, setQuizTargetIdx] = useState(0);

  const EMOJI_MAP = {
    'Cow': '🐄', 'cow': '🐄', 'ஆடு': '🐐', 'ஆவு': '🐄', 'गाय': '🐄', 'গরু': '🐄',
    'House': '🏠', 'house': '🏠', 'வீடு': '🏠', 'ఇల్లు': '🏠', 'घर': '🏠', 'मने': '🏠',
    'Tree': '🌳', 'tree': '🌳', 'மரம்': '🌳', 'చెట్టు': '🌳', 'पेड़': '🌳', 'গাছ': '🌳',
    'Apple': '🍎', 'apple': '🍎', 'பழம்': '🍎', 'పండు': '🍎', 'सेब': '🍎', 'আপেল': '🍎',
    'Exit': '🚪', 'exit': '🚪', 'வெளியேற்றம்': '🚪', 'నిష్క్రమణ': '🚪', 'निकास': '🚪', 'प्रस्थान': '🚪',
    'Stop': '🛑', 'stop': '🛑', 'நில்லுங்கள்': '🛑', 'ఆగుము': '🛑', 'रुकिए': '🛑', 'থামুন': '🛑',
    'Restroom': '🚻', 'restroom': '🚻', 'கழிப்பறை': '🚻', 'శౌచాలయం': '🚻', 'शौचालय': '🚻', 'শৌচাগার': '🚻',
    'Danger': '⚠️', 'danger': '⚠️', 'அபாயம்': '⚠️', 'ప్రమాదం': '⚠️', 'खतरा': '⚠️', 'বিপদ': '⚠️'
  };

  const getEmojiForWord = (w) => {
    if (!w) return null;
    const cleanW = w.replace(/[(),]/g, '').trim();
    return EMOJI_MAP[cleanW] || null;
  };

  const playWordAudio = (wordToSpeak) => {
    setIsPlayingAudio(true);
    try {
      const cleanText = (wordToSpeak || targetText).replace(/[.,!?;:'"\\\/\-_]/g, ' ').trim();
      const encodedText = encodeURIComponent(cleanText.slice(0, 200));
      const audioUrl = `${API_BASE_URL}/voice/tts?text=${encodedText}&lang=${lesson?.lang || 'te'}`;
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlayingAudio(false);
      audio.onerror = () => setIsPlayingAudio(false);
      audio.play().catch(() => setIsPlayingAudio(false));
    } catch (e) {
      setIsPlayingAudio(false);
    }
  };

  const markWordRead = (idx) => {
    const newSet = new Set(completedWords);
    newSet.add(idx);
    setCompletedWords(newSet);
    playWordAudio(words[idx]);
  };

  const startAudioQuiz = () => {
    setShowQuiz(true);
    const validWords = words.length > 0 ? words : ["Open", "Closed", "Exit", "Stop"];
    const randomIdx = Math.floor(Math.random() * Math.min(4, validWords.length));
    setQuizTargetIdx(randomIdx);
    setQuizScore(null);
    playWordAudio(validWords[randomIdx]);
  };

  const handleQuizSubmit = (selectedWord) => {
    const targetWord = words[quizTargetIdx];
    const isCorrect = selectedWord === targetWord;
    setQuizScore(isCorrect ? 100 : 50);
  };

  return (
    <div className="glass-panel max-w-3xl mx-auto rounded-2xl p-6 md:p-8 space-y-6 animate-fade-in border border-slate-700/80 shadow-2xl">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-4">
        <div className="flex items-center gap-3">
          {onClose && (
            <button 
              onClick={onClose}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-300 transition-all"
              title="Return to modules catalog"
            >
              <ArrowLeft size={20} />
            </button>
          )}
          <div>
            <span className="text-xs uppercase tracking-wider font-semibold text-emerald-400 flex items-center gap-1.5">
              <BookOpen size={14} />
              Functional Reading & Sight Recognition Studio
            </span>
            <h3 className="text-xl font-bold text-slate-100">{lesson?.title || "Reading Practice Module"}</h3>
          </div>
        </div>

        <button
          onClick={() => playWordAudio(targetText)}
          className="p-2.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 rounded-xl flex items-center gap-2 text-xs font-semibold transition-all"
        >
          <Volume2 size={16} className={isPlayingAudio ? 'animate-bounce text-emerald-400' : ''} />
          <span>{isPlayingAudio ? 'Reading...' : 'Read Full Sentence'}</span>
        </button>
      </div>

      {/* Main Flashcard / Signboard Reader View */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 rounded-2xl p-8 border border-slate-800 text-center space-y-6 shadow-inner">
        <div className="space-y-1">
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center justify-center gap-1.5">
            <Eye size={14} />
            Visual Sight Reading Target:
          </span>
          <p className="text-xs text-slate-400">Click any word below to listen and practice sight recognition</p>
        </div>

        {/* Word Flashcards Grid */}
        <div className="flex flex-wrap items-center justify-center gap-4 py-4">
          {words.map((word, idx) => {
            const isSelected = selectedWordIdx === idx;
            const isCompleted = completedWords.has(idx);
            const emojiBadge = getEmojiForWord(word);

            return (
              <button
                key={idx}
                onClick={() => {
                  setSelectedWordIdx(idx);
                  markWordRead(idx);
                }}
                className={`px-5 py-3.5 rounded-2xl font-extrabold text-2xl md:text-3xl transition-all flex items-center gap-2 shadow-lg cursor-pointer ${
                  isSelected
                    ? 'bg-emerald-500 text-white ring-4 ring-emerald-500/40 scale-110'
                    : isCompleted
                    ? 'bg-slate-800 text-emerald-300 border border-emerald-500/40 hover:bg-slate-700'
                    : 'bg-slate-900/90 text-amber-300 border border-slate-700 hover:border-emerald-500/60 hover:bg-slate-800'
                }`}
              >
                {emojiBadge && <span className="text-2xl">{emojiBadge}</span>}
                <span>{word}</span>
                {isCompleted && <CheckCircle size={18} className="text-emerald-400" />}
              </button>
            );
          })}
        </div>

        {/* Active Selected Word Focus Panel */}
        {words[selectedWordIdx] && (
          <div className="bg-slate-950/90 p-4 rounded-xl border border-slate-800 inline-block max-w-md w-full space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Active Focus Word:
            </span>
            <div className="text-2xl font-black text-emerald-300 flex items-center justify-center gap-2">
              {getEmojiForWord(words[selectedWordIdx]) && <span>{getEmojiForWord(words[selectedWordIdx])}</span>}
              <span>"{words[selectedWordIdx]}"</span>
            </div>
            <div className="flex items-center justify-center gap-2 pt-1">
              <button
                onClick={() => playWordAudio(words[selectedWordIdx])}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-md transition-all"
              >
                <Volume2 size={14} />
                <span>Listen Word</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Progress & Quiz Action Bar */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-xs text-slate-400 font-medium flex items-center gap-2">
          <span className="font-extrabold text-emerald-400">{completedWords.size} of {words.length}</span>
          <span>words sight-read</span>
        </div>

        <button
          onClick={() => {
            if (!showQuiz) startAudioQuiz();
            else setShowQuiz(false);
          }}
          className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-lg transition-all"
        >
          <Sparkles size={14} />
          <span>{showQuiz ? 'Hide Sight Recognition Quiz' : 'Take Audio Sight Recognition Quiz'}</span>
        </button>
      </div>

      {/* Sight Recognition Quiz */}
      {showQuiz && (
        <div className="bg-slate-900/90 rounded-2xl p-6 border border-emerald-500/40 space-y-4 animate-fade-in shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Sparkles size={16} />
              Audio Sight Recognition Quiz — Select the word you heard:
            </span>
            <button
              onClick={() => playWordAudio(words[quizTargetIdx])}
              className="p-2 bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-slate-700 rounded-lg text-xs font-bold flex items-center gap-1"
            >
              <Volume2 size={14} />
              <span>Replay Audio</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            {words.slice(0, 4).map((w, i) => (
              <button
                key={i}
                onClick={() => handleQuizSubmit(w)}
                className="p-3.5 rounded-xl bg-slate-950 hover:bg-emerald-950/60 border border-slate-800 hover:border-emerald-500/60 text-slate-100 font-bold text-sm text-center flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                {getEmojiForWord(w) && <span>{getEmojiForWord(w)}</span>}
                <span>{w}</span>
              </button>
            ))}
          </div>

          {quizScore !== null && (
            <div className={`p-4 rounded-xl flex items-center justify-between text-xs ${
              quizScore === 100 ? 'bg-emerald-950/50 border border-emerald-500/40 text-emerald-300' : 'bg-rose-950/40 border border-rose-500/40 text-rose-300'
            }`}>
              <span className="font-extrabold">
                {quizScore === 100 ? '🎉 Correct! 100% Audio Sight Recognition Accuracy!' : '❌ Try again! Replay audio to match the correct word card.'}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
