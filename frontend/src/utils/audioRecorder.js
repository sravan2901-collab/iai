/**
 * Audio Recording & WAV Encoding Utility for AksharAI.
 * 
 * Captures clean 16kHz mono 16-bit PCM audio directly from the user's microphone
 * and encodes it into standard RIFF/WAVE (audio/wav) format compatible with
 * Sarvam Saaras v3 STT, Google SpeechRecognition, and cloud APIs.
 */

export class PcmWavRecorder {
  constructor(sampleRate = 16000) {
    this.targetSampleRate = sampleRate;
    this.audioContext = null;
    this.mediaStream = null;
    this.sourceNode = null;
    this.processorNode = null;
    this.pcmChunks = [];
    this.isRecording = false;
  }

  async start() {
    this.pcmChunks = [];
    this.isRecording = true;

    // Request microphone access
    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: this.targetSampleRate,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    this.audioContext = new AudioContextClass({ sampleRate: this.targetSampleRate });
    this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);

    // Buffer size 4096 gives smooth audio capture without dropouts
    const bufferSize = 4096;
    this.processorNode = this.audioContext.createScriptProcessor(bufferSize, 1, 1);

    this.processorNode.onaudioprocess = (e) => {
      if (!this.isRecording) return;
      const inputBuffer = e.inputBuffer.getChannelData(0);
      // Clone the Float32Array channel slice
      this.pcmChunks.push(new Float32Array(inputBuffer));
    };

    this.sourceNode.connect(this.processorNode);
    this.processorNode.connect(this.audioContext.destination);

    return this.mediaStream;
  }

  async stop() {
    this.isRecording = false;

    // Disconnect audio processing nodes
    if (this.processorNode) {
      this.processorNode.disconnect();
      this.processorNode.onaudioprocess = null;
    }
    if (this.sourceNode) {
      this.sourceNode.disconnect();
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      try {
        await this.audioContext.close();
      } catch (e) {}
    }

    // Stop media stream tracks
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
    }

    // Flatten all captured PCM chunks into one single Float32Array
    let totalSamples = 0;
    for (const chunk of this.pcmChunks) {
      totalSamples += chunk.length;
    }

    const mergedSamples = new Float32Array(totalSamples);
    let offset = 0;
    for (const chunk of this.pcmChunks) {
      mergedSamples.set(chunk, offset);
      offset += chunk.length;
    }

    // Encode to standard 16-bit Mono 16kHz WAV Blob
    return this.encodeWAV(mergedSamples, this.targetSampleRate);
  }

  encodeWAV(samples, sampleRate) {
    const numChannels = 1;
    const bytesPerSample = 2; // 16-bit PCM
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = samples.length * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);

    // 1. RIFF chunk descriptor
    this.writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    this.writeString(view, 8, 'WAVE');

    // 2. fmt sub-chunk
    this.writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);          // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true);           // AudioFormat (1 = PCM)
    view.setUint16(22, numChannels, true); // NumChannels (1 = Mono)
    view.setUint32(24, sampleRate, true);  // SampleRate (16000 Hz)
    view.setUint32(28, byteRate, true);    // ByteRate
    view.setUint16(32, blockAlign, true);  // BlockAlign
    view.setUint16(34, 16, true);          // BitsPerSample (16-bit)

    // 3. data sub-chunk
    this.writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    // Write 16-bit PCM samples
    let writeOffset = 44;
    for (let i = 0; i < samples.length; i++, writeOffset += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(writeOffset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }

    return new Blob([view], { type: 'audio/wav' });
  }

  writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }
}
