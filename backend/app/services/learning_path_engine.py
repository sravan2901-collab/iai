"""
Learning Path Engine Service for AksharAI Language Literacy Platform.

Generates personalized learning_path and path_lesson sequences for learners
based on their predicted proficiency per skill type.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app import models
from app.services.proficiency_engine import (
    predict_proficiency,
    normalize_skill_type,
    CANONICAL_SKILL_TYPES,
)

# Proficiency level ordering from lowest to highest
LEVEL_ORDER = {
    "FOUNDATIONAL": 0,
    "BASIC": 1,
    "INTERMEDIATE": 2,
    "ADVANCED": 3,
}

# Next level mapping for progressive literacy goals
LEVEL_NEXT = {
    "FOUNDATIONAL": "BASIC",
    "BASIC": "INTERMEDIATE",
    "INTERMEDIATE": "ADVANCED",
    "ADVANCED": "ADVANCED",
}

# Difficulty ordering for sorting lessons
DIFFICULTY_ORDER = {
    "FOUNDATIONAL": 1,
    "BASIC": 2,
    "FUNCTIONAL": 2,
    "INTERMEDIATE": 3,
    "PROFICIENT": 4,
    "ADVANCED": 5,
}


def generate_learning_path(learner_id: int, db: Optional[Session] = None) -> int:
    """
    Generates a new personalized learning_path and path_lesson sequence for a learner:
    1. Calls predict_proficiency(learner_id) to get predicted proficiency per skill.
    2. Identifies the learner's weakest skill_type.
    3. Deactivates any existing ACTIVE learning_path by setting status = 'COMPLETED'.
    4. Inserts a new ACTIVE learning_path with current_level = weakest level and
       target_proficiency = next level up.
    5. Selects up to 5 matching lessons for the weakest skill_type, ordered by difficulty.
    6. Inserts path_lesson entries with sequence_no 1..5, status = 'UNLOCKED' for the
       first lesson and 'LOCKED' for subsequent lessons.

    :param learner_id: Unique integer ID of the learner.
    :param db: Optional SQLAlchemy Session. If omitted, uses SessionLocal context.
    :return: Unique path_id integer of the newly generated learning_path.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # 1. Predict learner's proficiency across all skills
        predictions = predict_proficiency(learner_id, db=db)

        # 2. Determine weakest skill_type
        # Sort by level rank ascending; tiebreak by canonical order
        weakest_skill = min(
            CANONICAL_SKILL_TYPES,
            key=lambda s: LEVEL_ORDER.get(predictions.get(s, "FOUNDATIONAL"), 0)
        )
        weakest_level = predictions.get(weakest_skill, "FOUNDATIONAL")
        target_level = LEVEL_NEXT.get(weakest_level, "BASIC")

        # 3. Complete any existing ACTIVE learning paths for this learner
        active_paths = (
            db.query(models.LearningPath)
            .filter(
                models.LearningPath.learner_id == learner_id,
                models.LearningPath.status == "ACTIVE"
            )
            .all()
        )
        for ap in active_paths:
            ap.status = "COMPLETED"
        db.commit()

        # 4. Insert new ACTIVE learning_path
        new_path = models.LearningPath(
            learner_id=learner_id,
            target_proficiency=target_level,
            current_level=weakest_level,
            completion_percentage=0.0,
            status="ACTIVE",
            generated_on=datetime.now(timezone.utc)
        )
        db.add(new_path)
        db.commit()
        db.refresh(new_path)

        # 5. Fetch learner and current language
        learner = db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
        lang_id = learner.current_lang_id if (learner and learner.current_lang_id) else 2  # Default to English (2)

        curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang_id).first()

        candidate_lessons: List[models.Lesson] = []
        if curriculum:
            # Query modules under curriculum matching weakest skill type
            modules = (
                db.query(models.Module)
                .filter(models.Module.curriculum_id == curriculum.curriculum_id)
                .all()
            )

            target_modules = [
                m for m in modules
                if normalize_skill_type(m.skill_type) == weakest_skill
            ]

            if not target_modules:
                target_modules = modules  # Fallback to all modules if specific skill module missing

            for mod in target_modules:
                mod_lessons = (
                    db.query(models.Lesson)
                    .filter(models.Lesson.module_id == mod.module_id)
                    .all()
                )
                candidate_lessons.extend(mod_lessons)

        # Sort candidate lessons by difficulty level ascending
        candidate_lessons.sort(
            key=lambda l: DIFFICULTY_ORDER.get((l.difficulty_level or "").upper(), 99)
        )

        # Take top 5 lessons
        selected_lessons = candidate_lessons[:5]

        # 6. Insert path_lesson rows
        for idx, lesson_obj in enumerate(selected_lessons):
            seq_no = idx + 1
            lesson_status = "UNLOCKED" if seq_no == 1 else "LOCKED"

            pl = models.PathLesson(
                path_id=new_path.path_id,
                lesson_id=lesson_obj.lesson_id,
                sequence_no=seq_no,
                status=lesson_status
            )
            db.add(pl)

        db.commit()
        return new_path.path_id

    finally:
        if close_db:
            db.close()


def get_active_path(learner_id: int, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves the current ACTIVE learning_path for a learner along with its ordered path_lesson list
    (joined with lesson details: title, content_type, difficulty_level, etc.).

    :param learner_id: Unique integer ID of the learner.
    :param db: Optional SQLAlchemy Session. If omitted, uses SessionLocal context.
    :return: Dictionary representation of active learning_path or None if no active path exists.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        active_path = (
            db.query(models.LearningPath)
            .filter(
                models.LearningPath.learner_id == learner_id,
                models.LearningPath.status == "ACTIVE"
            )
            .order_by(desc(models.LearningPath.path_id))
            .first()
        )

        if not active_path:
            return None

        # Query path_lesson entries joined with lesson
        path_lessons_query = (
            db.query(models.PathLesson, models.Lesson)
            .join(models.Lesson, models.PathLesson.lesson_id == models.Lesson.lesson_id)
            .filter(models.PathLesson.path_id == active_path.path_id)
            .order_by(models.PathLesson.sequence_no)
            .all()
        )

        ordered_lessons = []
        for pl, l in path_lessons_query:
            ordered_lessons.append({
                "path_lesson_id": pl.path_lesson_id,
                "lesson_id": l.lesson_id,
                "sequence_no": pl.sequence_no,
                "status": pl.status,
                "title": l.title,
                "content_type": l.content_type,
                "difficulty_level": l.difficulty_level,
                "target_text": l.target_text,
                "content_url": l.content_url
            })

        return {
            "path_id": active_path.path_id,
            "learner_id": active_path.learner_id,
            "target_proficiency": active_path.target_proficiency,
            "current_level": active_path.current_level,
            "status": active_path.status,
            "completion_percentage": float(active_path.completion_percentage or 0.0),
            "generated_on": active_path.generated_on.isoformat() if active_path.generated_on else None,
            "path_lessons": ordered_lessons
        }

    finally:
        if close_db:
            db.close()
