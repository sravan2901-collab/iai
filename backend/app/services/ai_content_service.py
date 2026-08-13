"""
AI Content & Learning Path Service for AksharAI Language Literacy Platform.

Interactions with local open-source LLMs via Ollama (Llama 3.1, Mistral, Gemma 2)
to generate dynamic, personalized learning paths and lesson content. Gracefully
falls back to rule-based logic if Ollama is offline or disabled.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from app.config import settings


def is_ai_available() -> bool:
    """
    Checks if Ollama LLM integration is enabled and reachable locally.
    """
    if not settings.AI_LEARNING_ENGINE_ENABLED:
        return False

    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/version"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AksharAI-Backend"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def _query_ollama_json(prompt: str, system_prompt: str = "") -> Optional[Any]:
    """
    Helper function to send prompt to Ollama's /api/generate endpoint and extract JSON.
    """
    if not is_ai_available():
        return None

    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt or "You are an expert AI educator producing structured JSON output only.",
        "stream": False,
        "format": "json"
    }

    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=settings.OLLAMA_TIMEOUT_SECONDS) as resp:
            if resp.status != 200:
                return None
            res_body = resp.read().decode("utf-8")
            res_json = json.loads(res_body)
            raw_response = res_json.get("response", "").strip()
            return json.loads(raw_response)
    except Exception as e:
        print(f"[OLLAMA AI NOTICE] Call skipped or returned invalid output: {e}")
        return None


def generate_path_plan(
    weakest_skill: str,
    current_level: str,
    target_level: str,
    lang_code: str = "en"
) -> Optional[List[Dict[str, Any]]]:
    """
    Generates a 3-5 lesson sequence plan tailored to the learner's weakest skill.

    :return: List of dicts with keys: 'title', 'difficulty_level', 'focus_area', or None on fallback.
    """
    system_prompt = (
        "You are an AI literacy curriculum designer for adult and neo-learners. "
        "Respond ONLY with a JSON array containing 3 to 5 lesson objects."
    )

    prompt = f"""
    Create an adaptive learning path sequence for a learner learning in language code '{lang_code}'.
    Learner's Weakest Skill: {weakest_skill}
    Current Proficiency Level: {current_level}
    Target Proficiency Level: {target_level}

    Return a JSON array of objects with the following keys:
    - "title": Descriptive lesson title in target language or English.
    - "difficulty_level": "{current_level}" or "FUNCTIONAL" or "{target_level}".
    - "focus_area": Short focus description.

    Example output format:
    [
      {{"title": "Basic Vowel Articulation", "difficulty_level": "FOUNDATIONAL", "focus_area": "Phonemes"}},
      {{"title": "Everyday Words & Spelling", "difficulty_level": "FUNCTIONAL", "focus_area": "Vocabulary"}}
    ]
    """

    res = _query_ollama_json(prompt, system_prompt)
    if isinstance(res, list) and len(res) >= 1:
        return res
    elif isinstance(res, dict) and "lessons" in res and isinstance(res["lessons"], list):
        return res["lessons"]

    return None


def generate_lesson_content(
    lesson_title: str,
    skill_type: str,
    lang_code: str = "en",
    target_level: str = "FOUNDATIONAL"
) -> Optional[Dict[str, Any]]:
    """
    Generates rich reading passage, phonetic breakdown, and target text for a lesson.
    """
    system_prompt = (
        "You are a multilingual literacy content generator. "
        "Respond ONLY with a JSON object."
    )

    prompt = f"""
    Generate lesson reading content for:
    Title: {lesson_title}
    Skill Type: {skill_type}
    Language: {lang_code}
    Target Level: {target_level}

    Return JSON with keys:
    - "target_text": A clear 1-2 sentence practice passage in language '{lang_code}'.
    - "phonetic_script": JSON array string of syllables/phonemes.
    - "content_url": Audio asset path string like "/audio/{lang_code}/generated_lesson.mp3".
    """

    res = _query_ollama_json(prompt, system_prompt)
    if isinstance(res, dict) and "target_text" in res:
        return res

    return None
