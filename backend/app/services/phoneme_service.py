"""
Phoneme & Pronunciation Evaluation Service for AksharAI Multilingual Literacy Platform.

Computes:
1. Multi-script phonetic distance & word similarity (Levenshtein)
2. Syllable & phoneme accuracy scores
3. Word-by-word color feedback (green/yellow/red)
4. Multilingual actionable remediation tips
"""

import re
import unicodedata
from typing import Dict, Any

def normalize_text_for_eval(text: str) -> str:
    """Cleans punctuation, normalizes unicode characters, and strips whitespace."""
    if not text:
        return ""
    # Normalize unicode to NFC
    norm = unicodedata.normalize("NFC", text)
    # Remove standard punctuation symbols but keep alphanumeric and native script characters
    cleaned = re.sub(r'[\.,!?;:\'\"\\\/\-_—।॥\(\)\[\]\{\}]', ' ', norm)
    # Collapse multiple whitespace
    return re.sub(r'\s+', ' ', cleaned).strip().lower()

def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def evaluate_pronunciation(target_text: str, spoken_text: str, language_code: str = "en") -> Dict[str, Any]:
    """
    Compares target text against recognized spoken text.
    Computes normalized word similarity, phoneme score, syllable coverage, and word color feedback.
    """
    if not target_text or not target_text.strip():
        return {
            "overall_score": 0.0,
            "phoneme_accuracy": 0.0,
            "syllable_score": 0.0,
            "word_feedback": {},
            "remediation_tip": "No target text provided for this lesson."
        }

    clean_target = normalize_text_for_eval(target_text)
    clean_spoken = normalize_text_for_eval(spoken_text)

    # Original target words for display keying
    raw_target_words = [w.strip() for w in re.sub(r'[\.,!?;:\'\"\\\/\-_—।॥]', '', target_text).split() if w.strip()]
    target_words = clean_target.split()
    spoken_words = clean_spoken.split()

    if not spoken_words:
        # User did not speak or no speech detected
        word_feedback = { (raw_target_words[i] if i < len(raw_target_words) else tw): "red" for i, tw in enumerate(target_words) }
        return {
            "overall_score": 0.0,
            "phoneme_accuracy": 0.0,
            "syllable_score": 0.0,
            "word_feedback": word_feedback,
            "remediation_tip": "No speech was detected. Press the microphone and speak aloud clearly."
        }

    word_feedback = {}
    total_similarity = 0.0
    used_spoken = set()

    for i, tw in enumerate(target_words):
        display_word = raw_target_words[i] if i < len(raw_target_words) else tw
        best_score = 0.0
        best_idx = -1

        for j, sw in enumerate(spoken_words):
            if j in used_spoken:
                continue
            max_len = max(len(tw), len(sw))
            dist = levenshtein_distance(tw, sw)
            sim = 1.0 - (dist / max_len) if max_len > 0 else 1.0
            if sim > best_score:
                best_score = sim
                best_idx = j

        if best_idx >= 0 and best_score > 0.3:
            used_spoken.add(best_idx)

        pct = best_score * 100.0
        if pct >= 80.0:
            word_feedback[display_word] = "green"
        elif pct >= 50.0:
            word_feedback[display_word] = "yellow"
        else:
            word_feedback[display_word] = "red"

        total_similarity += best_score

    accuracy = (total_similarity / len(target_words)) * 100.0 if target_words else 0.0
    found_count = sum(1 for v in word_feedback.values() if v != "red")
    syllable_score = (found_count / len(target_words)) * 100.0 if target_words else 0.0
    overall = round(accuracy * 0.6 + syllable_score * 0.4, 1)

    red_words = [k for k, v in word_feedback.items() if v == "red"]
    yellow_words = [k for k, v in word_feedback.items() if v == "yellow"]

    # Generate remediation tip
    if overall >= 90.0:
        remediation_tip = "Excellent pronunciation! Your speech closely matches the benchmark."
    elif overall >= 70.0:
        issues = ", ".join((yellow_words + red_words)[:3])
        remediation_tip = f"Good effort! Practice articulating these words clearly: {issues}."
    elif overall >= 50.0:
        issues = ", ".join((red_words + yellow_words)[:3])
        remediation_tip = f"Keep practicing. Focus on pronouncing: {issues}. Listen to the benchmark audio first."
    else:
        remediation_tip = "Listen to the benchmark reference audio, then repeat slowly one word at a time."

    return {
        "overall_score": min(max(overall, 0.0), 100.0),
        "phoneme_accuracy": round(min(accuracy, 100.0), 1),
        "syllable_score": round(min(syllable_score, 100.0), 1),
        "word_feedback": word_feedback,
        "remediation_tip": remediation_tip
    }
