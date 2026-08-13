"""
Recommendation Engine Service for AksharAI Language Literacy Platform.

Rule-based recommendation system that populates the recommendation table with lesson
suggestions for a learner ("you might also like / keep practicing" surface), separate
from their formal learning_path.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app import models
from app.services.proficiency_engine import (
    get_learner_scores,
    predict_proficiency,
    normalize_skill_type,
    CANONICAL_SKILL_TYPES,
)


def generate_recommendations(
    learner_id: int,
    limit: int = 3,
    db: Optional[Session] = None
) -> List[int]:
    """
    Generates up to `limit` rule-based lesson recommendations for a learner:
    1. Fetches learner's score map and proficiency map via proficiency_engine.
    2. Identifies skills where the learner scored in the bottom half of their benchmark range
       (or skills requiring reinforcement).
    3. Excludes lessons the learner has already completed (via path_lesson status or progress_tracking).
    4. Inserts new rows into the recommendation table with reason and model_version = 'rule-based-v1'.

    :param learner_id: Unique integer ID of the learner.
    :param limit: Maximum number of recommendations to generate (default: 3).
    :param db: Optional SQLAlchemy Session. If omitted, uses SessionLocal context.
    :return: List of new recommendation_id integers inserted into the database.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # 1. Fetch learner scores and proficiency map
        scores = get_learner_scores(learner_id, db=db)
        predictions = predict_proficiency(learner_id, db=db)

        # Fetch benchmarks from DB to determine exact score range midpoints
        benchmarks = db.query(models.ProficiencyBenchmark).all()
        benchmark_map: Dict[tuple[str, str], models.ProficiencyBenchmark] = {}
        for b in benchmarks:
            key = (normalize_skill_type(b.skill_type), b.level_name.upper())
            benchmark_map[key] = b

        # 2. Evaluate skill candidates needing reinforcement (bottom half of benchmark range)
        skill_evaluations = []
        for skill in CANONICAL_SKILL_TYPES:
            score = scores.get(skill, 0.0)
            level = predictions.get(skill, "FOUNDATIONAL")
            bench = benchmark_map.get((skill, level.upper()))

            if bench:
                min_s = float(bench.min_score)
                max_s = float(bench.max_score)
            else:
                # Default benchmark ranges if row not found
                ranges = {
                    "FOUNDATIONAL": (0.0, 40.0),
                    "BASIC": (41.0, 60.0),
                    "INTERMEDIATE": (61.0, 80.0),
                    "ADVANCED": (81.0, 100.0),
                }
                min_s, max_s = ranges.get(level.upper(), (0.0, 40.0))

            range_span = max(1.0, max_s - min_s)
            ratio = (score - min_s) / range_span
            midpoint = min_s + (range_span / 2.0)
            is_bottom_half = (score <= midpoint)

            skill_evaluations.append({
                "skill_type": skill,
                "score": score,
                "level": level,
                "ratio": ratio,
                "is_bottom_half": is_bottom_half
            })

        # Filter candidates: prioritize skills in the bottom half of their benchmark range
        candidates = [s for s in skill_evaluations if s["is_bottom_half"]]
        if not candidates:
            # If all skills are in top half, fallback to all skills ordered by lowest benchmark ratio
            candidates = skill_evaluations

        # Sort candidate skills by score ratio ascending (weakest / lowest relative score first)
        candidates.sort(key=lambda s: (s["ratio"], s["score"]))

        # 3. Identify completed lessons for this learner
        completed_lesson_ids: Set[int] = set()

        # Check path_lesson status = 'COMPLETED' for this learner
        completed_path_lessons = (
            db.query(models.PathLesson.lesson_id)
            .join(models.LearningPath, models.PathLesson.path_id == models.LearningPath.path_id)
            .filter(
                models.LearningPath.learner_id == learner_id,
                models.PathLesson.status == "COMPLETED"
            )
            .all()
        )
        for row in completed_path_lessons:
            completed_lesson_ids.add(row[0])

        # Check progress_tracking completion_percent >= 100.0
        completed_modules = (
            db.query(models.ProgressTracking.module_id)
            .filter(
                models.ProgressTracking.learner_id == learner_id,
                models.ProgressTracking.completion_percent >= 100.0
            )
            .all()
        )
        if completed_modules:
            comp_mod_ids = [m[0] for m in completed_modules]
            mod_lessons = (
                db.query(models.Lesson.lesson_id)
                .filter(models.Lesson.module_id.in_(comp_mod_ids))
                .all()
            )
            for row in mod_lessons:
                completed_lesson_ids.add(row[0])

        # Check existing recommendations for this learner to avoid duplicate active suggestions
        existing_recs = (
            db.query(models.Recommendation.lesson_id)
            .filter(models.Recommendation.learner_id == learner_id)
            .all()
        )
        existing_rec_lesson_ids = {r[0] for r in existing_recs}

        # 4. Fetch learner and current language
        learner = db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
        lang_id = learner.current_lang_id if (learner and learner.current_lang_id) else 2

        curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang_id).first()
        curr_id = curriculum.curriculum_id if curriculum else None

        new_rec_ids: List[int] = []

        # 5. Select lessons for candidate skills
        for candidate in candidates:
            if len(new_rec_ids) >= limit:
                break

            target_skill = candidate["skill_type"]
            score_val = candidate["score"]

            # Query candidate lessons for target skill in learner's curriculum
            lesson_query = (
                db.query(models.Lesson)
                .join(models.Module, models.Lesson.module_id == models.Module.module_id)
            )

            if curr_id:
                lesson_query = lesson_query.filter(models.Module.curriculum_id == curr_id)

            lessons = lesson_query.all()

            # Filter for lessons matching target_skill and not completed/recommended
            eligible_lessons = [
                l for l in lessons
                if normalize_skill_type(l.module.skill_type) == target_skill
                and l.lesson_id not in completed_lesson_ids
                and l.lesson_id not in existing_rec_lesson_ids
            ]

            # If no unrecommended lesson in specific module, loosen existing recommendation filter
            if not eligible_lessons:
                eligible_lessons = [
                    l for l in lessons
                    if normalize_skill_type(l.module.skill_type) == target_skill
                    and l.lesson_id not in completed_lesson_ids
                ]

            for l_obj in eligible_lessons:
                if len(new_rec_ids) >= limit:
                    break

                reason_str = (
                    f"Reinforce {target_skill} — recent score {int(score_val)}%"
                    if score_val > 0.0
                    else f"Reinforce {target_skill} — foundational practice needed"
                )

                new_rec = models.Recommendation(
                    learner_id=learner_id,
                    lesson_id=l_obj.lesson_id,
                    reason=reason_str,
                    model_version="rule-based-v1",
                    recommended_on=datetime.now(timezone.utc)
                )
                db.add(new_rec)
                db.commit()
                db.refresh(new_rec)

                new_rec_ids.append(new_rec.recommendation_id)
                existing_rec_lesson_ids.add(l_obj.lesson_id)

        return new_rec_ids

    finally:
        if close_db:
            db.close()


def get_recommendations(
    learner_id: int,
    limit: int = 3,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """
    Returns the learner's most recent `limit` recommendations with joined lesson title,
    content_type, difficulty_level, and reason.

    :param learner_id: Unique integer ID of the learner.
    :param limit: Maximum number of recent recommendations to retrieve (default: 3).
    :param db: Optional SQLAlchemy Session. If omitted, uses SessionLocal context.
    :return: List of dictionary representations of recommendations with joined lesson data.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        recs_query = (
            db.query(models.Recommendation, models.Lesson)
            .join(models.Lesson, models.Recommendation.lesson_id == models.Lesson.lesson_id)
            .filter(models.Recommendation.learner_id == learner_id)
            .order_by(desc(models.Recommendation.recommendation_id))
            .limit(limit)
            .all()
        )

        results = []
        for rec, l in recs_query:
            results.append({
                "recommendation_id": rec.recommendation_id,
                "learner_id": rec.learner_id,
                "lesson_id": rec.lesson_id,
                "reason": rec.reason,
                "model_version": rec.model_version,
                "recommended_on": rec.recommended_on.isoformat() if rec.recommended_on else None,
                "title": l.title,
                "content_type": l.content_type,
                "difficulty_level": l.difficulty_level,
                "target_text": l.target_text,
                "content_url": l.content_url
            })

        return results

    finally:
        if close_db:
            db.close()
