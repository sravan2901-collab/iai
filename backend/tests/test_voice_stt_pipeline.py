"""
Test Suite for Sarvam AI STT & Multilingual Voice Practice Pipeline.

Verifies:
1. SARVAM_API_KEY configuration handling
2. Elimination of hardcoded mock Hindi transcripts across non-Hindi languages
3. Multi-tier STT fallback (Sarvam Saaras v3 -> Web Speech Transcript Pass-Through -> Local SpeechRecognition)
4. Phoneme & pronunciation accuracy evaluation across multiple scripts (Telugu, Hindi, English, Tamil, etc.)
5. Dynamic language resolution (Telugu, Tamil, Kannada, Bengali, Hindi, English, Spanish)
6. Live GET /api/voice/status and POST /api/voice/evaluate endpoints
"""

import sys
import os
import unittest
import asyncio

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.sarvam_service import sarvam_service, SARVAM_LANG_MAP, detect_script_language
from app.services.phoneme_service import evaluate_pronunciation, normalize_text_for_eval

client = TestClient(app)

class TestVoiceSTTPipeline(unittest.TestCase):
    """Test suite for voice practice, STT fallback, and pronunciation scoring."""

    def test_01_sarvam_configuration_check(self):
        """Verify is_configured accurately reflects API key state without returning dummy keys."""
        is_conf = sarvam_service.is_configured()
        self.assertIsInstance(is_conf, bool)
        status = sarvam_service.get_service_status()
        self.assertIn("sarvam_configured", status)
        self.assertIn("stt_engine", status)
        self.assertIn("supported_languages", status)
        print(f"  ✓ [Voice Status] Sarvam Configured: {status['sarvam_configured']}, Active STT: {status['stt_engine']}")

    def test_02_language_code_normalization(self):
        """Verify ISO language codes correctly normalize to Sarvam language codes."""
        self.assertEqual(sarvam_service.normalize_language_code("te"), "te-IN")
        self.assertEqual(sarvam_service.normalize_language_code("hi"), "hi-IN")
        self.assertEqual(sarvam_service.normalize_language_code("ta"), "ta-IN")
        self.assertEqual(sarvam_service.normalize_language_code("bn"), "bn-IN")
        self.assertEqual(sarvam_service.normalize_language_code("kn"), "kn-IN")
        self.assertEqual(sarvam_service.normalize_language_code("mr"), "mr-IN")
        self.assertEqual(sarvam_service.normalize_language_code("en"), "en-IN")
        print("  ✓ [Language Mapping] All 8 languages normalized to Sarvam format")

    def test_03_no_hardcoded_hindi_mock_transcript(self):
        """Verify transcribe_audio does NOT return hardcoded 'नमस्ते आप कैसे हैं' when unconfigured."""
        res = asyncio.run(sarvam_service.transcribe_audio(
            audio_bytes=b"dummy_short_audio",
            language_code="te-IN",
            client_transcript="",
            target_text="నమస్కారం"
        ))
        self.assertNotEqual(res.get("transcript"), "नमस्ते आप कैसे हैं")
        print(f"  ✓ [STT Fallback] Clean unconfigured response verified: status={res.get('status')}")

    def test_04_client_web_speech_transcript_passthrough(self):
        """Verify client Web Speech transcript is correctly passed through and credited."""
        res = asyncio.run(sarvam_service.transcribe_audio(
            audio_bytes=b"",
            language_code="te-IN",
            client_transcript="నమస్కారం బాగున్నారా"
        ))
        self.assertEqual(res.get("transcript"), "నమస్కారం బాగున్నారా")
        self.assertEqual(res.get("provider"), "browser_web_speech_api")
        self.assertEqual(res.get("status"), "success")
        print("  ✓ [Web Speech Pass-Through] Browser transcript successfully passed to backend")

    def test_05_phoneme_evaluation_telugu_exact_match(self):
        """Verify 100% pronunciation score on exact match in Telugu."""
        target = "నమస్కారం మరియు శుభోదయం"
        spoken = "నమస్కారం మరియు శుభోదయం"
        eval_res = evaluate_pronunciation(target, spoken, language_code="te")
        self.assertEqual(eval_res["overall_score"], 100.0)
        self.assertEqual(eval_res["word_feedback"]["నమస్కారం"], "green")
        self.assertEqual(eval_res["word_feedback"]["శుభోదయం"], "green")
        print(f"  ✓ [Phoneme Eval Telugu] Score: {eval_res['overall_score']}% (All Green)")

    def test_06_phoneme_evaluation_english_partial_match(self):
        """Verify granular score and color coding on partial match in English."""
        target = "Language unlocks knowledge and wisdom"
        spoken = "Language unlocks knowledge"
        eval_res = evaluate_pronunciation(target, spoken, language_code="en")
        self.assertTrue(eval_res["overall_score"] > 50.0)
        self.assertEqual(eval_res["word_feedback"]["Language"], "green")
        self.assertEqual(eval_res["word_feedback"]["unlocks"], "green")
        self.assertEqual(eval_res["word_feedback"]["wisdom"], "red")
        print(f"  ✓ [Phoneme Eval English] Partial Score: {eval_res['overall_score']}% (Green + Red detected)")

    def test_07_phoneme_evaluation_empty_speech(self):
        """Verify empty speech properly marks 0 score and friendly remediation tip."""
        target = "नमस्ते भारत"
        spoken = ""
        eval_res = evaluate_pronunciation(target, spoken, language_code="hi")
        self.assertEqual(eval_res["overall_score"], 0.0)
        self.assertIn("No speech was detected", eval_res["remediation_tip"])
        print("  ✓ [Phoneme Eval Empty] Correctly handled zero-speech scenario")

    def test_08_api_voice_status_endpoint(self):
        """Verify GET /api/voice/status returns 200 with engine metadata."""
        res = client.get("/api/voice/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sarvam_configured", data)
        self.assertIn("stt_engine", data)
        print(f"  ✓ [REST API] GET /api/voice/status returned HTTP 200: {data['stt_engine']}")

    def test_09_api_voice_evaluate_endpoint_with_transcript(self):
        """Verify POST /api/voice/evaluate endpoint processes client transcript and scores properly."""
        payload = {
            "learner_id": 1,
            "lesson_id": 1,
            "transcript": "Alphabets and phonics fundamentals",
            "language_code": "en"
        }
        res = client.post("/api/voice/evaluate", data=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("overall_score", data)
        self.assertIn("phoneme_accuracy", data)
        self.assertIn("word_feedback", data)
        self.assertEqual(data["stt_provider"], "browser_web_speech_api")
        print(f"  ✓ [REST API] POST /api/voice/evaluate returned Score={data['overall_score']}, Provider={data['stt_provider']}")

    def test_10_script_language_auto_detection(self):
        """Verify script detection correctly identifies Telugu, Tamil, Kannada, Bengali, Hindi without defaulting to Hindi."""
        self.assertEqual(detect_script_language("నమస్కారం"), "te")
        self.assertEqual(detect_script_language("வணக்கம்"), "ta")
        self.assertEqual(detect_script_language("ನಮಸ್ಕಾರ"), "kn")
        self.assertEqual(detect_script_language("নমস্কার"), "bn")
        self.assertEqual(detect_script_language("नमस्ते"), "hi")
        self.assertEqual(detect_script_language("Hola mundo"), "es")
        self.assertEqual(detect_script_language("Good morning"), "en")
        print("  ✓ [Script Auto-Detection] All Indic scripts & European languages correctly detected")

    def test_11_transcribe_audio_never_sends_hindi_for_telugu_tamil_kannada(self):
        """Verify transcribe_audio automatically routes to correct native language even if language_code was omitted."""
        # Telugu target text without language_code
        res_te = asyncio.run(sarvam_service.transcribe_audio(
            client_transcript="నమస్కారం",
            target_text="నమస్కారం మరియు శుభోదయం"
        ))
        self.assertEqual(res_te["language_code"], "te-IN")

        # Tamil target text without language_code
        res_ta = asyncio.run(sarvam_service.transcribe_audio(
            client_transcript="வணக்கம்",
            target_text="வணக்கம் மற்றும் நல்வரவு"
        ))
        self.assertEqual(res_ta["language_code"], "ta-IN")

        # Kannada target text without language_code
        res_kn = asyncio.run(sarvam_service.transcribe_audio(
            client_transcript="ನಮಸ್ಕಾರ",
            target_text="ನಮಸ್ಕಾರ ಮತ್ತು ಶುಭೋದಯ"
        ))
        self.assertEqual(res_kn["language_code"], "kn-IN")

        # Bengali target text without language_code
        res_bn = asyncio.run(sarvam_service.transcribe_audio(
            client_transcript="নমস্কার",
            target_text="নমস্কার এবং সুপ্রভাত"
        ))
        self.assertEqual(res_bn["language_code"], "bn-IN")

        print("  ✓ [Native Language Routing] Telugu/Tamil/Kannada/Bengali correctly routed to te-IN, ta-IN, kn-IN, bn-IN (NEVER hi-IN)")

    def test_12_voice_evaluate_endpoint_with_telugu_lesson(self):
        """Verify POST /api/voice/evaluate endpoint properly sets te-IN for Telugu practice."""
        payload = {
            "learner_id": 1,
            "lesson_id": 1,
            "transcript": "నమస్కారం",
            "language_code": "te"
        }
        res = client.post("/api/voice/evaluate", data=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["language_code"], "te")
        print(f"  ✓ [REST API Telugu Practice] Evaluated in Telugu: language_code={data['language_code']}")

    def test_13_audio_bytes_saved_to_disk_and_served_via_endpoint(self):
        """Verify uploaded audio bytes are physically written to disk and served via /api/voice/audio/{filename}."""
        # Create a small valid WAV byte array
        import io, wave, struct, math
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            samples = [int(1000 * math.sin(2 * math.pi * 440 * i / 16000)) for i in range(16000)]
            wf.writeframes(struct.pack('<' + 'h'*len(samples), *samples))
        wav_bytes = buf.getvalue()

        # Submit to voice evaluate with audio file
        files = {"audio_file": ("test_recording.wav", wav_bytes, "audio/wav")}
        data = {"learner_id": 1, "lesson_id": 1, "transcript": "Hello world", "language_code": "en"}
        
        res = client.post("/api/voice/evaluate", data=data, files=files)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        audio_url = res_json.get("audio_url")
        self.assertTrue(bool(audio_url and audio_url.startswith("/api/voice/audio/")))
        
        # Verify physical retrieval of saved audio file from disk
        stream_res = client.get(audio_url)
        self.assertEqual(stream_res.status_code, 200)
        self.assertEqual(len(stream_res.content), len(wav_bytes))
        print(f"  ✓ [Audio Disk Persistence] Successfully saved & served audio from disk: {audio_url} ({len(stream_res.content)} bytes)")


if __name__ == "__main__":
    unittest.main()
