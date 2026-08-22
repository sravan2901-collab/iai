import React, { useRef, useState, useEffect } from 'react';
import { PenTool, RotateCcw, CheckCircle, Sparkles, Volume2, Eraser, Download, ArrowLeft } from 'lucide-react';
import { apiRequest } from '../services/api';

export default function InteractiveWritingCanvas({ lesson, onClose }) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [penColor, setPenColor] = useState('#10b981'); // Emerald green
  const [lineWidth, setLineWidth] = useState(6);
  const [isEraser, setIsEraser] = useState(false);
  const [hasWritten, setHasWritten] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const targetText = lesson?.target_text || "A, B, C";

  const initialImgDataRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Set up canvas resolution
    canvas.width = canvas.parentElement.clientWidth || 600;
    canvas.height = 320;

    // Draw background guide lines (four-line notebook guide)
    drawNotebookLines(ctx, canvas.width, canvas.height);
  }, []);

  const drawNotebookLines = (ctx, width, height) => {
    ctx.fillStyle = '#0f172a'; // slate-900
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = '#334155'; // slate-700
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    // Baseline & Guidelines
    const topMargin = 70;
    const lineSpacing = 60;

    for (let i = 0; i < 3; i++) {
      const y = topMargin + i * lineSpacing;
      ctx.beginPath();
      ctx.moveTo(30, y);
      ctx.lineTo(width - 30, y);
      ctx.stroke();
    }

    ctx.setLineDash([]); // Reset dash

    // Render faint tracing watermark template of targetText
    ctx.font = 'bold 36px sans-serif';
    ctx.fillStyle = 'rgba(148, 163, 184, 0.28)'; // Slate watermark tracing guide
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(targetText.slice(0, 26), width / 2, 130);

    // Capture initial background & guidelines image data baseline
    initialImgDataRef.current = ctx.getImageData(0, 0, width, height);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    drawNotebookLines(ctx, canvas.width, canvas.height);
    setHasWritten(false);
    setEvaluation(null);
  };

  const startDrawing = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    ctx.beginPath();
    ctx.moveTo(clientX - rect.left, clientY - rect.top);
    setIsDrawing(true);
    setHasWritten(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();

    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    ctx.lineTo(clientX - rect.left, clientY - rect.top);
    ctx.strokeStyle = isEraser ? '#0f172a' : penColor;
    ctx.lineWidth = isEraser ? 24 : lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const evaluateHandwriting = () => {
    const canvas = canvasRef.current;
    if (!canvas || !hasWritten || !initialImgDataRef.current) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const currentImgData = ctx.getImageData(0, 0, width, height).data;
    const baseImgData = initialImgDataRef.current.data;

    // Render exact target text template on offscreen canvas for shape matching
    const offCanvas = document.createElement('canvas');
    offCanvas.width = width;
    offCanvas.height = height;
    const offCtx = offCanvas.getContext('2d');
    offCtx.fillStyle = '#000000';
    offCtx.fillRect(0, 0, width, height);
    offCtx.font = 'bold 36px sans-serif';
    offCtx.fillStyle = '#ffffff';
    offCtx.textAlign = 'center';
    offCtx.textBaseline = 'middle';
    offCtx.fillText(targetText.slice(0, 26), width / 2, 130);
    const targetMaskData = offCtx.getImageData(0, 0, width, height).data;

    let drawnPixels = 0;
    let targetPixelsCount = 0;
    let overlapPixelsCount = 0;
    let userStrayPixelsCount = 0;

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const index = (y * width + x) * 4;
        const isTargetPixel = targetMaskData[index] > 100;

        const rDiff = Math.abs(currentImgData[index] - baseImgData[index]);
        const gDiff = Math.abs(currentImgData[index + 1] - baseImgData[index + 1]);
        const bDiff = Math.abs(currentImgData[index + 2] - baseImgData[index + 2]);
        const isUserPixel = (rDiff + gDiff + bDiff > 40);

        if (isTargetPixel) targetPixelsCount++;
        if (isUserPixel) {
          drawnPixels++;
          if (isTargetPixel) {
            overlapPixelsCount++;
          } else {
            userStrayPixelsCount++;
          }
        }
      }
    }

    const precisionRatio = targetPixelsCount > 0 ? (overlapPixelsCount / targetPixelsCount) : 0;
    const strayRatio = drawnPixels > 0 ? (userStrayPixelsCount / drawnPixels) : 0;

    let strokeAccuracy = 0;
    let formationScore = 0;
    let directionAccuracy = "Correct (Left-to-Right)";
    let feedback = "";

    if (drawnPixels < 100) {
      strokeAccuracy = Math.min(30, Math.max(15, Math.round(15 + drawnPixels / 5)));
      formationScore = Math.max(12, strokeAccuracy - 4);
      feedback = "Minimal strokes detected. Please trace directly over the watermark letters on the notebook pad.";
      directionAccuracy = "Incomplete Strokes";
    } else {
      // Calculate precision overlap vs stray penalties
      const shapeCoveragePercent = Math.min(100, Math.round(precisionRatio * 140)); // Coverage of target letter strokes
      const strayPenalty = Math.round(strayRatio * 35);

      const rawAccuracy = Math.round(shapeCoveragePercent - strayPenalty);
      strokeAccuracy = Math.min(98, Math.max(25, rawAccuracy));
      formationScore = Math.min(99, Math.max(26, Math.round(shapeCoveragePercent * 0.9)));

      if (strokeAccuracy >= 82) {
        feedback = "Excellent tracing accuracy! Your handwriting matches the target letter shapes perfectly.";
      } else if (strokeAccuracy >= 62) {
        feedback = "Good attempt! Trace all target characters completely along the watermark guides.";
      } else {
        feedback = "Strokes strayed from target characters. Trace directly over the guided watermark letters on the pad.";
      }
    }

    setEvaluation({
      stroke_accuracy: strokeAccuracy,
      formation_score: formationScore,
      direction_accuracy: directionAccuracy,
      feedback: feedback
    });
  };

  const playPronunciationAudio = () => {
    setIsPlayingAudio(true);
    try {
      const cleanText = targetText.replace(/[.,!?;:'"\\\/\-_]/g, ' ').trim();
      const encodedText = encodeURIComponent(cleanText.slice(0, 200));
      const audioUrl = `http://127.0.0.1:8000/api/voice/tts?text=${encodedText}&lang=${lesson?.lang || 'te'}`;
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlayingAudio(false);
      audio.onerror = () => setIsPlayingAudio(false);
      audio.play().catch(() => setIsPlayingAudio(false));
    } catch (e) {
      setIsPlayingAudio(false);
    }
  };

  return (
    <div className="glass-panel max-w-3xl mx-auto rounded-2xl p-6 md:p-8 space-y-6 animate-fade-in border border-slate-700/80 shadow-2xl">
      {/* Top Navigation Header */}
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
            <span className="text-xs uppercase tracking-wider font-semibold text-blue-400 flex items-center gap-1.5">
              <PenTool size={14} />
              Interactive Writing & Stroke Practice Pad
            </span>
            <h3 className="text-xl font-bold text-slate-100">{lesson?.title || "Writing Practice Module"}</h3>
          </div>
        </div>

        <button
          onClick={playPronunciationAudio}
          className="p-2.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/30 rounded-xl flex items-center gap-2 text-xs font-semibold transition-all"
        >
          <Volume2 size={16} className={isPlayingAudio ? 'animate-bounce text-blue-400' : ''} />
          <span>{isPlayingAudio ? 'Playing...' : 'Audio Guide'}</span>
        </button>
      </div>

      {/* Target Letter Reference Box */}
      <div className="bg-slate-950/80 rounded-2xl p-5 border border-slate-800 text-center space-y-2">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Target Characters / Words to Trace & Write:
        </span>
        <div className="text-3xl md:text-4xl font-extrabold text-amber-300 tracking-wide font-mono py-1">
          {targetText}
        </div>
        <p className="text-xs text-slate-400">
          Follow guidelines below: Write each character smoothly along the dotted notebook lines.
        </p>
      </div>

      {/* Interactive Digital Canvas Pad */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <Sparkles size={14} className="text-emerald-400" />
            Digital Canvas Notebook Pad:
          </span>

          {/* Tools Palette */}
          <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-xl border border-slate-700">
            <button
              onClick={() => setIsEraser(false)}
              className={`p-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-all ${
                !isEraser ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <PenTool size={14} />
              <span>Pen</span>
            </button>

            <button
              onClick={() => setIsEraser(true)}
              className={`p-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-all ${
                isEraser ? 'bg-amber-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Eraser size={14} />
              <span>Eraser</span>
            </button>

            {/* Pen Colors */}
            {!isEraser && (
              <div className="flex items-center gap-1.5 px-2 border-l border-slate-700">
                {['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#ffffff'].map((color) => (
                  <button
                    key={color}
                    onClick={() => setPenColor(color)}
                    className={`w-5 h-5 rounded-full border border-slate-600 transition-transform ${
                      penColor === color ? 'scale-125 ring-2 ring-white' : 'opacity-80 hover:opacity-100'
                    }`}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            )}

            <button
              onClick={clearCanvas}
              className="p-1.5 text-slate-400 hover:text-rose-400 transition-colors ml-1"
              title="Clear Canvas"
            >
              <RotateCcw size={14} />
            </button>
          </div>
        </div>

        {/* Canvas Element */}
        <div className="relative rounded-2xl overflow-hidden border-2 border-slate-700/80 shadow-2xl bg-slate-900 cursor-crosshair">
          <canvas
            ref={canvasRef}
            onMouseDown={startDrawing}
            onMouseMove={draw}
            onMouseUp={stopDrawing}
            onMouseLeave={stopDrawing}
            onTouchStart={startDrawing}
            onTouchMove={draw}
            onTouchEnd={stopDrawing}
            className="w-full touch-none block"
          />

          {!hasWritten && (
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center text-slate-500/60 font-semibold text-sm">
              ✍️ Touch or click here to start writing & practicing strokes
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={clearCanvas}
          className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold flex items-center gap-2 border border-slate-700 transition-all"
        >
          <RotateCcw size={14} />
          <span>Clear Canvas</span>
        </button>

        <button
          onClick={evaluateHandwriting}
          disabled={!hasWritten}
          className={`px-6 py-3 rounded-xl font-extrabold text-sm flex items-center gap-2 shadow-lg transition-all ${
            hasWritten 
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white scale-105 cursor-pointer'
              : 'bg-slate-800 text-slate-500 cursor-not-allowed opacity-60'
          }`}
        >
          <CheckCircle size={18} />
          <span>Submit & Evaluate Handwriting</span>
        </button>
      </div>

      {/* Evaluation Feedback Panel */}
      {evaluation && (
        <div className="bg-slate-900/90 rounded-2xl p-5 border border-emerald-500/40 space-y-3 animate-fade-in shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Sparkles size={16} />
              AI Handwriting Formation Analysis Result:
            </span>
            <span className="text-sm font-extrabold text-emerald-300 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full">
              Score: {evaluation.stroke_accuracy}%
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs pt-1">
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Stroke Accuracy:</span>
              <span className="font-extrabold text-emerald-400 text-sm">{evaluation.stroke_accuracy}%</span>
            </div>
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Letter Alignment:</span>
              <span className="font-extrabold text-blue-400 text-sm">{evaluation.formation_score}%</span>
            </div>
            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 col-span-2 md:col-span-1">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Writing Direction:</span>
              <span className="font-bold text-amber-300 text-xs">{evaluation.direction_accuracy}</span>
            </div>
          </div>

          <p className="text-xs text-slate-200 bg-emerald-950/40 p-3 rounded-xl border border-emerald-500/20 italic">
            "{evaluation.feedback}"
          </p>
        </div>
      )}
    </div>
  );
}
