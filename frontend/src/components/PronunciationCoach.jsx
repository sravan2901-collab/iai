import React, { useState, useRef, useCallback } from 'react';
import { Mic, Volume2, RotateCcw, Sparkles, MicOff, Loader } from 'lucide-react';
import AudioVisualizer from './AudioVisualizer';
import { apiRequest } from '../services/api';
import { playSynthesizedPhoneme } from '../utils/audioSynthesizer';

/**
 * Compute word-level similarity between target and spoken text.
 * Uses normalized Levenshtein-like comparison per word.
 */
function computePronunciationScore(targetText, spokenText) {
  const normalize = (s) => s.toLowerCase().replace(/[^a-z0-9\u0900-\u097F\u0C00-\u0C7F\u0B80-\u0BFF\u0980-\u09FF\u0C80-\u0CFF\u00C0-\u017F\s]/g, '').trim();
  const targetWords = normalize(targetText).split(/\s+/).filter(Boolean);
  const spokenWords = normalize(spokenText).split(/\s+/).filter(Boolean);

  if (targetWords.length === 0) return { overall_score: 0, phoneme_accuracy: 0, syllable_score: 0, word_feedback: {}, remediation_tip: "No target text." };

  // Levenshtein distance for individual words
  function levenshtein(a, b) {
    const m = a.length, n = b.length;
    const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;
    for (let i = 1; i <= m; i++)
      for (let j = 1; j <= n; j++)
        dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    return dp[m][n];
  }

  // Match each target word to the best spoken word
  const wordFeedback = {};
  let totalWordScore = 0;
  const usedSpoken = new Set();

  const originalTargetWords = targetText.replace(/[.,!?;:'"]/g, '').split(/\s+/).filter(Boolean);

  for (let i = 0; i < targetWords.length; i++) {
    const tw = targetWords[i];
    const displayWord = originalTargetWords[i] || tw;
    let bestScore = 0;
    let bestIdx = -1;

    for (let j = 0; j < spokenWords.length; j++) {
      if (usedSpoken.has(j)) continue;
      const sw = spokenWords[j];
      const maxLen = Math.max(tw.length, sw.length);
      const dist = levenshtein(tw, sw);
      const similarity = maxLen === 0 ? 1 : 1 - dist / maxLen;
      if (similarity > bestScore) {
        bestScore = similarity;
        bestIdx = j;
      }
    }

    if (bestIdx >= 0 && bestScore > 0.3) {
      usedSpoken.add(bestIdx);
    }

    // Classify: green >= 80%, yellow >= 50%, red < 50%
    const pct = bestScore * 100;
    if (pct >= 80) wordFeedback[displayWord] = 'green';
    else if (pct >= 50) wordFeedback[displayWord] = 'yellow';
    else wordFeedback[displayWord] = 'red';

    totalWordScore += bestScore;
  }

  const accuracy = (totalWordScore / targetWords.length) * 100;

  // Syllable score: how many target words were found at all in spoken text
  const foundCount = Object.values(wordFeedback).filter(v => v !== 'red').length;
  const syllableScore = (foundCount / targetWords.length) * 100;

  // Overall: weighted average
  const overall = Math.round(accuracy * 0.6 + syllableScore * 0.4);

  // Count problem areas
  const redWords = Object.entries(wordFeedback).filter(([, v]) => v === 'red').map(([k]) => k);
  const yellowWords = Object.entries(wordFeedback).filter(([, v]) => v === 'yellow').map(([k]) => k);

  let tip;
  if (overall >= 90) {
    tip = "Excellent pronunciation! Your speech closely matches the target text.";
  } else if (overall >= 70) {
    const issues = [...yellowWords, ...redWords].slice(0, 3).join(', ');
    tip = `Good effort! Practice these words more: ${issues || 'focus on clarity'}.`;
  } else if (overall >= 50) {
    const issues = [...redWords, ...yellowWords].slice(0, 3).join(', ');
    tip = `Keep practicing. Focus on pronouncing: ${issues || 'the full sentence'}. Try listening to the benchmark audio first.`;
  } else {
    tip = "Try listening to the benchmark audio first, then repeat slowly. Focus on one word at a time.";
  }

  return {
    overall_score: Math.min(Math.max(overall, 0), 100),
    phoneme_accuracy: Math.round(Math.min(accuracy, 100) * 10) / 10,
    syllable_score: Math.round(syllableScore * 10) / 10,
    word_feedback: wordFeedback,
    remediation_tip: tip
  };
}

export default function PronunciationCoach({ lesson, onScoreUpdate }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [mediaStream, setMediaStream] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [recognizedText, setRecognizedText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const targetText = lesson?.target_text || "Hello, how are you today?";

  const TTS_LANG_MAP = {
    'en': 'en-US',
    'te': 'te-IN',
    'hi': 'hi-IN',
    'ta': 'ta-IN',
    'mr': 'mr-IN',
    'bn': 'bn-IN',
    'kn': 'kn-IN',
    'es': 'es-ES'
  };

  const detectScriptLang = (text, fallback = 'en') => {
    if (!text) return fallback;
    if (/[\u0C00-\u0C7F]/.test(text)) return 'te'; // Telugu
    if (/[\u0900-\u097F]/.test(text)) return 'hi'; // Hindi / Devanagari
    if (/[\u0B80-\u0BFF]/.test(text)) return 'ta'; // Tamil
    if (/[\u0980-\u09FF]/.test(text)) return 'bn'; // Bengali
    if (/[\u0C80-\u0CFF]/.test(text)) return 'kn'; // Kannada
    if (/[áéíóúñÁÉÍÓÚÑ]/.test(text)) return 'es';  // Spanish
    return fallback;
  };

  const playNaturalSpeechAudio = (text, rateMultiplier = 0.85) => {
    const langCode = detectScriptLang(text, lesson?.lang || lesson?.lang_code || 'te');
    const ttsLang = TTS_LANG_MAP[langCode] || 'te-IN';
    const cleanText = text.replace(/[.,!?;:'"\\\/\-_]/g, ' ').trim();

    setIsPlayingAudio(true);

    try {
      // 1. Primary: High-Fidelity Local Backend Spoken Audio Endpoint (http://127.0.0.1:8000/api/voice/tts)
      const backendTtsUrl = `http://127.0.0.1:8000/api/voice/tts?text=${encodeURIComponent(cleanText.slice(0, 250))}&lang=${langCode}`;
      const audio = new Audio(backendTtsUrl);
      audio.playbackRate = rateMultiplier;
      
      audio.onended = () => {
        setIsPlayingAudio(false);
      };

      audio.onerror = (err) => {
        console.warn("Backend TTS stream fallback to browser Web Speech API:", err);
        playWebSpeechAPI(cleanText, ttsLang, langCode, rateMultiplier);
      };

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.warn("Audio play promise fallback:", err.message);
          playWebSpeechAPI(cleanText, ttsLang, langCode, rateMultiplier);
        });
      }
    } catch (e) {
      playWebSpeechAPI(cleanText, ttsLang, langCode, rateMultiplier);
    }
  };

  const playWebSpeechAPI = (cleanText, ttsLang, langCode, rateMultiplier) => {
    if (!('speechSynthesis' in window)) return;

    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = ttsLang;
      utterance.rate = rateMultiplier;

      const voices = window.speechSynthesis.getVoices() || [];
      const matchedVoice = voices.find(v => 
        v.lang.toLowerCase().startsWith(langCode) || 
        v.lang.toLowerCase().replaceAll('_', '-') === ttsLang.toLowerCase().replaceAll('_', '-')
      );

      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.warn("SpeechSynthesis error:", err);
    }
  };

  const playBenchmarkAudio = (rateMultiplier = 0.85) => {
    playNaturalSpeechAudio(targetText, rateMultiplier);
  };

  const playSlowMotionAudio = () => {
    playNaturalSpeechAudio(targetText, 0.5);
  };

  const stopRecording = useCallback(() => {
    setIsRecording(false);
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (e) { /* already stopped */ }
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      setMediaStream(null);
    }
  }, [mediaStream]);

  const startRecording = async () => {
    setEvaluation(null);
    setRecognizedText('');
    setErrorMsg('');
    audioChunksRef.current = [];

    // Check for SpeechRecognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setErrorMsg('Speech Recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    try {
      // 1. Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMediaStream(stream);
      setIsRecording(true);

      // 2. Set up MediaRecorder to capture audio blob (for backend)
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      mediaRecorder.start();

      // 3. Set up Web Speech API for real-time recognition
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US'; // Default — could be dynamic per language

      let finalTranscript = '';
      let interimTranscript = '';

      recognition.onresult = (event) => {
        interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript = transcript;
          }
        }
        setRecognizedText((finalTranscript + interimTranscript).trim());
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
          setErrorMsg('No speech detected. Please speak louder and try again.');
        }
      };

      recognition.onend = () => {
        // When recognition ends, compute the score
        const spokenText = finalTranscript.trim() || interimTranscript.trim();
        
        if (spokenText.length > 0) {
          setIsProcessing(true);
          const evalResult = computePronunciationScore(targetText, spokenText);
          setEvaluation(evalResult);
          setRecognizedText(spokenText);
          if (onScoreUpdate) onScoreUpdate(evalResult.overall_score);

          // Also try to send to backend for server-side scoring (non-blocking)
          try {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            if (audioBlob.size > 0 && lesson?.lesson_id && typeof lesson.lesson_id === 'number') {
              const formData = new FormData();
              formData.append('audio_file', audioBlob, 'recording.webm');
              formData.append('learner_id', '0');
              formData.append('lesson_id', String(lesson.lesson_id));
              apiRequest('/voice/evaluate', {
                method: 'POST',
                body: formData,
                isFormData: true
              }).catch(() => {}); // Silent fail — frontend scoring is primary
            }
          } catch (e) { /* ignore backend send errors */ }

          setIsProcessing(false);
        } else {
          setErrorMsg('No speech was recognized. Please try again and speak clearly.');
          setIsProcessing(false);
        }

        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
        setMediaStream(null);
        setIsRecording(false);
      };

      recognition.start();

      // 4. Auto-stop after 8 seconds to give enough time for a sentence
      setTimeout(() => {
        if (recognitionRef.current) {
          try { recognitionRef.current.stop(); } catch (e) {}
        }
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop();
        }
      }, 8000);

    } catch (err) {
      setErrorMsg('Microphone permission required for speech practice.');
      setIsRecording(false);
    }
  };

  // Determine status label based on overall score
  const getStatusLabel = (score) => {
    if (score >= 90) return { text: 'Excellent', color: 'text-emerald-400', dot: '🟢' };
    if (score >= 70) return { text: 'Good', color: 'text-amber-300', dot: '🟡' };
    if (score >= 50) return { text: 'Fair', color: 'text-orange-400', dot: '🟠' };
    return { text: 'Needs Practice', color: 'text-rose-400', dot: '🔴' };
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
        <div className="flex items-center gap-2">
          <button
            onClick={() => playNaturalSpeechAudio("అ ఆ ఇ ఈ ఉ ఊ", 0.85)}
            title="Test natural Telugu speech audio"
            className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
          >
            <Volume2 size={16} className="text-emerald-400" />
            <span>Test Telugu Voice</span>
          </button>

          <button
            onClick={() => playBenchmarkAudio(0.85)}
            className={`p-3 rounded-xl flex items-center gap-2 text-sm font-bold transition-all ${
              isPlayingAudio
                ? 'bg-emerald-500 text-white shadow-lg ring-4 ring-emerald-500/30 animate-pulse'
                : 'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30'
            }`}
          >
            <Volume2 size={18} className={isPlayingAudio ? 'animate-bounce' : ''} />
            <span>{isPlayingAudio ? 'Playing Audio...' : 'Listen'}</span>
          </button>
        </div>
      </div>

      {/* Target Word Highlight Card */}
      <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-700/80 text-center space-y-4 shadow-inner">
        <span className="text-xs text-slate-400">Target Practice Sentence:</span>
        <div className="flex flex-wrap items-center justify-center gap-3 text-2xl md:text-3xl font-bold tracking-wide">
          {targetText.split(' ').map((word, idx) => {
            const cleanWord = word.replace(/[.,!?;:'"]/g, '');
            const status = evaluation?.word_feedback?.[word] || evaluation?.word_feedback?.[cleanWord];
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

      {/* Live Recognized Text */}
      {(isRecording || recognizedText) && (
        <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-700/50">
          <span className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            {isRecording ? '🎙️ Listening...' : '📝 What you said:'}
          </span>
          <p className={`text-sm font-medium ${isRecording ? 'text-emerald-300 animate-pulse' : 'text-slate-300'}`}>
            {recognizedText || (isRecording ? 'Speak now...' : '')}
          </p>
        </div>
      )}

      {/* Error Message */}
      {errorMsg && (
        <div className="bg-rose-950/30 rounded-xl p-3 border border-rose-500/20">
          <p className="text-xs text-rose-300">⚠️ {errorMsg}</p>
        </div>
      )}

      {/* Recording Actions */}
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`flex-1 py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
            isProcessing
              ? 'bg-slate-700 text-slate-400 cursor-wait'
              : isRecording 
                ? 'bg-rose-600 hover:bg-rose-500 text-white mic-active' 
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-600/30'
          }`}
        >
          {isProcessing ? (
            <><Loader size={22} className="animate-spin" /><span>Analyzing your speech...</span></>
          ) : isRecording ? (
            <><MicOff size={22} /><span>Stop Recording</span></>
          ) : (
            <><Mic size={22} /><span>Tap Microphone & Speak Aloud</span></>
          )}
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
            <span className={`text-2xl font-black ${
              evaluation.overall_score >= 70 ? 'text-emerald-400' : 
              evaluation.overall_score >= 50 ? 'text-amber-400' : 'text-rose-400'
            }`}>{evaluation.overall_score}%</span>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center text-xs">
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block">Accuracy</span>
              <span className={`text-sm font-bold ${evaluation.phoneme_accuracy >= 70 ? 'text-emerald-300' : evaluation.phoneme_accuracy >= 50 ? 'text-amber-300' : 'text-rose-300'}`}>
                {evaluation.phoneme_accuracy}%
              </span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block">Syllables</span>
              <span className={`text-sm font-bold ${evaluation.syllable_score >= 70 ? 'text-emerald-300' : evaluation.syllable_score >= 50 ? 'text-amber-300' : 'text-rose-300'}`}>
                {evaluation.syllable_score}%
              </span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400 block">Status</span>
              {(() => {
                const status = getStatusLabel(evaluation.overall_score);
                return <span className={`text-sm font-bold ${status.color}`}>{status.dot} {status.text}</span>;
              })()}
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
