"""
Sarvam AI Integration Service for AksharAI Multilingual Literacy Platform.

Handles:
1. Speech-to-Text (STT) via Sarvam Saaras v3 with dynamic multi-tier fallback
   (Sarvam Saaras v3 -> Web Speech API Pass-Through -> Python SpeechRecognition -> Signal Evaluator)
2. Text-to-Speech (TTS) via Sarvam Bulbul v3 with fallback to gTTS / Web Speech
3. Translation via Sarvam Mayura v2
"""

import os
import io
import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

SARVAM_LANG_MAP = {
    "te": "te-IN",
    "te-in": "te-IN",
    "hi": "hi-IN",
    "hi-in": "hi-IN",
    "ta": "ta-IN",
    "ta-in": "ta-IN",
    "bn": "bn-IN",
    "bn-in": "bn-IN",
    "kn": "kn-IN",
    "kn-in": "kn-IN",
    "mr": "mr-IN",
    "mr-in": "mr-IN",
    "en": "en-IN",
    "en-in": "en-IN",
    "en-us": "en-IN",
    "gu": "gu-IN",
    "gu-in": "gu-IN",
    "ml": "ml-IN",
    "ml-in": "ml-IN",
    "pa": "pa-IN",
    "pa-in": "pa-IN",
    "od": "od-IN",
    "or": "od-IN",
    "es": "en-IN"
}

class SarvamAIService:
    """Service interacting with Sarvam AI API for Indic speech & language services."""

    def get_api_key(self) -> str:
        """Returns the active Sarvam API key from settings or OS environment."""
        key = (settings.SARVAM_API_KEY or os.getenv("SARVAM_API_KEY", "")).strip().strip("'\"")
        return key

    def is_configured(self) -> bool:
        """Returns True if a real Sarvam API Key is configured."""
        key = self.get_api_key()
        return bool(key and key != "mock_sarvam_api_key" and len(key) >= 10)

    def normalize_language_code(self, lang_code: str) -> str:
        """Normalizes any ISO language code (e.g. 'te', 'hi', 'en') to Sarvam language code (e.g. 'te-IN')."""
        if not lang_code:
            return "en-IN"
        clean = lang_code.strip().lower()
        return SARVAM_LANG_MAP.get(clean, SARVAM_LANG_MAP.get(clean.split('-')[0], "en-IN"))

    async def transcribe_audio(
        self,
        audio_bytes: Optional[bytes] = None,
        language_code: str = "en-IN",
        client_transcript: Optional[str] = None,
        target_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes speech audio using a multi-tiered pipeline:
        1. Primary: Sarvam Saaras v3 STT (if SARVAM_API_KEY is configured in .env)
        2. Secondary: Client Browser Web Speech API transcript (if provided by frontend)
        3. Tertiary: Python SpeechRecognition library (free Google Speech Recognition)
        4. Fallback: Empty transcript with status indicating no speech detected

        NEVER returns a static hardcoded dummy string.
        """
        sarvam_lang = self.normalize_language_code(language_code)
        clean_client_transcript = (client_transcript or "").strip()

        # -------------------------------------------------------------
        # TIER 1: Real Sarvam Saaras v3 STT API Call
        # -------------------------------------------------------------
        if self.is_configured() and audio_bytes and len(audio_bytes) > 100:
            api_key = self.get_api_key()
            headers = {"api-subscription-key": api_key}
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            data = {"language_code": sarvam_lang, "model": "saaras:v3"}

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        settings.SARVAM_STT_ENDPOINT,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=12.0
                    )
                    if response.status_code == 200:
                        res_json = response.json()
                        transcript = res_json.get("transcript", "").strip()
                        return {
                            "transcript": transcript,
                            "provider": "sarvam_ai_saaras_v3",
                            "status": "success" if transcript else "empty_transcript",
                            "language_code": sarvam_lang
                        }
                    else:
                        logger.warning(
                            f"[SARVAM STT] API returned HTTP {response.status_code}: {response.text}"
                        )
                except Exception as err:
                    logger.error(f"[SARVAM STT] Request exception: {err}")

        # -------------------------------------------------------------
        # TIER 2: Browser Web Speech API Transcript Pass-Through
        # -------------------------------------------------------------
        if clean_client_transcript:
            return {
                "transcript": clean_client_transcript,
                "provider": "browser_web_speech_api",
                "status": "success",
                "language_code": sarvam_lang
            }

        # -------------------------------------------------------------
        # TIER 3: Local Python SpeechRecognition (Google Free Speech Engine)
        # -------------------------------------------------------------
        if audio_bytes and len(audio_bytes) > 200:
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with io.BytesIO(audio_bytes) as audio_file:
                    with sr.AudioFile(audio_file) as source:
                        audio_data = recognizer.record(source)
                        sr_transcript = recognizer.recognize_google(
                            audio_data,
                            language=sarvam_lang
                        ).strip()
                        if sr_transcript:
                            return {
                                "transcript": sr_transcript,
                                "provider": "google_speech_recognition",
                                "status": "success",
                                "language_code": sarvam_lang
                            }
            except Exception as sr_err:
                logger.debug(f"[SPEECH_RECOGNITION] Local recognition notice: {sr_err}")

        # -------------------------------------------------------------
        # TIER 4: No speech recognized / Unconfigured state
        # -------------------------------------------------------------
        return {
            "transcript": "",
            "provider": "none",
            "status": "no_speech_detected",
            "language_code": sarvam_lang,
            "message": "No speech recognized. Please speak clearly into your microphone."
        }

    async def generate_speech(self, text: str, language_code: str = "hi-IN") -> bytes:
        """Calls Sarvam Bulbul v3 Text-to-Speech API if key configured."""
        if not self.is_configured():
            return b""

        sarvam_lang = self.normalize_language_code(language_code)
        headers = {
            "api-subscription-key": self.get_api_key(),
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text.strip()],
            "target_language_code": sarvam_lang,
            "speaker": "meera",
            "model": "bulbul:v3"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    settings.SARVAM_TTS_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.content
            except Exception as e:
                logger.error(f"[SARVAM TTS] API call failed: {e}")

        return b""

    async def translate_text(self, text: str, source_lang: str = "en-IN", target_lang: str = "hi-IN") -> str:
        """Calls Sarvam Mayura v2 Translation API if configured."""
        if not self.is_configured():
            return text

        src = self.normalize_language_code(source_lang)
        tgt = self.normalize_language_code(target_lang)

        headers = {
            "api-subscription-key": self.get_api_key(),
            "Content-Type": "application/json"
        }
        payload = {
            "input": text.strip(),
            "source_language_code": src,
            "target_language_code": tgt,
            "model": "mayura:v2"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    settings.SARVAM_TRANSLATE_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json.get("translated_text", text)
            except Exception as e:
                logger.error(f"[SARVAM TRANSLATE] API call failed: {e}")

        return text

    def get_service_status(self) -> Dict[str, Any]:
        """Returns the live status of the Sarvam AI service."""
        configured = self.is_configured()
        return {
            "sarvam_configured": configured,
            "stt_engine": "Sarvam Saaras v3" if configured else "Browser Web Speech API + SpeechRecognition",
            "tts_engine": "Sarvam Bulbul v3" if configured else "Google TTS (gTTS)",
            "supported_languages": list(SARVAM_LANG_MAP.keys()),
            "api_endpoint": settings.SARVAM_STT_ENDPOINT
        }

sarvam_service = SarvamAIService()
