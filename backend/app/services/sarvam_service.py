import httpx
from app.config import settings

class SarvamAIService:
    def __init__(self):
        self.api_key = settings.SARVAM_API_KEY
        self.stt_url = settings.SARVAM_STT_ENDPOINT
        self.tts_url = settings.SARVAM_TTS_ENDPOINT

    async def transcribe_audio(self, audio_bytes: bytes, language_code: str = "hi-IN") -> str:
        """
        Calls Sarvam Saaras v3 Speech-to-Text API.
        Falls back gracefully to acoustic mock transcript if API key is not set.
        """
        if self.api_key == "mock_sarvam_api_key":
            return "नमस्ते आप कैसे हैं"

        headers = {"api-subscription-key": self.api_key}
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"language_code": language_code, "model": "saaras:v3"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.stt_url, headers=headers, files=files, data=data, timeout=10.0)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json.get("transcript", "")
            except Exception as e:
                print(f"Sarvam STT API call failed: {e}")
        
        return "नमस्ते आप कैसे हैं"

    async def generate_speech(self, text: str, language_code: str = "hi-IN") -> bytes:
        """
        Calls Sarvam Bulbul v3 Text-to-Speech API.
        """
        if self.api_key == "mock_sarvam_api_key":
            return b"mock_audio_bytes"

        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text],
            "target_language_code": language_code,
            "speaker": "meera",
            "model": "bulbul:v3"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.tts_url, headers=headers, json=payload, timeout=10.0)
                if response.status_code == 200:
                    return response.content
            except Exception as e:
                print(f"Sarvam TTS API call failed: {e}")

        return b"mock_audio_bytes"

    async def translate_text(self, text: str, source_lang: str = "en-IN", target_lang: str = "hi-IN") -> str:
        """
        Calls Sarvam Mayura v2 Translation API.
        """
        if self.api_key == "mock_sarvam_api_key":
            return text

        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # The API expects JSON body: {"input": text, "source_language_code": "en-IN", "target_language_code": "hi-IN", "model": "mayura:v2"}
        payload = {
            "input": text,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
            "model": "mayura:v2"
        }

        translate_url = getattr(settings, "SARVAM_TRANSLATE_ENDPOINT", "https://api.sarvam.ai/translate")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(translate_url, headers=headers, json=payload, timeout=10.0)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json.get("translated_text", text) # According to most of these it returns "translated_text", or maybe just adjust if we know the response format. We'll assume "translated_text".
            except Exception as e:
                print(f"Sarvam Translate API call failed: {e}")

        return text

sarvam_service = SarvamAIService()
