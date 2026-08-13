from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from app.database import get_db
from app import models, schemas
from app.auth import get_optional_current_learner

router = APIRouter(prefix="/api/recommendations", tags=["AI Personalized Learning Engine (Milestone 2)"])

@router.get("/adaptive-plan", response_model=schemas.AdaptiveRecommendationOut)
def get_adaptive_learning_recommendation(
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    if not profile:
        profile = models.LearnerProfile(
            learner_id=learner.learner_id,
            first_name=learner.username,
            literacy_level="FOUNDATIONAL",
            reading_pct=45.0,
            comprehension_pct=60.0,
            voice_pct=55.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    r_pct = profile.reading_pct or 0.0
    c_pct = profile.comprehension_pct or 0.0
    v_pct = profile.voice_pct or 0.0

    skills = {
        "READING": r_pct,
        "COMPREHENSION": c_pct,
        "VOICE": v_pct
    }

    weakest_skill = min(skills, key=skills.get)
    weakest_score = skills[weakest_skill]

    # Calculate confidence score (higher variance & more assessment data -> higher confidence)
    variance = sum((val - (r_pct + c_pct + v_pct)/3.0)**2 for val in skills.values()) / 3.0
    confidence = round(min(0.98, max(0.65, 0.75 + math.sqrt(variance)/100.0)), 2)

    # Multi-lingual module names based on learner's language
    lang_id = learner.current_lang_id or 1
    lang = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
    iso = lang.iso_code if lang else "en"

    modules = []
    if weakest_skill == "READING":
        modules = [
            {"module_id": 1, "title": "Alphabets, Phonics & Sound Association", "skill_type": "READING", "priority_weight": 0.95},
            {"module_id": 2, "title": "Everyday Greetings & Basic Vocabulary", "skill_type": "READING", "priority_weight": 0.85},
            {"module_id": 3, "title": "Functional Comprehension", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
        ]
        rationale = f"Reading score ({r_pct}%) is below mastery threshold. Recommendation engine prioritized Phonics & Sound association to strengthen letter recognition."
    elif weakest_skill == "COMPREHENSION":
        modules = [
            {"module_id": 1, "title": "ATM & Banking Functional Reading", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
            {"module_id": 2, "title": "Health & Medical Prescription Literacy", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
            {"module_id": 3, "title": "Workplace Dialogue", "skill_type": "VOICE", "priority_weight": 0.65}
        ]
        rationale = f"Comprehension score ({c_pct}%) requires functional context training. Recommendation engine prioritized ATM Banking and Prescription Reading."
    else:
        modules = [
            {"module_id": 1, "title": "Workplace Communication & Professional Greetings", "skill_type": "VOICE", "priority_weight": 0.95},
            {"module_id": 2, "title": "Customer Service Dialogue & Voice Practice", "skill_type": "VOICE", "priority_weight": 0.90},
            {"module_id": 3, "title": "Sentence Grammar", "skill_type": "COMPREHENSION", "priority_weight": 0.55}
        ]
        rationale = f"Voice pronunciation score ({v_pct}%) is the lowest skill. Recommendation engine prioritized Workplace Speech and Customer Service dialogues."

    return {
        "learner_id": learner.learner_id,
        "primary_focus_skill": weakest_skill,
        "confidence_score": confidence,
        "reading_pct": r_pct,
        "comprehension_pct": c_pct,
        "voice_pct": v_pct,
        "recommended_modules": modules,
        "rationale": rationale
    }

@router.get("/predict-proficiency", response_model=schemas.ProficiencyPredictionOut)
def predict_learner_proficiency(
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    current_lvl = profile.literacy_level if profile else "FOUNDATIONAL"
    r_pct = profile.reading_pct if profile else 50.0
    c_pct = profile.comprehension_pct if profile else 50.0
    v_pct = profile.voice_pct if profile else 50.0

    avg_score = (r_pct + c_pct + v_pct) / 3.0

    if current_lvl == "FOUNDATIONAL":
        next_lvl = "FUNCTIONAL"
        days = max(3, int((75.0 - avg_score) * 0.4)) if avg_score < 75.0 else 1
    elif current_lvl == "FUNCTIONAL":
        next_lvl = "PROFICIENT"
        days = max(5, int((90.0 - avg_score) * 0.5)) if avg_score < 90.0 else 2
    else:
        next_lvl = "MASTERY"
        days = 0

    growth_rate = round(min(15.0, max(2.5, (avg_score / 10.0) + (profile.streak_count if profile else 1) * 0.5)), 1)

    return {
        "learner_id": learner.learner_id,
        "current_level": current_lvl,
        "predicted_next_level": next_lvl,
        "estimated_days_to_mastery": days,
        "accuracy_growth_rate": growth_rate,
        "skill_breakdown": {
            "reading": r_pct,
            "comprehension": c_pct,
            "voice": v_pct,
            "composite_average": round(avg_score, 1)
        }
    }

@router.post("/personalized-lessons", response_model=schemas.PersonalizedLessonOut)
def generate_personalized_lesson(
    skill_type: Optional[str] = None,
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    lang_id = learner.current_lang_id or 1
    lang = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
    iso = lang.iso_code if lang else "en"

    if not skill_type:
        skills = {
            "READING": profile.reading_pct or 0.0 if profile else 50.0,
            "COMPREHENSION": profile.comprehension_pct or 0.0 if profile else 50.0,
            "VOICE": profile.voice_pct or 0.0 if profile else 50.0
        }
        skill_type = min(skills, key=skills.get)

    level = profile.literacy_level if profile else "FOUNDATIONAL"

    if skill_type == "READING":
        exercise = {
            "lesson_id": f"gen_read_{learner.learner_id}",
            "target_skill": "READING",
            "language_code": iso,
            "difficulty": level,
            "exercise_type": "PHONICS_FLASHCARD",
            "title": "Adaptive Phonics & Syllable Trainer",
            "instructions": "Listen to the letter sound and select the matching word.",
            "practice_content": [
                {"symbol": "A / அ / अ", "sound_prompt": "apple", "options": ["Apple", "Ball", "Cat"], "correct": "Apple"},
                {"symbol": "B / ಬ / ব", "sound_prompt": "ball", "options": ["Dog", "Ball", "Elephant"], "correct": "Ball"}
            ]
        }
    elif skill_type == "COMPREHENSION":
        exercise = {
            "lesson_id": f"gen_comp_{learner.learner_id}",
            "target_skill": "COMPREHENSION",
            "language_code": iso,
            "difficulty": level,
            "exercise_type": "FUNCTIONAL_CONTEXT_READING",
            "title": "ATM & Financial Literacy Scenario",
            "instructions": "Read the receipt details and answer the comprehension question.",
            "practice_content": [
                {"passage": "ATM Withdrawal Receipt: Amount ₹500, Account XXXX1234, Balance ₹4,500", "question": "What is the remaining account balance?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        }
    else:
        exercise = {
            "lesson_id": f"gen_voice_{learner.learner_id}",
            "target_skill": "VOICE",
            "language_code": iso,
            "difficulty": level,
            "exercise_type": "PRONUNCIATION_COACH",
            "title": "Professional Speech Articulation",
            "instructions": "Tap microphone and speak the prompt phrase clearly.",
            "practice_content": [
                {"prompt_phrase": "Good morning, how can I help you today?", "target_phonemes": ["g", "d", "m", "n", "ng"]}
            ]
        }

    return exercise

@router.get("/recommended-content", response_model=List[schemas.ContentRecommendationOut])
def get_recommended_content(
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    v_pct = profile.voice_pct if profile else 50.0
    r_pct = profile.reading_pct if profile else 50.0

    return [
        {
            "category": "Interactive Speech Coach",
            "title": "Customer Service Dialogue Audio Practice",
            "skill_type": "VOICE",
            "relevance_score": 0.96 if v_pct < 60 else 0.75,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "Hello, welcome to our office."}
        },
        {
            "category": "Functional Literacy Flashcards",
            "title": "Medical Prescription & Pharmacy Signs",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "Health"}
        },
        {
            "category": "Phonics Mastery",
            "title": "Vowel Blends & Consonant Clusters",
            "skill_type": "READING",
            "relevance_score": 0.88 if r_pct < 60 else 0.70,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ]
