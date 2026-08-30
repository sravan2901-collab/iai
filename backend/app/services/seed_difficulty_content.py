# -*- coding: utf-8 -*-
"""
Seeds the database with lessons for all 7 new difficulty levels
(Absolute Beginner through Mastery) across 8 languages × 3 pillars.

Idempotent: skips if lessons with matching difficulty_level already exist for a language.
"""

import logging
from sqlalchemy.orm import Session
from app import models
from app.services.difficulty_content import DIFFICULTY_CONTENT, DIFFICULTY_LEVELS

logger = logging.getLogger(__name__)

# Levels to seed (skip "Zero" — already exists)
LEVELS_TO_SEED = DIFFICULTY_LEVELS[1:]  # ["Absolute Beginner", "Beginner", ..., "Mastery"]

SKILL_TO_MODULE_PREFIX = {
    "SPOKEN": "Spoken",
    "WRITTEN": "Written",
    "READING": "Reading"
}

LEVEL_DESCRIPTIONS = {
    "Absolute Beginner": "First words, basic objects, greeting responses, counting 11-20",
    "Beginner": "Family, body parts, food, colors, simple statements",
    "Elementary": "Daily routines, weather, animals, polite requests, time",
    "Intermediate": "Shopping, directions, health, transport, past tense",
    "Upper Intermediate": "Descriptions, opinions, comparisons, storytelling",
    "Advanced": "Workplace, banking, formal communication, news, interviews",
    "Mastery": "Public speaking, creative writing, debate, proverbs, essays"
}


def seed_difficulty_content(db: Session):
    """
    Main entry point. Seeds all difficulty levels for all languages.
    Returns (languages_seeded, lessons_created) counts.
    """
    languages = db.query(models.Language).all()
    if not languages:
        logger.warning("No languages found in database. Skipping difficulty content seed.")
        return 0, 0

    total_languages = 0
    total_lessons = 0

    for lang in languages:
        iso = lang.iso_code.lower()
        if iso not in DIFFICULTY_CONTENT:
            logger.info(f"No content data for language '{iso}'. Skipping.")
            continue

        # Check if already seeded — look for any "Absolute Beginner" lesson for this language
        existing = (
            db.query(models.Lesson)
            .join(models.Module)
            .join(models.Curriculum)
            .filter(
                models.Curriculum.lang_id == lang.lang_id,
                models.Lesson.difficulty_level == "Absolute Beginner"
            )
            .first()
        )
        if existing:
            logger.info(f"Difficulty content already seeded for {lang.lang_name} ({iso}). Skipping.")
            continue

        lessons_created = _seed_language(db, lang, iso)
        total_languages += 1
        total_lessons += lessons_created
        logger.info(f"✅ Seeded {lessons_created} lessons for {lang.lang_name} ({iso})")

    if total_lessons > 0:
        db.commit()
        logger.info(f"🎉 Total: Seeded {total_lessons} lessons across {total_languages} languages")
    else:
        logger.info("All difficulty content already seeded. No changes made.")

    return total_languages, total_lessons


def _seed_language(db: Session, lang: models.Language, iso: str) -> int:
    """Seed all difficulty levels for a single language. Returns lesson count."""
    content = DIFFICULTY_CONTENT[iso]
    lessons_created = 0

    # Find existing curricula for this language
    curricula = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == lang.lang_id
    ).all()

    if not curricula:
        logger.warning(f"No curriculum found for {lang.lang_name}. Creating one.")
        curriculum = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} Curriculum",
            description=f"Complete literacy curriculum for {lang.lang_name}"
        )
        db.add(curriculum)
        db.flush()
        curricula = [curriculum]

    # Use the first curriculum for this language
    curriculum = curricula[0]

    # Get the highest existing sequence number for modules
    max_seq = (
        db.query(models.Module.sequence_no)
        .filter(models.Module.curriculum_id == curriculum.curriculum_id)
        .order_by(models.Module.sequence_no.desc())
        .first()
    )
    next_seq = (max_seq[0] if max_seq else 0) + 1

    for level in LEVELS_TO_SEED:
        if level not in content:
            logger.warning(f"Missing level '{level}' in {iso} content. Skipping.")
            continue

        level_content = content[level]
        level_desc = LEVEL_DESCRIPTIONS.get(level, level)

        for skill_type in ["SPOKEN", "WRITTEN", "READING"]:
            if skill_type not in level_content:
                logger.warning(f"Missing {skill_type} in {iso}/{level}. Skipping.")
                continue

            lessons_data = level_content[skill_type]
            prefix = SKILL_TO_MODULE_PREFIX[skill_type]

            # Create a module for this level + skill
            module = models.Module(
                curriculum_id=curriculum.curriculum_id,
                module_name=f"{prefix} — {level}: {level_desc}",
                sequence_no=next_seq,
                skill_type=skill_type
            )
            db.add(module)
            db.flush()
            next_seq += 1

            # Create lessons under this module
            for lesson_data in lessons_data:
                lesson = models.Lesson(
                    module_id=module.module_id,
                    title=lesson_data.get("title", f"{skill_type} {level} Lesson"),
                    content_type=lesson_data.get("content_type", "Voice Practice"),
                    target_text=lesson_data.get("target_text", ""),
                    phonetic_script=lesson_data.get("phonetic_script", ""),
                    difficulty_level=level
                )
                db.add(lesson)
                lessons_created += 1

    db.flush()
    return lessons_created
