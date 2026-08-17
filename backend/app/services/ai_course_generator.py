"""
AICourseGenerator — Open-Source LLM-Powered Course & Recommendation Engine
Supports: Groq (Llama 3.3 70B) → Ollama (local) → Rule-based fallback
"""
import json
import re
import logging
from typing import Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# Language display names for prompts
LANG_NAMES = {
    "en": "English", "hi": "Hindi (हिन्दी)", "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)", "mr": "Marathi (मराठी)", "bn": "Bengali (বাংলা)",
    "kn": "Kannada (ಕನ್ನಡ)", "es": "Spanish (Español)"
}

LANG_SCRIPTS = {
    "en": "Latin", "hi": "Devanagari", "te": "Telugu script", "ta": "Tamil script",
    "mr": "Devanagari", "bn": "Bengali script", "kn": "Kannada script", "es": "Latin with accents"
}


class AICourseGenerator:
    """
    AI-powered course content and recommendation generator.
    Uses a 3-tier fallback: Groq Cloud → Ollama Local → Rule-based Static.
    """

    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.groq_endpoint = settings.GROQ_ENDPOINT
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.ollama_timeout = settings.OLLAMA_TIMEOUT_SECONDS
        self.ai_provider = settings.AI_PROVIDER
        self.ai_enabled = settings.AI_LEARNING_ENGINE_ENABLED

    def get_active_provider(self) -> dict:
        """Returns which AI provider is currently active and available."""
        if not self.ai_enabled:
            return {"provider": "none", "model": None, "status": "AI engine disabled"}

        if self.ai_provider == "none":
            return {"provider": "rule-based", "model": None, "status": "AI provider set to none"}

        if self.ai_provider in ("auto", "groq") and self.groq_api_key:
            return {
                "provider": "groq",
                "model": self.groq_model,
                "status": "Groq API key configured"
            }

        if self.ai_provider in ("auto", "ollama"):
            return {
                "provider": "ollama",
                "model": self.ollama_model,
                "status": f"Ollama at {self.ollama_base_url}"
            }

        return {"provider": "rule-based", "model": None, "status": "No AI provider available"}

    # ─── Core AI Call Methods ───────────────────────────────────────────

    async def _call_groq(self, messages: list) -> Optional[str]:
        """Call Groq Cloud API (OpenAI-compatible endpoint)."""
        if not self.groq_api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.groq_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.groq_model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2048,
                        "response_format": {"type": "json_object"}
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info(f"Groq API success: {len(content)} chars")
                    return content
                else:
                    logger.warning(f"Groq API error {response.status_code}: {response.text[:200]}")
                    return None

        except Exception as e:
            logger.warning(f"Groq API exception: {e}")
            return None

    async def _call_ollama(self, messages: list) -> Optional[str]:
        """Call local Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=self.ollama_timeout) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": messages,
                        "stream": False,
                        "format": "json"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("message", {}).get("content", "")
                    logger.info(f"Ollama success: {len(content)} chars")
                    return content
                else:
                    logger.warning(f"Ollama error {response.status_code}")
                    return None

        except Exception as e:
            logger.warning(f"Ollama exception (likely not running): {e}")
            return None

    async def _call_ai(self, messages: list) -> tuple[Optional[str], str]:
        """
        Try AI providers in priority order. Returns (response_text, provider_used).
        """
        if not self.ai_enabled or self.ai_provider == "none":
            return None, "rule-based"

        # Try Groq first (if configured)
        if self.ai_provider in ("auto", "groq") and self.groq_api_key:
            result = await self._call_groq(messages)
            if result:
                return result, "groq"

        # Try Ollama second
        if self.ai_provider in ("auto", "ollama"):
            result = await self._call_ollama(messages)
            if result:
                return result, "ollama"

        return None, "rule-based"

    def _parse_json_response(self, text: str) -> Optional[dict]:
        """Robustly extract JSON from LLM response (handles markdown fences, partial JSON)."""
        if not text:
            return None

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code fences
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if '```' in pattern else match.group(0))
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to parse JSON from AI response: {text[:200]}")
        return None

    # ─── Recommendation Generator ───────────────────────────────────────

    async def generate_recommendations(self, profile_data: dict) -> tuple[list, str]:
        """
        Generate 3 personalized learning recommendations.
        Returns (recommendations_list, provider_used).
        """
        lang = profile_data.get("language", "en")
        lang_name = LANG_NAMES.get(lang, "English")
        reading = profile_data.get("reading_pct", 0)
        comprehension = profile_data.get("comprehension_pct", 0)
        voice = profile_data.get("voice_pct", 0)
        level = profile_data.get("literacy_level", "FOUNDATIONAL")
        completed = profile_data.get("completed_lessons", 0)
        total = profile_data.get("total_lessons", 0)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert literacy education advisor for the AksharAI platform. "
                    "You analyze learner performance data and generate personalized learning recommendations. "
                    "Always respond with valid JSON only. No markdown, no explanations outside the JSON."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Analyze this learner's profile and generate exactly 3 personalized learning recommendations.\n\n"
                    f"LEARNER PROFILE:\n"
                    f"- Language: {lang_name}\n"
                    f"- Proficiency Level: {level}\n"
                    f"- Reading Score: {reading}%\n"
                    f"- Comprehension Score: {comprehension}%\n"
                    f"- Voice/Pronunciation Score: {voice}%\n"
                    f"- Lessons Completed: {completed}/{total}\n"
                    f"- Weakest Skill: {self._identify_weakest(reading, comprehension, voice)}\n\n"
                    f"Return a JSON object with this exact structure:\n"
                    f'{{"recommendations": [\n'
                    f'  {{"type": "practice_weak_area|continue_module|try_new_module",\n'
                    f'   "title": "Short descriptive title",\n'
                    f'   "reason": "2-3 sentence personalized explanation of why this is recommended",\n'
                    f'   "priority": "HIGH|MEDIUM|LOW",\n'
                    f'   "skill_focus": "READING|COMPREHENSION|VOICE"}}\n'
                    f']}}\n\n'
                    f"Make the first recommendation HIGH priority targeting their weakest skill. "
                    f"Make reasons specific to their exact scores, not generic advice."
                )
            }
        ]

        ai_response, provider = await self._call_ai(messages)

        if ai_response:
            parsed = self._parse_json_response(ai_response)
            if parsed and "recommendations" in parsed:
                recs = parsed["recommendations"][:3]
                # Validate structure
                valid_recs = []
                for r in recs:
                    valid_recs.append({
                        "type": r.get("type", "practice_weak_area"),
                        "title": r.get("title", "Practice recommended skill"),
                        "reason": r.get("reason", "Based on your assessment scores"),
                        "priority": r.get("priority", "MEDIUM"),
                        "skill_focus": r.get("skill_focus", "READING")
                    })
                return valid_recs, provider

        # Rule-based fallback
        return self._get_rule_based_recommendations(profile_data), "rule-based"

    # ─── Exercise Generator ─────────────────────────────────────────────

    async def generate_exercise(
        self, language: str, skill_type: str, difficulty: str,
        existing_titles: list = None
    ) -> tuple[dict, str]:
        """
        Generate a custom practice exercise for a specific skill area.
        Returns (exercise_dict, provider_used).
        """
        lang_name = LANG_NAMES.get(language, "English")
        script_name = LANG_SCRIPTS.get(language, "Latin")
        existing = ", ".join(existing_titles[:5]) if existing_titles else "None"

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are an expert {lang_name} literacy content creator. "
                    f"You create educational exercises for language learners. "
                    f"All content in {lang_name} must use the {script_name} script. "
                    f"Always respond with valid JSON only."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Create a {difficulty} level {skill_type} exercise for a {lang_name} language learner.\n\n"
                    f"REQUIREMENTS:\n"
                    f"- The target practice text MUST be in {lang_name} using {script_name} script\n"
                    f"- Include phonetic syllable breakdown of the practice text\n"
                    f"- Create 3 multiple-choice questions about the text\n"
                    f"- Avoid duplicating these existing lessons: {existing}\n\n"
                    f"Return a JSON object with this exact structure:\n"
                    f'{{"title": "Lesson title in {lang_name}",\n'
                    f' "title_english": "English translation of the title",\n'
                    f' "target_text": "A meaningful practice sentence in {lang_name} ({script_name} script)",\n'
                    f' "phonetic_script": ["syl-la-ble-1", "syl-la-ble-2"],\n'
                    f' "content_type": "Voice Practice",\n'
                    f' "questions": [\n'
                    f'   {{"question": "Question text in English",\n'
                    f'    "options": ["A", "B", "C", "D"],\n'
                    f'    "correct_answer": "A"}}\n'
                    f' ],\n'
                    f' "explanation": "Brief teaching note about this exercise"}}'
                )
            }
        ]

        ai_response, provider = await self._call_ai(messages)

        if ai_response:
            parsed = self._parse_json_response(ai_response)
            if parsed and "target_text" in parsed:
                exercise = {
                    "title": parsed.get("title", f"{skill_type} Practice"),
                    "title_english": parsed.get("title_english", ""),
                    "target_text": parsed.get("target_text", ""),
                    "phonetic_script": parsed.get("phonetic_script", []),
                    "content_type": parsed.get("content_type", "Voice Practice"),
                    "questions": parsed.get("questions", []),
                    "explanation": parsed.get("explanation", ""),
                    "difficulty_level": difficulty,
                    "skill_type": skill_type
                }
                return exercise, provider

        # Rule-based fallback exercise
        return self._get_fallback_exercise(language, skill_type, difficulty), "rule-based"

    # ─── Helper Methods ─────────────────────────────────────────────────

    def _identify_weakest(self, reading: float, comprehension: float, voice: float) -> str:
        """Identify the weakest skill area."""
        scores = {"READING": reading, "COMPREHENSION": comprehension, "VOICE": voice}
        return min(scores, key=scores.get)

    def _get_rule_based_recommendations(self, profile_data: dict) -> list:
        """Generate static recommendations — each card targets a DIFFERENT skill."""
        reading = profile_data.get("reading_pct", 0)
        comprehension = profile_data.get("comprehension_pct", 0)
        voice = profile_data.get("voice_pct", 0)
        completed = profile_data.get("completed_lessons", 0)
        total = profile_data.get("total_lessons", 0)

        # Sort skills by score (ascending) so weakest is first
        skills = [
            ("VOICE", voice, "Voice & Pronunciation"),
            ("READING", reading, "Reading & Phonics"),
            ("COMPREHENSION", comprehension, "Comprehension & Vocabulary")
        ]
        skills.sort(key=lambda x: x[1])

        recs = []

        # Recommendation 1 (HIGH) — weakest skill
        sk, sc, label = skills[0]
        recs.append({
            "type": "practice_weak_area",
            "title": f"Boost Your {label}",
            "reason": (
                f"Your {label.lower()} score is {sc}%, which is your weakest area. "
                f"Targeted practice in this skill will have the biggest impact on your "
                f"overall literacy level. Focus on exercises that build this foundation."
            ),
            "priority": "HIGH",
            "skill_focus": sk
        })

        # Recommendation 2 (MEDIUM) — middle skill + progress context
        sk2, sc2, label2 = skills[1]
        if completed < total:
            progress_pct = round((completed / max(total, 1)) * 100)
            recs.append({
                "type": "continue_module",
                "title": f"Continue Your Current Learning Path",
                "reason": (
                    f"You've completed {completed} of {total} lessons ({progress_pct}%). "
                    f"Keep up the momentum — consistency is key to language mastery. "
                    f"Your {label2.lower()} score ({sc2}%) can improve with regular practice."
                ),
                "priority": "MEDIUM",
                "skill_focus": sk2
            })
        else:
            recs.append({
                "type": "try_new_module",
                "title": f"Strengthen Your {label2}",
                "reason": (
                    f"You've completed all {total} lessons! Your {label2.lower()} "
                    f"score is {sc2}%. Generate a custom AI exercise to push this "
                    f"skill further and unlock advanced content."
                ),
                "priority": "MEDIUM",
                "skill_focus": sk2
            })

        # Recommendation 3 (LOW) — strongest skill (maintain & grow)
        sk3, sc3, label3 = skills[2]
        recs.append({
            "type": "try_new_module",
            "title": f"Practice {label3}",
            "reason": (
                f"Your {label3.lower()} score is {sc3}%, your strongest area. "
                f"While focusing on weaker skills, don't neglect your strengths. "
                f"A balanced approach leads to faster overall fluency."
            ),
            "priority": "LOW",
            "skill_focus": sk3
        })

        return recs

    def _get_fallback_exercise(self, language: str, skill_type: str, difficulty: str) -> dict:
        """Return a pre-built fallback exercise when AI is unavailable."""
        lang_name = LANG_NAMES.get(language, "English")

        fallback_texts = {
            "en": {"target": "Practice makes perfect in language learning", "phonemes": ["Prac-tice", "makes", "per-fect"]},
            "hi": {"target": "निरंतर अभ्यास से ही भाषा में निपुणता आती है", "phonemes": ["नि-रं-त-र", "अभ्-या-स"]},
            "te": {"target": "నిరంతర సాధన ద్వారా భాషా ప్రావీణ్యం లభిస్తుంది", "phonemes": ["నిరం-త-ర", "సా-ధ-న"]},
            "ta": {"target": "தொடர் பயிற்சியால் மொழி திறன் வளரும்", "phonemes": ["தொ-ட-ர்", "ப-யிற்-சி"]},
            "mr": {"target": "सातत्याने सरावाने भाषेत प्रगती होते", "phonemes": ["सा-त-त्या-ने", "स-रा-वा-ने"]},
            "bn": {"target": "নিয়মিত অভ্যাসে ভাষার দক্ষতা বাড়ে", "phonemes": ["নি-য়-মি-ত", "অভ্-যা-সে"]},
            "kn": {"target": "ನಿರಂತರ ಅಭ್ಯಾಸದಿಂದ ಭಾಷಾ ಪ್ರಾವೀಣ್ಯ ಬರುತ್ತದೆ", "phonemes": ["ನಿ-ರಂ-ತ-ರ", "ಅಭ್-ಯಾ-ಸ"]},
            "es": {"target": "La práctica constante mejora el dominio del idioma", "phonemes": ["prác-ti-ca", "cons-tan-te"]},
        }

        fb = fallback_texts.get(language, fallback_texts["en"])

        return {
            "title": f"{skill_type.title()} Practice — {lang_name}",
            "title_english": f"{skill_type.title()} Practice Exercise",
            "target_text": fb["target"],
            "phonetic_script": fb["phonemes"],
            "content_type": "Voice Practice",
            "questions": [
                {
                    "question": f"What skill does this exercise focus on?",
                    "options": ["Reading", "Comprehension", "Voice", "Writing"],
                    "correct_answer": skill_type.title()
                }
            ],
            "explanation": f"This is a {difficulty.lower()} level {skill_type.lower()} exercise. "
                          f"Practice reading the text aloud with correct pronunciation.",
            "difficulty_level": difficulty,
            "skill_type": skill_type
        }


# Singleton instance
ai_course_generator = AICourseGenerator()
