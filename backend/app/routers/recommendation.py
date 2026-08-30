"""
Recommendation Router — Phase 4: AI-Powered Recommendation & Exercise Generator
Provides personalized learning recommendations and custom AI-generated exercises.
"""
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_current_learner, get_optional_current_learner
from app.services.ai_course_generator import ai_course_generator
from typing import Optional

router = APIRouter(prefix="/api/recommendations", tags=["AI Recommendations & Course Generator"])


@router.get("/ai-status")
async def get_ai_status():
    """
    Returns the current AI provider status. No authentication required.
    Useful for debugging and showing the AI badge in the frontend.
    """
    provider_info = ai_course_generator.get_active_provider()
    return {
        "ai_enabled": ai_course_generator.ai_enabled,
        "provider": provider_info["provider"],
        "model": provider_info["model"],
        "status": provider_info["status"],
        "fallback_available": True  # Rule-based fallback is always available
    }


@router.get("")
async def get_recommendations(
    current_learner: models.Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """
    Returns top 3 AI-powered learning recommendations for the authenticated learner.
    Uses the learner's profile scores and progress data to personalize recommendations.
    Results are cached in the Recommendation table.
    """
    learner_id = current_learner.learner_id

    # 1. Fetch learner profile
    profile = db.query(models.LearnerProfile).filter(
        models.LearnerProfile.learner_id == learner_id
    ).first()

    # 2. Get language info
    lang_code = "en"
    if current_learner.current_lang_id:
        lang = db.query(models.Language).filter(
            models.Language.lang_id == current_learner.current_lang_id
        ).first()
        if lang:
            lang_code = lang.iso_code

    # 3. Count lesson progress
    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == learner_id
    ).first()

    completed_lessons = 0
    total_lessons = 0
    if path:
        path_lessons = db.query(models.PathLesson).filter(
            models.PathLesson.path_id == path.path_id
        ).all()
        total_lessons = len(path_lessons)
        completed_lessons = sum(1 for pl in path_lessons if pl.status == "COMPLETED")

    # 4. Build profile data for AI
    profile_data = {
        "language": lang_code,
        "literacy_level": profile.literacy_level if profile else "FOUNDATIONAL",
        "reading_pct": profile.reading_pct if profile else 0.0,
        "comprehension_pct": profile.comprehension_pct if profile else 0.0,
        "voice_pct": profile.voice_pct if profile else 0.0,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons
    }

    # 5. Generate recommendations via AI service
    recommendations, provider_used = await ai_course_generator.generate_recommendations(profile_data)

    # 6. Persist to Recommendation table (replace old ones)
    db.query(models.Recommendation).filter(
        models.Recommendation.learner_id == learner_id
    ).delete()

    for rec in recommendations:
        db_rec = models.Recommendation(
            learner_id=learner_id,
            lesson_id=None,
            reason=rec.get("reason", ""),
            model_version=f"{provider_used}-{ai_course_generator.groq_model if provider_used == 'groq' else ai_course_generator.ollama_model if provider_used == 'ollama' else 'static'}",
            priority=rec.get("priority", "MEDIUM"),
            skill_focus=rec.get("skill_focus", "READING"),
            rec_type=rec.get("type", "practice_weak_area"),
            title=rec.get("title", "Recommendation")
        )
        db.add(db_rec)

    db.commit()

    return {
        "recommendations": recommendations,
        "ai_provider": provider_used,
        "model": ai_course_generator.groq_model if provider_used == "groq" else ai_course_generator.ollama_model if provider_used == "ollama" else None,
        "learner_profile": profile_data
    }


@router.post("/generate-exercise")
async def generate_exercise(
    payload: dict = Body(...),
    current_learner: models.Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """
    Generate a custom AI exercise for a specific skill area and difficulty level.
    
    Expected payload:
    {
        "skill_type": "READING" | "COMPREHENSION" | "VOICE",
        "difficulty_level": "FOUNDATIONAL" | "FUNCTIONAL" | "PROFICIENT"
    }
    """
    skill_type = payload.get("skill_type", "READING").upper()
    difficulty = payload.get("difficulty_level", "FOUNDATIONAL").upper()
    force_new = payload.get("force_new", False)
    learner_id = current_learner.learner_id

    if skill_type not in ("READING", "COMPREHENSION", "VOICE"):
        raise HTTPException(status_code=400, detail="Invalid skill_type. Use READING, COMPREHENSION, or VOICE.")
    if difficulty not in ("FOUNDATIONAL", "FUNCTIONAL", "PROFICIENT"):
        raise HTTPException(status_code=400, detail="Invalid difficulty_level. Use FOUNDATIONAL, FUNCTIONAL, or PROFICIENT.")

    # Get learner language
    lang_code = "en"
    if current_learner.current_lang_id:
        lang = db.query(models.Language).filter(
            models.Language.lang_id == current_learner.current_lang_id
        ).first()
        if lang:
            lang_code = lang.iso_code

    # Check for recently cached exercise (within 24h) unless force_new requested
    if not force_new:
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        cached = db.query(models.AIGeneratedContent).filter(
            models.AIGeneratedContent.learner_id == learner_id,
            models.AIGeneratedContent.language_code == lang_code,
            models.AIGeneratedContent.skill_type == skill_type,
            models.AIGeneratedContent.difficulty_level == difficulty,
            models.AIGeneratedContent.generated_at >= recent_cutoff
        ).first()

        if cached:
            return {
                "exercise": json.loads(cached.content_json),
                "ai_provider": cached.generated_by,
                "cached": True,
                "content_id": cached.content_id
            }

    # Get existing lesson titles to avoid duplicates
    existing_titles = []
    completed_lessons = db.query(models.PathLesson).join(models.LearningPath).filter(
        models.LearningPath.learner_id == learner_id,
        models.PathLesson.status == "COMPLETED"
    ).all()
    for pl in completed_lessons:
        if pl.lesson:
            existing_titles.append(pl.lesson.title)

    # Generate new exercise via AI
    exercise, provider_used = await ai_course_generator.generate_exercise(
        language=lang_code,
        skill_type=skill_type,
        difficulty=difficulty,
        existing_titles=existing_titles
    )

    # Save to database
    ai_content = models.AIGeneratedContent(
        learner_id=learner_id,
        language_code=lang_code,
        skill_type=skill_type,
        difficulty_level=difficulty,
        title=exercise.get("title", f"{skill_type} Exercise"),
        content_json=json.dumps(exercise, ensure_ascii=False),
        generated_by=provider_used
    )
    db.add(ai_content)
    db.commit()
    db.refresh(ai_content)

    return {
        "exercise": exercise,
        "ai_provider": provider_used,
        "cached": False,
        "content_id": ai_content.content_id
    }


@router.get("/history")
async def get_generated_content_history(
    current_learner: models.Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """Returns all AI-generated exercises for this learner."""
    contents = db.query(models.AIGeneratedContent).filter(
        models.AIGeneratedContent.learner_id == current_learner.learner_id
    ).order_by(models.AIGeneratedContent.generated_at.desc()).limit(20).all()

    return {
        "exercises": [
            {
                "content_id": c.content_id,
                "title": c.title,
                "language_code": c.language_code,
                "skill_type": c.skill_type,
                "difficulty_level": c.difficulty_level,
                "generated_by": c.generated_by,
                "generated_at": c.generated_at.isoformat() if c.generated_at else None,
                "exercise": json.loads(c.content_json)
            }
            for c in contents
        ],
        "total": len(contents)
    }


@router.get("/pytorch-predictions")
async def get_pytorch_neural_predictions(
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Returns deep neural network predictions from PyTorch AI Engine:
    - Learner Multi-Skill Proficiency Level & Composite Score
    - Handwriting Quality & Guideline Discipline Tier
    - Phoneme Accuracy & Speech Fluency Index
    """
    from app.services.pytorch_ai_engine import PyTorchAIEngine
    pytorch_engine = PyTorchAIEngine()

    # Determine learner profile metrics or use default foundational benchmark
    lid = current_learner.learner_id if current_learner else 1
    features = [70.0, 75.0, 65.0, 60.0, 85.0, 80.0, 50.0]

    if current_learner:
        profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == lid).first()
        if profile:
            features = [
                float(profile.reading_score or 50.0),
                float(profile.word_formation_score or 50.0),
                float(profile.grammar_score or 50.0),
                float(profile.literature_score or 50.0),
                85.0,
                80.0,
                50.0
            ]

    prof_res = pytorch_engine.predict_learner_proficiency(features)
    hw_res = pytorch_engine.evaluate_handwriting_strokes([88.0, 82.0, 75.0, 8.0, 42.0, 0.0])
    speech_res = pytorch_engine.evaluate_pronunciation_audio([0.88, 14.0, 62.0, 0.07, 125.0])

    return {
        "engine": "PyTorch Deep Learning Engine v2.13",
        "status": "ACTIVE",
        "learner_id": lid,
        "proficiency_classification": prof_res,
        "handwriting_evaluation": hw_res,
        "pronunciation_evaluation": speech_res
    }
