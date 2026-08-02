import React, { useEffect, useRef } from 'react';

export default function AudioVisualizer({ isRecording, mediaStream }) {
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    if (!isRecording || !mediaStream) return;

    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(mediaStream);

    source.connect(analyser);
    analyser.fftSize = 64;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');

    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);

      analyser.getByteFrequencyData(dataArray);

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 1.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;

        const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, 0);
        gradient.addColorStop(0, '#10b981'); // Emerald green
        gradient.addColorStop(1, '#3b82f6'); // Electric blue

        canvasCtx.fillStyle = gradient;
        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);

        x += barWidth;
      }
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameRef.current);
      audioContext.close();
    };
  }, [isRecording, mediaStream]);

  if (!isRecording) return null;

  return (
    <div className="w-full flex flex-col items-center justify-center my-3">
      <canvas 
        ref={canvasRef} 
        width={300} 
        height={60} 
        className="w-full max-w-xs h-16 rounded-lg bg-slate-900/60 border border-emerald-500/30"
      />
      <span className="text-[11px] text-emerald-400/80 mt-1 animate-pulse font-medium">
        🎙️ Listening to your voice...
      </span>
    </div>
  );
}
