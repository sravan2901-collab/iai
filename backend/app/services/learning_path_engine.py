"""
Learning Path Engine Service for AksharAI Language Literacy Platform.

Generates personalized learning_path and path_lesson sequences for learners
based on their predicted proficiency per skill type. Supports dynamic open-source
LLM generation via Ollama (ai_content_service) with immediate fallback to
deterministic rule-based lesson selection.
"""

import json
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
from app.services.ai_content_service import (
    is_ai_available,
    generate_path_plan,
    generate_lesson_content,
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


def generate_learning_path(learner_id: int, target_lang: Optional[str] = None, db: Optional[Session] = None) -> int:
    """
    Generates a new personalized learning_path and path_lesson sequence for a learner:
    1. Calls predict_proficiency(learner_id) to get predicted proficiency per skill.
    2. Identifies the learner's weakest skill_type.
    3. Resolves target language (e.g. 'en', 'hi', 'te', etc.) and updates learner.current_lang_id.
    4. Deactivates any existing ACTIVE learning_path by setting status = 'COMPLETED'.
    5. Inserts a new ACTIVE learning_path with current_level = weakest level and
       target_proficiency = next level up.
    6. Attempts dynamic AI plan generation via Ollama (ai_content_service). If available,
       persists generated lessons. Otherwise, gracefully falls back to rule-based selection.
    7. Inserts path_lesson entries with sequence_no 1..N, status = 'UNLOCKED' for the
       first lesson and 'LOCKED' for subsequent lessons. Guarantees non-empty path.

    :param learner_id: Unique integer ID of the learner.
    :param target_lang: Optional language code ISO string (e.g. 'en', 'hi', 'te', etc.)
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
        weakest_skill = min(
            CANONICAL_SKILL_TYPES,
            key=lambda s: LEVEL_ORDER.get(predictions.get(s, "FOUNDATIONAL"), 0)
        )
        weakest_level = predictions.get(weakest_skill, "FOUNDATIONAL")
        target_level = LEVEL_NEXT.get(weakest_level, "BASIC")

        # 3. Resolve Learner Language
        learner = db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
        
        target_iso = (target_lang or "").strip().lower() if target_lang else None
        lang_obj = None

        if target_iso:
            lang_obj = db.query(models.Language).filter(models.Language.iso_code == target_iso).first()
        
        if not lang_obj and learner and learner.current_lang_id:
            lang_obj = db.query(models.Language).filter(models.Language.lang_id == learner.current_lang_id).first()

        if not lang_obj:
            lang_obj = db.query(models.Language).filter(models.Language.iso_code == "en").first()
            if not lang_obj:
                lang_obj = db.query(models.Language).first()

        lang_id = lang_obj.lang_id if lang_obj else 2
        lang_code = lang_obj.iso_code if lang_obj else "en"

        if learner and lang_id:
            learner.current_lang_id = lang_id
            db.commit()

        # 4. Complete any existing ACTIVE learning paths for this learner
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

        # 5. Insert new ACTIVE learning_path
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

        # 6. Resolve Curriculum & Lessons
        curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang_id).first()
        if not curriculum:
            curriculum = models.Curriculum(
                lang_id=lang_id,
                title=f"{lang_code.upper()} Literacy Curriculum",
                description=f"Personalized Literacy Curriculum for {lang_code.upper()}"
            )
            db.add(curriculum)
            db.commit()
            db.refresh(curriculum)

        selected_lessons: List[models.Lesson] = []
        ai_generated_success = False

        # Attempt Ollama AI Generation if available
        if is_ai_available():
            try:
                ai_plan = generate_path_plan(
                    weakest_skill=weakest_skill,
                    current_level=weakest_level,
                    target_level=target_level,
                    lang_code=lang_code
                )

                if ai_plan and curriculum:
                    target_mod = (
                        db.query(models.Module)
                        .filter(
                            models.Module.curriculum_id == curriculum.curriculum_id,
                            models.Module.skill_type == weakest_skill
                        )
                        .first()
                    )

                    if not target_mod:
                        target_mod = models.Module(
                            curriculum_id=curriculum.curriculum_id,
                            module_name=f"{weakest_skill} AI Mastery",
                            sequence_no=5,
                            skill_type=weakest_skill
                        )
                        db.add(target_mod)
                        db.commit()
                        db.refresh(target_mod)

                    for item in ai_plan[:5]:
                        l_title = item.get("title", f"AI {weakest_skill} Lesson")
                        l_diff = item.get("difficulty_level", weakest_level)

                        content = generate_lesson_content(
                            lesson_title=l_title,
                            skill_type=weakest_skill,
                            lang_code=lang_code,
                            target_level=l_diff
                        ) or {}

                        new_lesson = models.Lesson(
                            module_id=target_mod.module_id,
                            title=l_title,
                            content_type="Voice Practice" if "Pronunciation" in weakest_skill else "Functional Reading",
                            content_url=content.get("content_url", f"/audio/{lang_code}/ai_generated.mp3"),
                            target_text=content.get("target_text", f"Practice lesson for {l_title}"),
                            phonetic_script=json.dumps(content.get("phonetic_script", ["Phoneme"])),
                            difficulty_level=l_diff
                        )
                        db.add(new_lesson)
                        db.commit()
                        db.refresh(new_lesson)

                        selected_lessons.append(new_lesson)

                    if selected_lessons:
                        ai_generated_success = True
            except Exception as ai_err:
                print(f"[AI GENERATION NOTICE] Ollama generation notice: {ai_err}")

        # Rule-Based Selection Fallback
        if not ai_generated_success or not selected_lessons:
            candidate_lessons: List[models.Lesson] = []
            if curriculum:
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
                    target_modules = modules

                for mod in target_modules:
                    mod_lessons = (
                        db.query(models.Lesson)
                        .filter(models.Lesson.module_id == mod.module_id)
                        .all()
                    )
                    candidate_lessons.extend(mod_lessons)

            if not candidate_lessons:
                candidate_lessons = (
                    db.query(models.Lesson)
                    .join(models.Module, models.Lesson.module_id == models.Module.module_id)
                    .join(models.Curriculum, models.Module.curriculum_id == models.Curriculum.curriculum_id)
                    .filter(models.Curriculum.lang_id == lang_id)
                    .all()
                )

            if candidate_lessons:
                candidate_lessons.sort(
                    key=lambda l: DIFFICULTY_ORDER.get((l.difficulty_level or "").upper(), 99)
                )
                selected_lessons = candidate_lessons[:5]

        # Emergency Lesson Seeding if repository has no lessons for target language
        if not selected_lessons:
            emergency_mod = db.query(models.Module).filter(models.Module.curriculum_id == curriculum.curriculum_id).first()
            if not emergency_mod:
                emergency_mod = models.Module(
                    curriculum_id=curriculum.curriculum_id,
                    module_name=f"{lang_code.upper()} Phonics & Literacy",
                    sequence_no=1,
                    skill_type="Reading & Pronunciation"
                )
                db.add(emergency_mod)
                db.commit()
                db.refresh(emergency_mod)

            seed_data = [
                ("Phoneme Sounds & Vowels", "Voice Practice", "Welcome to English language practice"),
                ("Word Formation & Vocabulary", "Functional Reading", "Learning essential everyday vocabulary"),
                ("Sentence Construction & Tenses", "Functional Reading", "Language unlocks knowledge and opportunity"),
                ("Passage Reading & Fluency", "Voice Practice", "Continuous practice develops confidence and skill"),
                ("Literary Expression & Articulation", "Voice Practice", "Mastery of language transforms human communication")
            ]

            for s_idx, (t_title, t_type, t_text) in enumerate(seed_data):
                s_les = models.Lesson(
                    module_id=emergency_mod.module_id,
                    title=f"Lesson {s_idx+1}: {t_title}",
                    content_type=t_type,
                    content_url=f"/audio/{lang_code}/lesson_{s_idx+1}.mp3",
                    target_text=t_text,
                    difficulty_level="FOUNDATIONAL" if s_idx < 2 else "FUNCTIONAL"
                )
                db.add(s_les)
                db.commit()
                db.refresh(s_les)
                selected_lessons.append(s_les)

        # 7. Insert path_lesson rows
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


def get_active_path(learner_id: int, target_lang: Optional[str] = None, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves the current ACTIVE learning_path for a learner along with its ordered path_lesson list
    and structured milestones. Guarantees that lessons match target_lang if provided.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        req_lang_id = None
        if target_lang:
            target_iso = target_lang.strip().lower()
            lang_rec = db.query(models.Language).filter(models.Language.iso_code == target_iso).first()
            if lang_rec:
                req_lang_id = lang_rec.lang_id

        active_path = (
            db.query(models.LearningPath)
            .filter(
                models.LearningPath.learner_id == learner_id,
                models.LearningPath.status == "ACTIVE"
            )
            .order_by(desc(models.LearningPath.path_id))
            .first()
        )

        # If active_path exists and req_lang_id specified, check language match
        if active_path and req_lang_id:
            first_pl = (
                db.query(models.PathLesson, models.Lesson, models.Module, models.Curriculum)
                .join(models.Lesson, models.PathLesson.lesson_id == models.Lesson.lesson_id)
                .join(models.Module, models.Lesson.module_id == models.Module.module_id)
                .join(models.Curriculum, models.Module.curriculum_id == models.Curriculum.curriculum_id)
                .filter(models.PathLesson.path_id == active_path.path_id)
                .first()
            )
            if first_pl and first_pl.Curriculum.lang_id != req_lang_id:
                # Language mismatch! Generate a new learning path strictly for target_lang
                generate_learning_path(learner_id, target_lang=target_lang, db=db)
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
            if target_lang:
                generate_learning_path(learner_id, target_lang=target_lang, db=db)
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

        # Build structured milestones from ordered_lessons
        milestone1_lessons = ordered_lessons[:2]
        milestone2_lessons = ordered_lessons[2:4]
        milestone3_lessons = ordered_lessons[4:]

        milestones = [
            {
                "step": 1,
                "title": f"Milestone 1: {active_path.current_level} Phonics & Alphabet Fundamentals",
                "category": "Phonemes & Letter Recognition",
                "status": "UNLOCKED",
                "completion": 50 if any(l["status"] == "COMPLETED" for l in milestone1_lessons) else 0,
                "description": "Master letter sound associations and fundamental phonemes",
                "lessons": milestone1_lessons
            }
        ]

        if milestone2_lessons:
            milestones.append({
                "step": 2,
                "title": "Milestone 2: Functional Reading & Word Vocabulary",
                "category": "Functional Reading & Everyday Literacy",
                "status": "UNLOCKED" if any(l["status"] in ["UNLOCKED", "COMPLETED"] for l in milestone2_lessons) else "LOCKED",
                "completion": 50 if any(l["status"] == "COMPLETED" for l in milestone2_lessons) else 0,
                "description": "Everyday practical reading, signs, and functional vocabulary",
                "lessons": milestone2_lessons
            })

        if milestone3_lessons:
            milestones.append({
                "step": 3,
                "title": "Milestone 3: Sentence Grammar & Literary Expression",
                "category": "Advanced Fluency & Expression",
                "status": "UNLOCKED" if any(l["status"] in ["UNLOCKED", "COMPLETED"] for l in milestone3_lessons) else "LOCKED",
                "completion": 50 if any(l["status"] == "COMPLETED" for l in milestone3_lessons) else 0,
                "description": "Expressive speech, complex sentence grammar, and literary fluency",
                "lessons": milestone3_lessons
            })

        return {
            "path_id": active_path.path_id,
            "learner_id": active_path.learner_id,
            "target_proficiency": active_path.target_proficiency,
            "current_level": active_path.current_level,
            "path_title": f"AI Personalized Literacy Path ({active_path.current_level} → {active_path.target_proficiency})",
            "status": active_path.status,
            "completion_percentage": float(active_path.completion_percentage or 0.0),
            "personalization_reason": f"Generated by AI Engine based on placement score: Target goal set to {active_path.target_proficiency}.",
            "generated_on": active_path.generated_on.isoformat() if active_path.generated_on else None,
            "path_lessons": ordered_lessons,
            "milestones": milestones
        }

    finally:
        if close_db:
            db.close()
