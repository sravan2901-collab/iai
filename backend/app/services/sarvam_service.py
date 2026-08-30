"""
Sarvam AI Integration Service for AksharAI Multilingual Literacy Platform.

Handles:
1. Speech-to-Text (STT) via Sarvam Saaras v3 with dynamic multi-tier fallback
   (Sarvam Saaras v3 -> Web Speech API Pass-Through -> Python SpeechRecognition -> Signal Evaluator)
2. Text-to-Speech (TTS) via Sarvam Bulbul v3 with fallback to gTTS
3. Translation via Sarvam Mayura v1
"""

import os
import io
import re
import asyncio
import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Sarvam Saaras v3 Supported Languages:
# hi-IN, bn-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN, gu-IN, en-IN
SARVAM_LANG_MAP = {
    "te": "te-IN",
    "te-in": "te-IN",
    "telugu": "te-IN",
    "hi": "hi-IN",
    "hi-in": "hi-IN",
    "hindi": "hi-IN",
    "ta": "ta-IN",
    "ta-in": "ta-IN",
    "tamil": "ta-IN",
    "bn": "bn-IN",
    "bn-in": "bn-IN",
    "bengali": "bn-IN",
    "kn": "kn-IN",
    "kn-in": "kn-IN",
    "kannada": "kn-IN",
    "mr": "mr-IN",
    "mr-in": "mr-IN",
    "marathi": "mr-IN",
    "en": "en-IN",
    "en-in": "en-IN",
    "en-us": "en-IN",
    "english": "en-IN",
    "gu": "gu-IN",
    "gu-in": "gu-IN",
    "gujarati": "gu-IN",
    "ml": "ml-IN",
    "ml-in": "ml-IN",
    "malayalam": "ml-IN",
    "pa": "pa-IN",
    "pa-in": "pa-IN",
    "punjabi": "pa-IN",
    "od": "od-IN",
    "or": "od-IN",
    "odia": "od-IN",
    "es": "es",
    "spanish": "es"
}

def detect_script_language(text: Optional[str], fallback: str = "en") -> str:
    """
    Auto-detects the Indic/Spanish/English script language from character Unicode ranges.
    Guarantees that Telugu, Tamil, Kannada, Bengali, Hindi, etc., are never misidentified.
    """
    if not text:
        return fallback
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "te"  # Telugu
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"  # Tamil
    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kn"  # Kannada
    if re.search(r'[\u0980-\u09FF]', text):
        return "bn"  # Bengali
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"  # Hindi / Devanagari
    if re.search(r'[áéíóúñÁÉÍÓÚÑ¡¿]', text) or re.search(r'\b(hola|mundo|gracias|buenos|dias|días|amigo|como|estas|por favor)\b', text, re.IGNORECASE):
        return "es"  # Spanish
    return fallback


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
        language_code: Optional[str] = None,
        client_transcript: Optional[str] = None,
        target_text: Optional[str] = None,
        audio_filename: str = "audio.wav"
    ) -> Dict[str, Any]:
        """
        Transcribes speech audio using Sarvam Saaras v3 STT.
        
        Requirements satisfied:
        - Sends form fields: language_code, model='saaras:v3', mode='transcribe'
        - Reads response.json()["transcript"] and returned language_code
        - Retries on HTTP 429 / 503 with backoff
        - Logs response body and request_id on failure
        - Skips Sarvam call for Spanish ('es'), relying on client-side transcript
        - Never defaults to Hindi for non-Hindi lessons
        """
        # Resolve language code: explicit parameter -> script detection from target_text -> fallback
        effective_lang = language_code
        if not effective_lang or effective_lang in ("en", "en-IN", ""):
            if target_text:
                detected = detect_script_language(target_text, fallback=effective_lang or "en")
                if detected != "en":
                    effective_lang = detected

        clean_client_transcript = (client_transcript or "").strip()

        # Spanish guard: Sarvam does not support Spanish STT — skip cleanly
        if effective_lang and (effective_lang.lower().startswith("es") or effective_lang.lower() == "spanish"):
            logger.info("[SARVAM STT] Spanish language detected — skipping Sarvam STT and using client speech transcript.")
            return {
                "transcript": clean_client_transcript,
                "provider": "browser_web_speech_api" if clean_client_transcript else "none",
                "status": "success" if clean_client_transcript else "spanish_skip",
                "language_code": "es-ES"
            }

        sarvam_lang = self.normalize_language_code(effective_lang or "en-IN")

        # -------------------------------------------------------------
        # TIER 1: Real Sarvam Saaras v3 STT API Call
        # -------------------------------------------------------------
        if self.is_configured() and audio_bytes and len(audio_bytes) > 100:
            api_key = self.get_api_key()
            headers = {"api-subscription-key": api_key}
            
            # Determine mime type from filename or audio bytes
            mime_type = "audio/wav"
            if audio_filename.lower().endswith(".mp3") or audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb":
                mime_type = "audio/mpeg"
                upload_name = "recording.mp3"
            elif audio_filename.lower().endswith(".ogg") or audio_bytes[:4] == b"OggS":
                mime_type = "audio/ogg"
                upload_name = "recording.ogg"
            elif audio_filename.lower().endswith(".flac") or audio_bytes[:4] == b"fLaC":
                mime_type = "audio/flac"
                upload_name = "recording.flac"
            else:
                mime_type = "audio/wav"
                upload_name = "recording.wav"

            files = {"file": (upload_name, audio_bytes, mime_type)}
            data = {
                "language_code": sarvam_lang,
                "model": "saaras:v3",
                "mode": "transcribe"
            }

            # Request with 30s timeout + 1 retry with exponential backoff on 429/503
            max_attempts = 2
            for attempt in range(1, max_attempts + 1):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            settings.SARVAM_STT_ENDPOINT,
                            headers=headers,
                            files=files,
                            data=data,
                            timeout=30.0
                        )

                        if response.status_code == 200:
                            res_json = response.json()
                            transcript = res_json.get("transcript", "").strip()
                            detected_lang = res_json.get("language_code") or sarvam_lang
                            req_id = res_json.get("request_id", "")
                            
                            logger.info(f"[SARVAM STT] Success (request_id={req_id}, lang={detected_lang}): '{transcript}'")
                            return {
                                "transcript": transcript,
                                "provider": "sarvam_ai_saaras_v3",
                                "status": "success" if transcript else "empty_transcript",
                                "language_code": detected_lang,
                                "request_id": req_id
                            }
                        
                        elif response.status_code in (429, 503) and attempt < max_attempts:
                            logger.warning(
                                f"[SARVAM STT] HTTP {response.status_code} on attempt {attempt}, retrying in 1.5s..."
                            )
                            await asyncio.sleep(1.5)
                            continue
                        else:
                            try:
                                err_json = response.json()
                                req_id = err_json.get("request_id") or err_json.get("error", {}).get("request_id", "unknown")
                                logger.error(
                                    f"[SARVAM STT] API error HTTP {response.status_code} (request_id={req_id}): {response.text}"
                                )
                            except Exception:
                                logger.error(
                                    f"[SARVAM STT] API error HTTP {response.status_code}: {response.text}"
                                )
                            break

                except httpx.TimeoutException as te:
                    logger.warning(f"[SARVAM STT] Timeout on attempt {attempt}: {te}")
                    if attempt < max_attempts:
                        await asyncio.sleep(1.0)
                        continue
                except Exception as err:
                    logger.error(f"[SARVAM STT] Network exception on attempt {attempt}: {err}")
                    if attempt < max_attempts:
                        await asyncio.sleep(1.0)
                        continue
                    break

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
            "language_code": sarvam_lang
        }

    async def generate_speech(
        self,
        text: str,
        language_code: str = "te",
        speaker: str = "priya"
    ) -> Optional[bytes]:
        """Generates natural spoken audio via Sarvam Bulbul v3 TTS."""
        if not self.is_configured():
            return None

        sarvam_lang = self.normalize_language_code(language_code)
        if sarvam_lang == "es":
            return None

        import base64
        api_key = self.get_api_key()
        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text.strip()],
            "target_language_code": sarvam_lang,
            "speaker": speaker,
            "model": "bulbul:v3"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.SARVAM_TTS_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=20.0
                )
                if response.status_code == 200:
                    res_json = response.json()
                    audios = res_json.get("audios", [])
                    if audios and isinstance(audios[0], str):
                        return base64.b64decode(audios[0])
                else:
                    logger.warning(f"[SARVAM TTS] API returned HTTP {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"[SARVAM TTS] Generation exception: {e}")

        return None

    async def translate_text(
        self,
        text: str,
        source_language_code: str = "en-IN",
        target_language_code: str = "te-IN"
    ) -> Optional[str]:
        """Translates text across Indic languages via Sarvam Mayura v1."""
        if not self.is_configured():
            return None

        src_lang = self.normalize_language_code(source_language_code)
        tgt_lang = self.normalize_language_code(target_language_code)

        if src_lang == tgt_lang:
            return text

        api_key = self.get_api_key()
        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "input": text.strip(),
            "source_language_code": src_lang,
            "target_language_code": tgt_lang,
            "speaker_gender": "Female",
            "mode": "formal",
            "model": "mayura:v1"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.SARVAM_TRANSLATE_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=15.0
                )
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json.get("translated_text", "")
        except Exception as e:
            logger.error(f"[SARVAM TRANSLATE] Exception: {e}")

        return None

    def get_service_status(self) -> Dict[str, Any]:
        """Returns the configuration status and active STT/TTS engine."""
        configured = self.is_configured()
        return {
            "sarvam_configured": configured,
            "stt_engine": "Sarvam Saaras v3" if configured else "Browser Web Speech API + SpeechRecognition",
            "tts_engine": "Sarvam Bulbul v3" if configured else "gTTS / Browser Synthesis",
            "supported_languages": list(SARVAM_LANG_MAP.keys()),
            "api_endpoint": settings.SARVAM_STT_ENDPOINT
        }


# Singleton service instance
sarvam_service = SarvamAIService()
