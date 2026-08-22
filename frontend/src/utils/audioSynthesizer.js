/**
 * Web Audio API Phoneme & Speech Synthesizer for AksharAI
 * Provides instant, offline-capable synthesized audio feedback for letters,
 * syllables, and words across native Indian languages (Telugu, Hindi, Tamil, etc.)
 */

// Phoneme frequency maps for Telugu and Indic vowels & consonants
const PHONEME_FREQ_MAP = {
  // Telugu Vowels
  'అ': { freq: 220, type: 'sine', duration: 0.4, label: 'A-short' },
  'ఆ': { freq: 240, type: 'sine', duration: 0.6, label: 'A-long' },
  'ఇ': { freq: 330, type: 'triangle', duration: 0.4, label: 'I-short' },
  'ఈ': { freq: 350, type: 'triangle', duration: 0.6, label: 'I-long' },
  'ఉ': { freq: 165, type: 'sine', duration: 0.4, label: 'U-short' },
  'ఊ': { freq: 175, type: 'sine', duration: 0.6, label: 'U-long' },
  'ఋ': { freq: 280, type: 'sawtooth', duration: 0.5, label: 'Ru' },
  'ఎ': { freq: 293, type: 'triangle', duration: 0.4, label: 'E-short' },
  'ఏ': { freq: 311, type: 'triangle', duration: 0.6, label: 'E-long' },
  'ఐ': { freq: 392, type: 'sawtooth', duration: 0.6, label: 'Ai' },
  'ఒ': { freq: 200, type: 'sine', duration: 0.4, label: 'O-short' },
  'ఓ': { freq: 215, type: 'sine', duration: 0.6, label: 'O-long' },
  'ఔ': { freq: 250, type: 'sawtooth', duration: 0.6, label: 'Au' },
  'అం': { freq: 230, type: 'sine', duration: 0.5, label: 'Am' },
  'అః': { freq: 245, type: 'sine', duration: 0.5, label: 'Aha' }
};

let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

/**
 * Synthesizes a pleasant vocal-like tone sequence for Indic letters & phrases
 */
export function playSynthesizedPhoneme(text, rate = 1.0) {
  const ctx = getAudioContext();
  if (!ctx) return false;

  const chars = Array.from(text.replace(/[\s,.!?;:'"\\\/\-_]/g, ''));
  if (chars.length === 0) return false;

  let startTime = ctx.currentTime + 0.05;

  chars.forEach((char, idx) => {
    const config = PHONEME_FREQ_MAP[char] || {
      freq: 200 + ((char.charCodeAt(0) * 7) % 300),
      type: 'triangle',
      duration: 0.35
    };

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = config.type || 'triangle';
    osc.frequency.setValueAtTime(config.freq, startTime);

    // Formant filter simulation for vocal warmth
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(config.freq * 1.5, startTime);
    filter.Q.setValueAtTime(3.0, startTime);

    // Envelope
    const duration = (config.duration || 0.4) / rate;
    gain.gain.setValueAtTime(0.001, startTime);
    gain.gain.exponentialRampToValueAtTime(0.3, startTime + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    osc.start(startTime);
    osc.stop(startTime + duration + 0.05);

    startTime += duration + (0.1 / rate);
  });

  return true;
}
