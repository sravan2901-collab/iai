"""
Progress Tracking Router — Phase 3: Progress-Driven Re-Planning System
Handles lesson completion tracking, dashboard aggregation, and progress analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from typing import Optional

router = APIRouter(prefix="/api/progress", tags=["Progress Tracking & Dashboard"])


@router.get("/dashboard")
async def get_progress_dashboard(
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated progress dashboard data for the authenticated learner.
    Includes: skill scores, completion stats, recent activity, streak info.
    """
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    learner_id = current_learner.learner_id
    profile = db.query(models.LearnerProfile).filter(
        models.LearnerProfile.learner_id == learner_id
    ).first()

    # Get active learning path
    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == learner_id
    ).first()

    # Count path lesson stats
    total_lessons = 0
    completed_lessons = 0
    unlocked_lessons = 0
    in_progress_lessons = 0
    locked_lessons = 0

    if path:
        path_lessons = db.query(models.PathLesson).filter(
            models.PathLesson.path_id == path.path_id
        ).all()
        total_lessons = len(path_lessons)
        completed_lessons = sum(1 for pl in path_lessons if pl.status == "COMPLETED")
        unlocked_lessons = sum(1 for pl in path_lessons if pl.status == "UNLOCKED")
        in_progress_lessons = sum(1 for pl in path_lessons if pl.status == "IN_PROGRESS")
        locked_lessons = sum(1 for pl in path_lessons if pl.status == "LOCKED")

    # Get module-level progress from ProgressTracking
    module_progress = []
    progress_entries = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.learner_id == learner_id
    ).all()

    for prog in progress_entries:
        module = db.query(models.Module).filter(
            models.Module.module_id == prog.module_id
        ).first()
        if module:
            module_progress.append({
                "module_id": module.module_id,
                "module_name": module.module_name,
                "skill_type": module.skill_type,
                "completion_percent": prog.completion_percent,
                "time_spent_min": prog.time_spent_min
            })

    # Get recent pronunciation scores with actual model field names
    recent_scores = db.query(models.PronunciationScore).join(
        models.VoiceSession
    ).filter(
        models.VoiceSession.learner_id == learner_id
    ).order_by(
        models.PronunciationScore.score_id.desc()
    ).limit(10).all()

    voice_history = []
    for s in recent_scores:
        voice_history.append({
            "score_id": s.score_id,
            "overall_score": s.overall_score,
            "phoneme_accuracy": s.phoneme_accuracy,
            "syllable_score": s.syllable_score,
            "recognized_text": s.recognized_text,
            "created_at": str(s.created_at) if hasattr(s, "created_at") and s.created_at else None
        })

    # Query earned achievements
    earned_achievements = db.query(models.LearnerAchievement).join(
        models.Achievement
    ).filter(
        models.LearnerAchievement.learner_id == learner_id
    ).order_by(
        models.LearnerAchievement.earned_on.desc()
    ).all()

    achievements_list = []
    for la in earned_achievements:
        achievements_list.append({
            "achievement_id": la.achievement.achievement_id if la.achievement else la.achievement_id,
            "achievement_name": la.achievement.achievement_name if la.achievement else "Badge",
            "description": la.achievement.description if la.achievement else "",
            "criteria": la.achievement.criteria if la.achievement else "",
            "earned_on": str(la.earned_on) if la.earned_on else None
        })

    # Calculate total time spent
    total_time_min = sum(p.time_spent_min or 0 for p in progress_entries)

    # Get language info
    lang_name = "English"
    if current_learner.current_lang_id:
        lang = db.query(models.Language).filter(
            models.Language.lang_id == current_learner.current_lang_id
        ).first()
        if lang:
            lang_name = lang.lang_name

    # Determine learner display name
    learner_name = current_learner.username if hasattr(current_learner, "username") else "Learner"
    if profile and (profile.first_name or profile.last_name):
        learner_name = f"{profile.first_name or ''} {profile.last_name or ''}".strip()

    streak_count = profile.streak_count if profile and profile.streak_count is not None else 0
    total_points = profile.total_points if profile and profile.total_points is not None else 0

    return {
        "learner_id": learner_id,
        "learner_name": learner_name,
        "language": lang_name,
        "streak_count": streak_count,
        "total_points": total_points,
        "profile": {
            "literacy_level": profile.literacy_level if profile else "FOUNDATIONAL",
            "reading_pct": profile.reading_pct if profile else 0.0,
            "comprehension_pct": profile.comprehension_pct if profile else 0.0,
            "voice_pct": profile.voice_pct if profile else 0.0,
            "overall_pct": round(
                ((profile.reading_pct or 0) + (profile.comprehension_pct or 0) + (profile.voice_pct or 0)) / 3, 1
            ) if profile else 0.0,
            "streak_count": streak_count,
            "total_points": total_points
        },
        "path_stats": {
            "path_id": path.path_id if path else None,
            "current_level": path.current_level if path else "FOUNDATIONAL",
            "completion_percentage": path.completion_percentage if path else 0.0,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "unlocked_lessons": unlocked_lessons,
            "in_progress_lessons": in_progress_lessons,
            "locked_lessons": locked_lessons
        },
        "module_progress": module_progress,
        "voice_history": voice_history,
        "achievements": achievements_list,
        "total_time_spent_min": total_time_min,
        "lessons_completed_today": completed_lessons
    }


@router.post("/complete-lesson")
async def complete_lesson(
    payload: dict = Body(...),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Called when a learner completes a lesson (e.g., finishes voice practice).
    Triggers the complete_lesson_workflow from learning_path.py.
    
    Expected payload:
    {
        "lesson_id": int,
        "score": float (0-100),
        "path_lesson_id": int (optional)
    }
    """
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    lesson_id = payload.get("lesson_id")
    score = payload.get("score", 100.0)
    path_lesson_id = payload.get("path_lesson_id")

    if not lesson_id:
        raise HTTPException(status_code=400, detail="lesson_id is required")

    # Import the workflow function from learning_path router
    from app.routers.learning_path import complete_lesson_workflow

    result = complete_lesson_workflow(
        learner_id=current_learner.learner_id,
        lesson_id=lesson_id,
        score=score,
        db=db
    )

    if not result:
        raise HTTPException(status_code=404, detail="Lesson or learning path not found")

    return {
        "message": "Lesson completed successfully!",
        "result": result,
        "achievements_unlocked": result.get("achievements_unlocked", []) if isinstance(result, dict) else []
    }


@router.get("/module/{module_id}")
async def get_module_progress(
    module_id: int,
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """Returns detailed progress for a specific module."""
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    module = db.query(models.Module).filter(models.Module.module_id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get all lessons in this module
    lessons = db.query(models.Lesson).filter(models.Lesson.module_id == module_id).all()

    # Get path lessons for status
    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == current_learner.learner_id
    ).first()

    lesson_details = []
    for lesson in lessons:
        path_lesson = None
        if path:
            path_lesson = db.query(models.PathLesson).filter(
                models.PathLesson.path_id == path.path_id,
                models.PathLesson.lesson_id == lesson.lesson_id
            ).first()

        lesson_details.append({
            "lesson_id": lesson.lesson_id,
            "title": lesson.title,
            "content_type": lesson.content_type,
            "difficulty_level": lesson.difficulty_level,
            "status": path_lesson.status if path_lesson else "LOCKED",
            "path_lesson_id": path_lesson.path_lesson_id if path_lesson else None
        })

    # Get progress tracking entry
    prog = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.learner_id == current_learner.learner_id,
        models.ProgressTracking.module_id == module_id
    ).first()

    return {
        "module_id": module.module_id,
        "module_name": module.module_name,
        "skill_type": module.skill_type,
        "completion_percent": prog.completion_percent if prog else 0.0,
        "time_spent_min": prog.time_spent_min if prog else 0,
        "total_lessons": len(lessons),
        "completed_lessons": sum(1 for l in lesson_details if l["status"] == "COMPLETED"),
        "lessons": lesson_details
    }


@router.get("/history")
async def get_learning_history(
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """Returns the learner's complete learning history — completed lessons with scores."""
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == current_learner.learner_id
    ).first()

    if not path:
        return {"history": [], "total_completed": 0}

    completed_path_lessons = db.query(models.PathLesson).filter(
        models.PathLesson.path_id == path.path_id,
        models.PathLesson.status == "COMPLETED"
    ).order_by(models.PathLesson.sequence_no).all()

    history = []
    for pl in completed_path_lessons:
        lesson = pl.lesson
        module = lesson.module if lesson else None
        history.append({
            "path_lesson_id": pl.path_lesson_id,
            "lesson_id": lesson.lesson_id,
            "lesson_title": lesson.title,
            "content_type": lesson.content_type,
            "module_name": module.module_name if module else "Unknown",
            "skill_type": module.skill_type if module else "Unknown",
            "sequence_no": pl.sequence_no
        })

    return {
        "history": history,
        "total_completed": len(history),
        "path_completion": path.completion_percentage,
        "current_level": path.current_level
    }
