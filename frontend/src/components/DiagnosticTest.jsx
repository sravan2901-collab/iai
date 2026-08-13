import React, { useState, useEffect } from 'react';
import { Award, CheckCircle, Mic, ArrowRight, ArrowLeft, BookOpen, Edit3, Volume2, RefreshCw, AlertCircle, XCircle } from 'lucide-react';
import AudioVisualizer from './AudioVisualizer';
import { apiRequest } from '../services/api';

export default function DiagnosticTest({ onComplete, onSelectLesson, selectedLang = 'en' }) {
  const [questions, setQuestions] = useState([]);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  
  const [userAnswers, setUserAnswers] = useState({});
  const [writtenInput, setWrittenInput] = useState("");
  
  const [isRecording, setIsRecording] = useState(false);
  const [mediaStream, setMediaStream] = useState(null);
  const [transcribedText, setTranscribedText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const NATIVE_FALLBACKS = {
    en: [
      { id: 1, stage: 1, difficulty: 1, skill_type: "READ", question_title: "Question 1/9 [Level 1] — Phonetics", question_text: "Which word contains the long vowel sound /eɪ/ as in 'Fate'?", options: [{ id: "a", text: "Grace", is_correct: true }, { id: "b", text: "Track", is_correct: false }, { id: "c", text: "Bell", is_correct: false }, { id: "d", text: "Rock", is_correct: false }] },
      { id: 2, stage: 2, difficulty: 2, skill_type: "WRITE", question_title: "Question 2/9 [Level 2] — Spelling", question_text: "Type the correctly spelled word for a place where books are kept:", accepted_answers: ["Library", "library", "LIBRARY"] },
      { id: 3, stage: 3, difficulty: 3, skill_type: "SPEAK", question_title: "Question 3/9 [Level 3] — Pronunciation", question_text: "Press microphone and speak aloud the sentence below:", target_text: "Language unlocks knowledge, wisdom, and human expression" },
      { id: 4, stage: 4, difficulty: 4, skill_type: "READ", question_title: "Question 4/9 [Level 4] — Synonyms", question_text: "Select the exact synonym for the word 'PERSISTENT':", options: [{ id: "a", text: "Persevering", is_correct: true }, { id: "b", text: "Temporary", is_correct: false }, { id: "c", text: "Hesitant", is_correct: false }, { id: "d", text: "Careless", is_correct: false }] },
      { id: 5, stage: 5, difficulty: 5, skill_type: "WRITE", question_title: "Question 5/9 [Level 5] — Grammar", question_text: "Type the past perfect form of the verb 'Write':", accepted_answers: ["written", "Written", "WRITTEN"] },
      { id: 6, stage: 6, difficulty: 6, skill_type: "SPEAK", question_title: "Question 6/9 [Level 6] — Articulation", question_text: "Press microphone and speak aloud the compound complex sentence:", target_text: "Although the journey was challenging, continuous practice brought clarity and confidence" },
      { id: 7, stage: 7, difficulty: 7, skill_type: "READ", question_title: "Question 7/9 [Level 7] — Prose Reading", question_text: "Read passage: 'The profound silence of the evening was broken only by the gentle rustle of falling leaves.' What is the primary tone?", options: [{ id: "a", text: "Tranquil and Reflective", is_correct: true }, { id: "b", text: "Chaotic and Noisy", is_correct: false }, { id: "c", text: "Frightening", is_correct: false }, { id: "d", text: "Humorous", is_correct: false }] },
      { id: 8, stage: 8, difficulty: 8, skill_type: "WRITE", question_title: "Question 8/9 [Level 8] — Advanced Spelling", question_text: "Type the correct spelling for fluent and expressive speech:", accepted_answers: ["Eloquence", "eloquence", "ELOQUENCE"] },
      { id: 9, stage: 9, difficulty: 9, skill_type: "SPEAK", question_title: "Question 9/9 [Level 9] — High Fluency", question_text: "Press microphone and speak aloud the advanced literary passage:", target_text: "Mastery over language transforms thought into eloquent communication and lifelong empowerment" }
    ],
    te: [
      { id: 1, stage: 1, difficulty: 1, skill_type: "READ", question_title: "ప్రశ్న 1/9 [స్థాయి 1] — అక్షరం మరియు గుణింత గుర్తింపు (Question 1/9 [Level 1] — Phonetics)", question_text: "క్రింది వాటిలో 'కృ' (క + ఋ) గుణింత అక్షరం కలిగి ఉన్న పదాన్ని ఎంచుకోండి\nWhich word contains the 'కృ' (k + ru) letter sound?", options: [{ id: "a", text: "కృప", is_correct: true }, { id: "b", text: "కథ", is_correct: false }, { id: "c", text: "కలము", is_correct: false }, { id: "d", text: "కడవ", is_correct: false }] },
      { id: 2, stage: 2, difficulty: 2, skill_type: "WRITE", question_title: "ప్రశ్న 2/9 [స్థాయి 2] — అక్షర దోష నివారణ మరియు రాయడం (Question 2/9 [Level 2] — Spelling)", question_text: "జ్ఞానానికి మరియు పుస్తకాలకు నిలయమైన ప్రదేశాన్ని తెలిపే పదాన్ని రాయండి\nType the correct word for library:", accepted_answers: ["గ్రంథాలయము", "గ్రంథాలయం", "పుస్తకాలయం"] },
      { id: 3, stage: 3, difficulty: 3, skill_type: "SPEAK", question_title: "ప్రశ్న 3/9 [స్థాయి 3] — భాషా ఉచ్చారణ వాక్యం (Question 3/9 [Level 3] — Speech)", question_text: "మైక్రోఫోన్ నొక్కి క్రింది భాషా వాక్యాన్ని స్పష్టంగా చదవండి\nPress microphone and speak aloud the sentence below:", target_text: "భాష అనేది ఆలోచనలకు రూపాన్ని ఇచ్చే అమూల్యమైన సాధనం" },
      { id: 4, stage: 4, difficulty: 4, skill_type: "READ", question_title: "ప్రశ్న 4/9 [స్థాయి 4] — పర్యాయపదాలు మరియు పదజాలం (Question 4/9 [Level 4] — Synonyms)", question_text: "'అమృతం' అనే పదానికి సరైన పర్యాయపదాన్ని ఎంచుకోండి\nSelect the exact synonym for 'Amrutam':", options: [{ id: "a", text: "సుధ", is_correct: true }, { id: "b", text: "గరళం", is_correct: false }, { id: "c", text: "అనలం", is_correct: false }, { id: "d", text: "పవనం", is_correct: false }] },
      { id: 5, stage: 5, difficulty: 5, skill_type: "WRITE", question_title: "ప్రశ్న 5/9 [స్థాయి 5] — సంధి మరియు వ్యాకరణ రాయడం (Question 5/9 [Level 5] — Grammar)", question_text: "'దేవ + ఆలయం' కలిపి రాస్తే వచ్చే సరైన పదాన్ని టైప్ చేయండి\nType the combined Sandhi word for 'Deva + Alayam':", accepted_answers: ["దేవాలయం", "దేవాలయము"] },
      { id: 6, stage: 6, difficulty: 6, skill_type: "SPEAK", question_title: "ప్రశ్న 6/9 [స్థాయి 6] — సంక్లిష్ట వాక్య ఉచ్చారణ (Question 6/9 [Level 6] — Articulation)", question_text: "మైక్రోఫోన్ నొక్కి క్రింది సంక్లిష్ట వాక్యాన్ని బిగ్గరగా చదవండి\nPress microphone and speak aloud complex sentence:", target_text: "నిరంతర సాధన మరియు అధ్యయనం ద్వారా మాత్రమే భాషా ప్రావీణ్యం లభిస్తుంది" },
      { id: 7, stage: 7, difficulty: 7, skill_type: "READ", question_title: "ప్రశ్న 7/9 [స్థాయి 7] — సాహిత్య గద్య పఠనావగాహన (Question 7/9 [Level 7] — Prose Reading)", question_text: "వాక్యం: 'ప్రశాంతమైన సాయంత్ర వేళ పక్షుల కలకూజనాలు మనస్సుకు ఆహ్లాదాన్ని కలిగిస్తాయి.' దీని భావం ఏమిటి?\nWhat is the primary tone of the passage?", options: [{ id: "a", text: "ప్రశాంతత మరియు సంతోషం", is_correct: true }, { id: "b", text: "భయం మరియు ఆందోళన", is_correct: false }, { id: "c", text: "కోపం", is_correct: false }, { id: "d", text: "అల్లరి", is_correct: false }] },
      { id: 8, stage: 8, difficulty: 8, skill_type: "WRITE", question_title: "ప్రశ్న 8/9 [స్థాయి 8] — ప్రౌఢ సాహిత్య పద నిర్మాణం (Question 8/9 [Level 8] — Advanced Spelling)", question_text: "మిక్కిలి పాండిత్యం కలవాడిని తెలిపే పదాన్ని సరైన అక్షరాలతో రాయండి\nType the correct word for scholar:", accepted_answers: ["విద్వాంసుడు", "విద్వాంసురాలు"] },
      { id: 9, stage: 9, difficulty: 9, skill_type: "SPEAK", question_title: "ప్రశ్న 9/9 [స్థాయి 9] — ప్రౌఢ సాహిత్య భాషా ప్రవాహం (Question 9/9 [Level 9] — High Fluency)", question_text: "మైక్రోఫోన్ నొక్కి క్రింది ఉన్నత సాహిత్య వాక్యాన్ని అనర్గళంగా చదవండి\nPress microphone and speak aloud advanced literary passage:", target_text: "సాహిత్యానుశీలనం మానవ చైతన్యానికి మరియు వ్యక్తిత్వ వికాసానికి అక్షయమైన నిధి" }
    ]
  };

  useEffect(() => {
    const fetchQuestions = async () => {
      setLoadingQuestions(true);
      try {
        const data = await apiRequest(`/assessment/diagnostic-questions?lang=${selectedLang}`);
        if (data && data.length === 9) {
          setQuestions(data);
        } else {
          setQuestions(NATIVE_FALLBACKS[selectedLang] || NATIVE_FALLBACKS['en']);
        }
      } catch (err) {
        setQuestions(NATIVE_FALLBACKS[selectedLang] || NATIVE_FALLBACKS['en']);
      } finally {
        setLoadingQuestions(false);
      }
    };

    fetchQuestions();
  }, [selectedLang]);

  const currentQ = questions[currentIdx];

  // Option selection for READ questions
  const handleSelectOption = (opt) => {
    const isCorrect = Boolean(opt.is_correct);
    setUserAnswers(prev => ({
      ...prev,
      [currentIdx]: {
        stage: currentQ.stage || (currentIdx + 1),
        skill_type: currentQ.skill_type,
        selected_option_id: opt.id,
        is_correct: isCorrect
      }
    }));
  };

  // Text input for WRITE questions (STRICT MATCH AGAINST ACCEPTED ANSWERS)
  const handleWriteInputChange = (val) => {
    setWrittenInput(val);
    const acceptedList = currentQ?.accepted_answers || [];
    const cleanVal = val.trim().toLowerCase();
    
    // Strict evaluation: must match one of accepted_answers exactly (case-insensitive)
    const isOk = cleanVal.length > 0 && acceptedList.some(ans => ans.trim().toLowerCase() === cleanVal);
    
    setUserAnswers(prev => ({
      ...prev,
      [currentIdx]: {
        stage: currentQ.stage || (currentIdx + 1),
        skill_type: currentQ.skill_type,
        written_text: val,
        is_correct: isOk
      }
    }));
  };

  // Voice recording & evaluation for SPEAK questions
  const startVoiceRecording = async () => {
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = selectedLang === 'te' ? 'te-IN' : (selectedLang === 'hi' ? 'hi-IN' : (selectedLang === 'ta' ? 'ta-IN' : 'en-US'));
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        setIsRecording(true);
        recognition.start();

        recognition.onresult = (event) => {
          const speechResult = event.results[0][0].transcript;
          setTranscribedText(speechResult);
          setIsRecording(false);

          const target = (currentQ?.target_text || "").trim().toLowerCase();
          const cleanSpeech = speechResult.trim().toLowerCase();
          
          // Verify speech match
          const targetWords = target.split(' ').filter(w => w.length > 1);
          const speechWords = cleanSpeech.split(' ').filter(w => w.length > 1);
          const matches = speechWords.filter(sw => targetWords.some(tw => tw.includes(sw) || sw.includes(tw)));
          const isMatch = (targetWords.length > 0 && (matches.length / targetWords.length) >= 0.5) || (cleanSpeech === target);

          setUserAnswers(prev => ({
            ...prev,
            [currentIdx]: {
              stage: currentQ.stage || (currentIdx + 1),
              skill_type: currentQ.skill_type,
              spoken_text: speechResult,
              is_correct: isMatch
            }
          }));
        };

        recognition.onerror = () => {
          setIsRecording(false);
        };
        recognition.onend = () => {
          setIsRecording(false);
        };
      } else {
        // Microphone recording fallback
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true }).catch(() => null);
        setMediaStream(stream);
        setIsRecording(true);

        setTimeout(() => {
          setIsRecording(false);
          if (stream) stream.getTracks().forEach(track => track.stop());
        }, 2500);
      }
    } catch (err) {
      setIsRecording(false);
      alert("Microphone permission is required for voice assessment questions.");
    }
  };

  // Text input handler for speech verification fallback
  const handleSpokenTextChange = (val) => {
    setTranscribedText(val);
    const target = (currentQ?.target_text || "").trim().toLowerCase();
    const cleanSpeech = val.trim().toLowerCase();
    
    const targetWords = target.split(' ').filter(w => w.length > 1);
    const speechWords = cleanSpeech.split(' ').filter(w => w.length > 1);
    const matches = speechWords.filter(sw => targetWords.some(tw => tw.includes(sw) || sw.includes(tw)));
    const isMatch = cleanSpeech.length > 0 && ((targetWords.length > 0 && (matches.length / targetWords.length) >= 0.5) || (cleanSpeech === target));

    setUserAnswers(prev => ({
      ...prev,
      [currentIdx]: {
        stage: currentQ.stage || (currentIdx + 1),
        skill_type: currentQ.skill_type,
        spoken_text: val,
        is_correct: isMatch
      }
    }));
  };

  const syncCurrentInputToAnswers = () => {
    if (!currentQ) return;
    if (currentQ.skill_type === 'WRITE') {
      const acceptedList = currentQ?.accepted_answers || [];
      const cleanVal = writtenInput.trim().toLowerCase();
      const isOk = cleanVal.length > 0 && acceptedList.some(ans => ans.trim().toLowerCase() === cleanVal);
      setUserAnswers(prev => ({
        ...prev,
        [currentIdx]: {
          stage: currentQ.stage || (currentIdx + 1),
          skill_type: currentQ.skill_type,
          written_text: writtenInput,
          is_correct: isOk
        }
      }));
    } else if (currentQ.skill_type === 'SPEAK') {
      const target = (currentQ?.target_text || "").trim().toLowerCase();
      const cleanSpeech = transcribedText.trim().toLowerCase();
      const targetWords = target.split(' ').filter(w => w.length > 1);
      const speechWords = cleanSpeech.split(' ').filter(w => w.length > 1);
      const matches = speechWords.filter(sw => targetWords.some(tw => tw.includes(sw) || sw.includes(tw)));
      const isMatch = cleanSpeech.length > 0 && ((targetWords.length > 0 && (matches.length / targetWords.length) >= 0.5) || (cleanSpeech === target));

      setUserAnswers(prev => ({
        ...prev,
        [currentIdx]: {
          stage: currentQ.stage || (currentIdx + 1),
          skill_type: currentQ.skill_type,
          spoken_text: transcribedText,
          is_correct: isMatch
        }
      }));
    }
  };

  const handleNextQuestion = () => {
    syncCurrentInputToAnswers();
    if (currentIdx < questions.length - 1) {
      const nextIdx = currentIdx + 1;
      setCurrentIdx(nextIdx);
      const prevNextAns = userAnswers[nextIdx] || {};
      setWrittenInput(prevNextAns.written_text || "");
      setTranscribedText(prevNextAns.spoken_text || "");
    } else {
      handleFinishAssessment();
    }
  };

  const handlePrevQuestion = () => {
    syncCurrentInputToAnswers();
    if (currentIdx > 0) {
      const prevIdx = currentIdx - 1;
      setCurrentIdx(prevIdx);
      const prevAns = userAnswers[prevIdx] || {};
      setWrittenInput(prevAns.written_text || "");
      setTranscribedText(prevAns.spoken_text || "");
    }
  };

  const handleFinishAssessment = async () => {
    setIsSubmitting(true);
    syncCurrentInputToAnswers();
    
    const formattedAnswers = questions.map((q, idx) => {
      const ans = userAnswers[idx] || {};
      return {
        stage: q.stage || q.id || (idx + 1),
        question_id: q.id || q.stage || (idx + 1),
        skill_type: q.skill_type,
        selected_option_id: ans.selected_option_id || null,
        written_text: ans.written_text || null,
        spoken_text: ans.spoken_text || null,
        is_correct: Boolean(ans.is_correct)
      };
    });

    const payload = {
      lang: selectedLang,
      answers: formattedAnswers
    };

    let resultData = null;

    try {
      resultData = await apiRequest('/assessment/submit', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    } catch (err) {
      const correctCount = formattedAnswers.filter(a => a.is_correct).length;
      const totalScore = Math.min(100, Math.round((correctCount / questions.length) * 100));
      let level = "FOUNDATIONAL";
      
      if (totalScore >= 75) level = "PROFICIENT";
      else if (totalScore >= 45) level = "FUNCTIONAL";

      resultData = {
        status: "success",
        total_score: totalScore,
        correct_answers: correctCount,
        total_questions: questions.length,
        proficiency_level: level,
        learning_path: {
          path_title: `Language Literacy Mastery Roadmap — Track: ${level}`,
          current_level: level,
          completion_percentage: totalScore >= 75 ? 85 : (totalScore >= 45 ? 50 : 15)
        }
      };
    } finally {
      setIsSubmitting(false);
      if (resultData && onComplete) {
        onComplete(resultData);
      }
    }
  };

  if (loadingQuestions || !questions || questions.length === 0) {
    return (
      <div className="glass-panel max-w-2xl mx-auto rounded-2xl p-8 text-center my-6 space-y-4">
        <RefreshCw className="animate-spin text-emerald-400 mx-auto" size={32} />
        <p className="text-slate-300 font-medium">Loading 9 bilingual placement questions (Difficulty 1 to 9)...</p>
      </div>
    );
  }

  const currentAnswerState = userAnswers[currentIdx] || {};
  const answeredCurrent = currentQ.skill_type === 'READ' 
    ? Boolean(currentAnswerState.selected_option_id)
    : currentQ.skill_type === 'WRITE'
    ? writtenInput.trim().length > 0
    : transcribedText.trim().length > 0 || Boolean(currentAnswerState.spoken_text);

  // Format question text lines (Native Language on Line 1, English on Line 2)
  const textLines = (currentQ?.question_text || "").split("\n");
  const nativeLine = textLines[0] || currentQ?.question_text;
  const englishLine = textLines[1] || "";

  return (
    <div className="glass-panel max-w-2xl mx-auto rounded-2xl p-6 md:p-8 text-center my-6 space-y-6">
      
      {/* Header & Difficulty Bar */}
      <div className="space-y-3 pb-4 border-b border-slate-700/60">
        <div className="flex items-center justify-between">
          <div className="text-left space-y-1">
            <h2 className="text-xl font-bold flex items-center gap-2 text-emerald-400">
              <Award className="text-amber-400" />
              Bilingual Placement Test ({selectedLang.toUpperCase()})
            </h2>
            <p className="text-xs text-slate-300">Questions are displayed in Native Language + English. Only native language answers are accepted.</p>
          </div>
          <span className="text-xs px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full font-semibold border border-emerald-500/30">
            Q {currentIdx + 1} of {questions.length}
          </span>
        </div>

        {/* 9-Step Difficulty Indicator Bar */}
        <div className="grid grid-cols-9 gap-1.5 pt-1">
          {questions.map((q, idx) => {
            const hasAns = userAnswers[idx];
            const isCompleted = Boolean(hasAns) || idx < currentIdx;
            return (
              <div
                key={idx}
                className={`h-2.5 rounded-full transition-all ${
                  idx === currentIdx
                    ? 'bg-amber-400 ring-2 ring-amber-400/50 shadow-md shadow-amber-400/30'
                    : isCompleted
                    ? 'bg-emerald-500'
                    : 'bg-slate-700/80'
                }`}
                title={`Question ${idx + 1}: Difficulty Level ${q.difficulty || idx + 1}`}
              />
            );
          })}
        </div>
      </div>

      {/* Question Skill & Title */}
      <div className="text-left space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider flex items-center gap-1.5">
            {currentQ.skill_type === 'READ' && <BookOpen size={16} />}
            {currentQ.skill_type === 'WRITE' && <Edit3 size={16} />}
            {currentQ.skill_type === 'SPEAK' && <Volume2 size={16} />}
            {currentQ.question_title}
          </span>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
            Difficulty {currentQ.difficulty || (currentIdx + 1)}/9
          </span>
        </div>

        {/* Explicit Bilingual Line Formatting */}
        <div className="space-y-1 bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
          <p className="text-base md:text-lg text-emerald-300 font-bold leading-relaxed">
            {nativeLine}
          </p>
          {englishLine && (
            <p className="text-xs md:text-sm text-slate-300 font-medium italic border-t border-slate-700/40 pt-1.5 mt-1">
              {englishLine}
            </p>
          )}
        </div>
      </div>

      {/* QUESTION SKILL TYPE 1: READ (Multiple Choice) */}
      {currentQ.skill_type === 'READ' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
          {currentQ.options?.map(opt => {
            const isSelected = currentAnswerState.selected_option_id === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => handleSelectOption(opt)}
                className={`p-4 rounded-xl border text-left font-medium transition-all ${
                  isSelected 
                    ? 'border-emerald-500 bg-emerald-500/20 text-white shadow-md shadow-emerald-500/20 ring-2 ring-emerald-500/50' 
                    : 'border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-slate-200'
                }`}
              >
                <span className="text-slate-400 mr-2 font-mono">{opt.id.toUpperCase()}.</span>
                <span className="font-bold text-lg text-emerald-300">{opt.text}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* QUESTION SKILL TYPE 2: WRITE (Text Input) */}
      {currentQ.skill_type === 'WRITE' && (
        <div className="space-y-3 text-left">
          <label className="text-xs text-slate-300 block font-semibold">Type Answer in Native Language Script ONLY:</label>
          <input
            type="text"
            value={writtenInput}
            onChange={(e) => handleWriteInputChange(e.target.value)}
            placeholder="Type native language answer here..."
            className="w-full bg-slate-900/90 border border-slate-700 focus:border-emerald-500 rounded-xl p-4 text-emerald-300 font-bold text-lg focus:outline-none shadow-inner"
          />
        </div>
      )}

      {/* QUESTION SKILL TYPE 3: SPEAK (Voice Assessment) */}
      {currentQ.skill_type === 'SPEAK' && (
        <div className="space-y-4 text-left">
          <div className="bg-slate-900/80 p-5 rounded-xl border border-slate-700 text-center">
            <span className="text-2xl font-bold text-amber-300">
              "{currentQ.target_text}"
            </span>
          </div>

          <AudioVisualizer isRecording={isRecording} mediaStream={mediaStream} />

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
            <span>{isRecording ? "Listening to your voice..." : "Turn On Microphone & Speak Aloud Native Phrase"}</span>
          </button>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs text-slate-300 block font-medium">Extracted Speech Transcript (Voice Only):</label>
              <span className="text-[10px] text-amber-400 font-semibold px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                🔒 Manual Typing Prohibited
              </span>
            </div>
            <input
              type="text"
              value={transcribedText}
              readOnly={true}
              placeholder="Live speech transcript will automatically appear here when you speak into the microphone..."
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl p-3 text-emerald-300 font-semibold text-sm focus:outline-none cursor-not-allowed select-none shadow-inner"
            />
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-700/60 gap-4">
        <button
          onClick={handlePrevQuestion}
          disabled={currentIdx === 0}
          className="px-4 py-3 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-300 font-semibold text-xs disabled:opacity-30 flex items-center gap-1.5"
        >
          <ArrowLeft size={16} />
          <span>Previous</span>
        </button>

        <button
          onClick={handleNextQuestion}
          disabled={!answeredCurrent}
          className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm shadow-lg shadow-emerald-600/30 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {isSubmitting ? (
            <span className="flex items-center gap-2">
              <RefreshCw className="animate-spin" size={18} />
              Calculating 9-Level Proficiency Score...
            </span>
          ) : currentIdx === questions.length - 1 ? (
            <>
              <span>Submit & View Placement Results</span>
              <CheckCircle size={18} />
            </>
          ) : (
            <>
              <span>Next Question (Difficulty {currentQ.difficulty + 1 || currentIdx + 2}/9)</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
