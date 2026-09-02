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

    # ─── Report Narrative Generator ─────────────────────────────────────

    async def generate_report_narrative(self, snapshot_dict: dict) -> Optional[str]:
        """
        Generate a cohesive 3-5 sentence narrative pedagogical report for the learner's progress snapshot.
        Returns AI narrative string, or a sensible rule-based narrative if AI is unavailable.
        """
        profile = snapshot_dict.get("profile", {})
        path_stats = snapshot_dict.get("path_stats", {})
        lang_name = snapshot_dict.get("language", "English")
        learner_name = snapshot_dict.get("learner_name", "Learner")
        
        reading = profile.get("reading_pct", 0)
        comprehension = profile.get("comprehension_pct", 0)
        voice = profile.get("voice_pct", 0)
        overall = profile.get("overall_pct", 0)
        level = profile.get("literacy_level", "FOUNDATIONAL")
        streak = snapshot_dict.get("streak_count", profile.get("streak_count", 0))
        points = snapshot_dict.get("total_points", profile.get("total_points", 0))
        completed_lessons = path_stats.get("completed_lessons", 0)
        total_lessons = path_stats.get("total_lessons", 0)
        weakest = self._identify_weakest(reading, comprehension, voice)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert literacy education advisor and progress evaluator for the AksharAI platform. "
                    "Write a concise, encouraging, and actionable 3-5 sentence learning report narrative summarizing "
                    "the learner's achievements, current strengths, and specific areas to practice next. "
                    "Respond with plain text only (no JSON, no bullet points, no markdown formatting)."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a personalized learning report narrative for {learner_name}.\n\n"
                    f"LEARNER SNAPSHOT:\n"
                    f"- Target Language: {lang_name}\n"
                    f"- Proficiency Tier: {level}\n"
                    f"- Overall Mastery: {overall}%\n"
                    f"- Reading & Phonics Score: {reading}%\n"
                    f"- Comprehension Score: {comprehension}%\n"
                    f"- Voice & Pronunciation Score: {voice}%\n"
                    f"- Active Practice Streak: {streak} days\n"
                    f"- Total Earned Points: {points} XP\n"
                    f"- Curriculum Lessons Completed: {completed_lessons} of {total_lessons}\n"
                    f"- Weakest Focus Skill: {weakest}\n\n"
                    f"Requirements: 3-5 sentences total. Highlight key strengths, acknowledge practice consistency/streak, "
                    f"and provide a concrete pedagogical recommendation for improving their {weakest.lower()} skills."
                )
            }
        ]

        ai_response, _provider = await self._call_ai(messages)
        if ai_response:
            clean_text = ai_response.strip()
            if clean_text.startswith("{") and clean_text.endswith("}"):
                try:
                    parsed = json.loads(clean_text)
                    clean_text = parsed.get("narrative") or parsed.get("report") or list(parsed.values())[0]
                except Exception:
                    pass
            clean_text = re.sub(r'^["\']|["\']$', '', clean_text.strip())
            if clean_text:
                return clean_text

        # Rule-based fallback narrative if AI provider is unavailable
        weak_label = "Voice & Pronunciation" if weakest == "VOICE" else ("Reading & Phonics" if weakest == "READING" else "Comprehension & Vocabulary")
        fallback_narrative = (
            f"{learner_name} is making steady progress at the {level} tier in {lang_name} with an overall mastery score of {overall}%. "
            f"With an active {streak}-day practice streak and {points} XP earned, commitment to daily literacy practice remains strong. "
            f"To accelerate progress toward fluency, prioritize targeted exercises in {weak_label} while continuing your structured curriculum path."
        )
        return fallback_narrative

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
                    f"You are an expert {lang_name} literacy curriculum AI creator. "
                    f"You create progressive step-by-step learning modules for language learners starting from zero knowledge to beginner level. "
                    f"All content in {lang_name} must use the {script_name} script. "
                    f"Always respond with valid JSON only."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a full progressive 5-step beginner learning module curriculum for a {lang_name} language learner starting from ZERO KNOWLEDGE up to BEGINNER level.\n"
                    f"Focus Skill: {skill_type}\n"
                    f"Target Language: {lang_name} ({script_name} script)\n"
                    f"Difficulty Level: {difficulty}\n\n"
                    f"REQUIREMENTS:\n"
                    f"- Generate exactly 5 progressive course steps:\n"
                    f"  Step 1: ZERO KNOWLEDGE (Alphabet Single Letter Sounds & Phonemes)\n"
                    f"  Step 2: ABSOLUTE STARTER (Vowels & Short Sound Recognition)\n"
                    f"  Step 3: BEGINNER TIER 1 (2-Letter Word Blends & Syllables)\n"
                    f"  Step 4: BEGINNER TIER 2 (3-Letter Everyday Object Nouns)\n"
                    f"  Step 5: BEGINNER TIER 3 (Simple Expressive Sentences)\n"
                    f"- Avoid duplicating these existing titles: {existing}\n\n"
                    f"Return a JSON object with this exact structure:\n"
                    f'{{\n'
                    f' "title": "Course Title in {lang_name}",\n'
                    f' "title_english": "English translation of course title",\n'
                    f' "explanation": "Brief pedagogical note explaining the zero-knowledge to beginner progression",\n'
                    f' "target_text": "Sample practice sentence for final step in {lang_name}",\n'
                    f' "phonetic_script": ["syl-la-ble-1", "syl-la-ble-2"],\n'
                    f' "content_type": "Voice Practice",\n'
                    f' "course_steps": [\n'
                    f'   {{\n'
                    f'     "step_no": 1,\n'
                    f'     "stage": "ZERO KNOWLEDGE",\n'
                    f'     "title": "Step 1 Title",\n'
                    f'     "target_text": "Single letter sounds text in {lang_name}",\n'
                    f'     "phonetic_script": ["A-ah", "B-buh"],\n'
                    f'     "focus": "Pedagogical focus for Step 1"\n'
                    f'   }},\n'
                    f'   {{\n'
                    f'     "step_no": 2,\n'
                    f'     "stage": "ABSOLUTE STARTER",\n'
                    f'     "title": "Step 2 Title",\n'
                    f'     "target_text": "Vowels text in {lang_name}",\n'
                    f'     "phonetic_script": ["A-apple", "E-egg"],\n'
                    f'     "focus": "Pedagogical focus for Step 2"\n'
                    f'   }},\n'
                    f'   {{\n'
                    f'     "step_no": 3,\n'
                    f'     "stage": "BEGINNER TIER 1",\n'
                    f'     "title": "Step 3 Title",\n'
                    f'     "target_text": "2-letter words text in {lang_name}",\n'
                    f'     "phonetic_script": ["In", "On", "At"],\n'
                    f'     "focus": "Pedagogical focus for Step 3"\n'
                    f'   }},\n'
                    f'   {{\n'
                    f'     "step_no": 4,\n'
                    f'     "stage": "BEGINNER TIER 2",\n'
                    f'     "title": "Step 4 Title",\n'
                    f'     "target_text": "3-letter words text in {lang_name}",\n'
                    f'     "phonetic_script": ["Cat", "Dog", "Sun"],\n'
                    f'     "focus": "Pedagogical focus for Step 4"\n'
                    f'   }},\n'
                    f'   {{\n'
                    f'     "step_no": 5,\n'
                    f'     "stage": "BEGINNER TIER 3",\n'
                    f'     "title": "Step 5 Title",\n'
                    f'     "target_text": "Simple sentence text in {lang_name}",\n'
                    f'     "phonetic_script": ["I", "can", "read"],\n'
                    f'     "focus": "Pedagogical focus for Step 5"\n'
                    f'   }}\n'
                    f' ],\n'
                    f' "questions": [\n'
                    f'   {{"question": "Question text in English", "options": ["A", "B", "C", "D"], "correct_answer": "A"}}\n'
                    f' ]\n'
                    f'}}\n'
                )
            }
        ]

        ai_response, provider = await self._call_ai(messages)

        if ai_response:
            parsed = self._parse_json_response(ai_response)
            if parsed and ("target_text" in parsed or "course_steps" in parsed):
                exercise = {
                    "title": parsed.get("title", f"{skill_type} Practice"),
                    "title_english": parsed.get("title_english", ""),
                    "target_text": parsed.get("target_text", ""),
                    "phonetic_script": parsed.get("phonetic_script", []),
                    "content_type": parsed.get("content_type", "Voice Practice"),
                    "questions": parsed.get("questions", []),
                    "explanation": parsed.get("explanation", ""),
                    "difficulty_level": difficulty,
                    "skill_type": skill_type,
                    "course_steps": parsed.get("course_steps", [])
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
        """Return a pre-built beginner-friendly exercise tailored specifically to skill_type and difficulty level."""
        lang_name = LANG_NAMES.get(language, "English")
        clean_skill = (skill_type or "READING").upper()
        clean_diff = (difficulty or "FOUNDATIONAL").upper()

        fallback_db = {
            "en": {
                ("VOICE", "FOUNDATIONAL"): {
                    "title": "Alphabet Vowels & Phonics Fundamentals",
                    "title_english": "Alphabet Vowels & Phonics Fundamentals",
                    "target_text": "A, B, C, D — Long & Short Vowel Sounds",
                    "phonetic_script": ["A", "B", "C", "D", "Vow-els"],
                    "content_type": "Voice Practice",
                    "questions": [
                        {"question": "Which letter is a vowel sound?", "options": ["A", "B", "C", "D"], "correct_answer": "A"},
                        {"question": "How many basic vowel letters are in English?", "options": ["5", "2", "10", "26"], "correct_answer": "5"}
                    ],
                    "explanation": "Beginner Voice Exercise: Learn and speak aloud fundamental alphabet sounds and vowel phonemes."
                },
                ("COMPREHENSION", "FOUNDATIONAL"): {
                    "title": "Everyday 3-Letter Vocabulary Words",
                    "title_english": "Everyday 3-Letter Vocabulary Words",
                    "target_text": "Cat, Dog, Sun, Book, Cup",
                    "phonetic_script": ["Cat", "Dog", "Sun", "Book", "Cup"],
                    "content_type": "Functional Reading",
                    "questions": [
                        {"question": "Which word refers to an everyday pet?", "options": ["Dog", "Sun", "Cup", "Book"], "correct_answer": "Dog"},
                        {"question": "Which word refers to the bright star in the sky?", "options": ["Sun", "Cat", "Cup", "Dog"], "correct_answer": "Sun"}
                    ],
                    "explanation": "Beginner Vocabulary Exercise: Recognize and read basic everyday 3-letter nouns."
                },
                ("READING", "FOUNDATIONAL"): {
                    "title": "Simple Beginner Sentence Reading",
                    "title_english": "Simple Beginner Sentence Reading",
                    "target_text": "I can read simple English words",
                    "phonetic_script": ["I", "can", "read", "sim-ple", "words"],
                    "content_type": "Voice Practice",
                    "questions": [
                        {"question": "What is the primary action in the sentence?", "options": ["Read", "Run", "Sleep", "Write"], "correct_answer": "Read"},
                        {"question": "What language is being practiced?", "options": ["English", "Spanish", "French", "German"], "correct_answer": "English"}
                    ],
                    "explanation": "Beginner Sentence Reading: Read short 5-word English sentences with clarity and confidence."
                },
                ("VOICE", "FUNCTIONAL"): {
                    "title": "Workplace Team Meeting Greetings",
                    "title_english": "Workplace Team Meeting Greetings",
                    "target_text": "Good morning team, let us review our daily goals",
                    "phonetic_script": ["Good", "morn-ing", "team", "dai-ly", "goals"],
                    "content_type": "Voice Practice",
                    "questions": [
                        {"question": "What time of day is referenced in the greeting?", "options": ["Morning", "Night", "Evening", "Afternoon"], "correct_answer": "Morning"}
                    ],
                    "explanation": "Functional Voice Exercise: Practice speaking professional workplace greetings with clear intonation."
                },
                ("COMPREHENSION", "FUNCTIONAL"): {
                    "title": "ATM PIN Security Guidelines",
                    "title_english": "ATM PIN Security Guidelines",
                    "target_text": "Never share your ATM PIN with anyone",
                    "phonetic_script": ["Ne-ver", "share", "ATM", "PIN", "any-one"],
                    "content_type": "Functional Reading",
                    "questions": [
                        {"question": "Should you share your ATM PIN?", "options": ["Never", "Always", "Sometimes", "With friends"], "correct_answer": "Never"}
                    ],
                    "explanation": "Functional Reading Exercise: Understand practical banking and security guidelines."
                },
                ("READING", "FUNCTIONAL"): {
                    "title": "Health & Medical Prescription Reading",
                    "title_english": "Health & Medical Prescription Reading",
                    "target_text": "Take one tablet after breakfast with water",
                    "phonetic_script": ["Take", "one", "tab-let", "af-ter", "break-fast"],
                    "content_type": "Functional Reading",
                    "questions": [
                        {"question": "When should the tablet be taken?", "options": ["After breakfast", "Before sleep", "At midnight", "Never"], "correct_answer": "After breakfast"}
                    ],
                    "explanation": "Functional Reading Exercise: Read medical prescription instructions accurately."
                }
            },
            "te": {
                ("VOICE", "FOUNDATIONAL"): {
                    "title": "అక్షరాలు మరియు స్వరాలు (Alphabet Vowels)",
                    "title_english": "Alphabet Vowels & Phonics",
                    "target_text": "అ, ఆ, ఇ, ఈ — ప్రాథమిక అక్షర గుర్తింపు",
                    "phonetic_script": ["అ", "ఆ", "ఇ", "ఈ"],
                    "content_type": "Voice Practice",
                    "questions": [{"question": "మొదటి అక్షరం ఏది?", "options": ["అ", "ఆ", "ఇ", "ఈ"], "correct_answer": "అ"}],
                    "explanation": "ప్రారంభ స్థాయి ఉచ్చారణ సాధన: తెలుగు అచ్చులు మరియు ప్రాథమిక అక్షర గుర్తింపు."
                },
                ("COMPREHENSION", "FOUNDATIONAL"): {
                    "title": "దైనందిన 3 అక్షరాల పదాలు (Everyday Words)",
                    "title_english": "Everyday 3-Letter Words",
                    "target_text": "అమ్మ, ఇల్లు, నీరు, పుస్తకం",
                    "phonetic_script": ["అమ్మ", "ఇల్లు", "నీరు", "పుస్తకం"],
                    "content_type": "Functional Reading",
                    "questions": [{"question": "ఇంటికి ఉపయోగించే పదం ఏది?", "options": ["ఇల్లు", "నీరు", "అమ్మ", "పుస్తకం"], "correct_answer": "ఇల్లు"}],
                    "explanation": "ప్రారంభ స్థాయి పదజాలం: రోజువారీ ఉపయోగించే ముఖ్యమైన పదాలు."
                },
                ("READING", "FOUNDATIONAL"): {
                    "title": "లఘు వాక్య పఠనం (Simple Sentence Reading)",
                    "title_english": "Simple Sentence Reading",
                    "target_text": "నేను ప్రతిరోజూ పుస్తకాలు చదువుతాను",
                    "phonetic_script": ["నేను", "ప్రతిరోజూ", "పుస్తకాలు", "చదువుతాను"],
                    "content_type": "Voice Practice",
                    "questions": [{"question": "ఈ వాక్యం దేని గురించి?", "options": ["చదవడం", "పరిగెత్తడం", "నిద్రించడం", "రాయడం"], "correct_answer": "చదవడం"}],
                    "explanation": "ప్రారంభ స్థాయి వాక్య పఠనం: చిన్న వాక్యాలను స్పష్టంగా చదవడం సాధన చేయండి."
                }
            },
            "hi": {
                ("VOICE", "FOUNDATIONAL"): {
                    "title": "वर्णमाला एवं स्वर उच्चारण (Alphabet Vowels)",
                    "title_english": "Alphabet Vowels & Phonics",
                    "target_text": "अ, आ, इ, ई — बुनियादी स्वर पहचान",
                    "phonetic_script": ["अ", "आ", "इ", "ई"],
                    "content_type": "Voice Practice",
                    "questions": [{"question": "पहला स्वर कौन सा है?", "options": ["अ", "आ", "इ", "ई"], "correct_answer": "अ"}],
                    "explanation": "शुरुआती स्वर अभ्यास: हिंदी वर्णमाला और प्राथमिक स्वर पहचान।"
                },
                ("COMPREHENSION", "FOUNDATIONAL"): {
                    "title": "दैनिक व्यावहारिक शब्द (Everyday Words)",
                    "title_english": "Everyday Words",
                    "target_text": "घर, जल, फल, पुस्तक, मित्र",
                    "phonetic_script": ["घर", "जल", "फल", "पुस्तक"],
                    "content_type": "Functional Reading",
                    "questions": [{"question": "पानी के लिए कौन सा शब्द प्रयुक्त है?", "options": ["जल", "फल", "घर", "मित्र"], "correct_answer": "जल"}],
                    "explanation": "शुरुआती शब्दावली अभ्यास: दैनिक जीवन के आसान शब्द।"
                },
                ("READING", "FOUNDATIONAL"): {
                    "title": "सरल वाक्य वाचन (Simple Sentence Reading)",
                    "title_english": "Simple Sentence Reading",
                    "target_text": "मैं प्रतिदिन अच्छी पुस्तकें पढ़ता हूँ",
                    "phonetic_script": ["मैं", "प्रतिदिन", "पुस्तकें", "पढ़ता"],
                    "content_type": "Voice Practice",
                    "questions": [{"question": "वाक्य में क्या कार्य हो रहा है?", "options": ["पढ़ना", "दौड़ना", "सोना", "लिखना"], "correct_answer": "पढ़ना"}],
                    "explanation": "शुरुआती वाक्य वाचन: छोटे वाक्यों का स्पष्ट उच्चारण।"
                }
            }
        }

        lang_db = fallback_db.get(language, fallback_db["en"])
        exercise = lang_db.get((clean_skill, clean_diff))

        if not exercise:
            # Fallback to English skill-matched exercise if target language entry missing
            exercise = fallback_db["en"].get((clean_skill, clean_diff), fallback_db["en"][("READING", "FOUNDATIONAL")])

        # Progressive 5-Step Roadmap from Zero Knowledge to Beginner
        course_steps = [
            {
                "step_no": 1,
                "stage": "ZERO KNOWLEDGE",
                "stage_label": "Step 1: Single Letter Phonemes & Sounds",
                "title": "Alphabet Letter Sounds",
                "target_text": "A, B, C, D — Single Letter Sound Phonemes",
                "phonetic_script": ["A-ah", "B-buh", "C-kuh", "D-duh"],
                "focus": "Absolute starter: Learn fundamental single letter sounds."
            },
            {
                "step_no": 2,
                "stage": "ABSOLUTE STARTER",
                "stage_label": "Step 2: Vowel Recognition & Sounds",
                "title": "Vowel Sounds & Recognition",
                "target_text": "A, E, I, O, U — Short Vowel Sounds",
                "phonetic_script": ["A-apple", "E-egg", "I-ink", "O-owl", "U-up"],
                "focus": "Recognize and pronounce basic long and short vowel sounds."
            },
            {
                "step_no": 3,
                "stage": "BEGINNER TIER 1",
                "stage_label": "Step 3: Two-Letter Word Blends",
                "title": "Two-Letter Word Formation",
                "target_text": "In, On, At, Go, To, Up, Me, He, We",
                "phonetic_script": ["In", "On", "At", "Go", "To", "Up"],
                "focus": "Combine vowels and consonants to form 2-letter words."
            },
            {
                "step_no": 4,
                "stage": "BEGINNER TIER 2",
                "stage_label": "Step 4: Three-Letter Everyday Nouns",
                "title": "Everyday 3-Letter Object Words",
                "target_text": "Cat, Dog, Sun, Cup, Pen, Book, Box",
                "phonetic_script": ["Cat", "Dog", "Sun", "Cup", "Pen"],
                "focus": "Read and understand common 3-letter everyday nouns."
            },
            {
                "step_no": 5,
                "stage": "BEGINNER TIER 3",
                "stage_label": "Step 5: Simple Expressive Sentences",
                "title": "Simple Expressive Sentence Reading",
                "target_text": exercise["target_text"],
                "phonetic_script": exercise["phonetic_script"],
                "focus": "Read short complete sentences with confidence."
            }
        ]

        return {
            "title": exercise["title"],
            "title_english": exercise.get("title_english", f"{clean_skill.title()} Practice"),
            "target_text": exercise["target_text"],
            "phonetic_script": exercise["phonetic_script"],
            "content_type": exercise.get("content_type", "Voice Practice"),
            "questions": exercise.get("questions", []),
            "explanation": exercise.get("explanation", f"Beginner {clean_skill.lower()} exercise for {lang_name}."),
            "difficulty_level": clean_diff,
            "skill_type": clean_skill,
            "course_steps": course_steps
        }


# Singleton instance
ai_course_generator = AICourseGenerator()
