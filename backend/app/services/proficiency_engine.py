"""
Proficiency Engine Service for AksharAI Language Literacy Platform.

Computes learner scores and predicts proficiency levels per skill_type
(Reading & Pronunciation, Word Formation, Grammar, Literature).
"""

from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app import models

# The 4 canonical skill types required by AksharAI proficiency system
CANONICAL_SKILL_TYPES = [
    "Reading & Pronunciation",
    "Word Formation",
    "Grammar",
    "Literature",
]

# Mapping table to convert raw DB module skill_types to canonical skill types
SKILL_TYPE_MAPPING = {
    "READING & PRONUNCIATION": "Reading & Pronunciation",
    "READING": "Reading & Pronunciation",
    "READ": "Reading & Pronunciation",
    "VOICE": "Reading & Pronunciation",
    "SPEAK": "Reading & Pronunciation",
    "PHONETICS": "Reading & Pronunciation",

    "WORD FORMATION": "Word Formation",
    "VOCABULARY": "Word Formation",
    "WRITE": "Word Formation",
    "SPELLING": "Word Formation",

    "GRAMMAR": "Grammar",
    "SYNTAX": "Grammar",

    "LITERATURE": "Literature",
    "COMPREHENSION": "Literature",
    "PROSE": "Literature",
}

DEFAULT_BENCHMARKS = [
    # Reading & Pronunciation
    {"skill_type": "Reading & Pronunciation", "level_name": "FOUNDATIONAL", "min_score": 0, "max_score": 44},
    {"skill_type": "Reading & Pronunciation", "level_name": "FUNCTIONAL", "min_score": 45, "max_score": 74},
    {"skill_type": "Reading & Pronunciation", "level_name": "PROFICIENT", "min_score": 75, "max_score": 100},
    
    # Word Formation
    {"skill_type": "Word Formation", "level_name": "FOUNDATIONAL", "min_score": 0, "max_score": 44},
    {"skill_type": "Word Formation", "level_name": "FUNCTIONAL", "min_score": 45, "max_score": 74},
    {"skill_type": "Word Formation", "level_name": "PROFICIENT", "min_score": 75, "max_score": 100},

    # Grammar
    {"skill_type": "Grammar", "level_name": "FOUNDATIONAL", "min_score": 0, "max_score": 44},
    {"skill_type": "Grammar", "level_name": "FUNCTIONAL", "min_score": 45, "max_score": 74},
    {"skill_type": "Grammar", "level_name": "PROFICIENT", "min_score": 75, "max_score": 100},

    # Literature
    {"skill_type": "Literature", "level_name": "FOUNDATIONAL", "min_score": 0, "max_score": 44},
    {"skill_type": "Literature", "level_name": "FUNCTIONAL", "min_score": 45, "max_score": 74},
    {"skill_type": "Literature", "level_name": "PROFICIENT", "min_score": 75, "max_score": 100},
]


def normalize_skill_type(db_skill: Optional[str]) -> Optional[str]:
    """
    Normalizes a raw database module or question skill_type string into one of the 4 canonical
    skill types: 'Reading & Pronunciation', 'Word Formation', 'Grammar', 'Literature'.

    :param db_skill: Raw skill_type string from the database.
    :return: Canonical skill_type string or original if unmapped.
    """
    if not db_skill:
        return None
    cleaned = db_skill.strip().upper()
    if cleaned in SKILL_TYPE_MAPPING:
        return SKILL_TYPE_MAPPING[cleaned]

    # Partial fallback matching
    if any(kw in cleaned for kw in ["READ", "VOICE", "PRONUNCIATION", "SPEAK", "PHONET"]):
        return "Reading & Pronunciation"
    if any(kw in cleaned for kw in ["WORD", "VOCAB", "WRITE", "SPELL"]):
        return "Word Formation"
    if any(kw in cleaned for kw in ["GRAMMAR", "SYNTAX"]):
        return "Grammar"
    if any(kw in cleaned for kw in ["LITERAT", "COMPREHENS", "PROSE"]):
        return "Literature"

    return db_skill


def ensure_default_benchmarks(db: Session) -> None:
    """
    Ensures that default benchmark rows exist in the proficiency_benchmark table
    for all 4 canonical skill types.

    :param db: SQLAlchemy Session.
    """
    existing_count = db.query(models.ProficiencyBenchmark).count()
    if existing_count == 0:
        for bench in DEFAULT_BENCHMARKS:
            db_bench = models.ProficiencyBenchmark(
                skill_type=bench["skill_type"],
                level_name=bench["level_name"],
                min_score=bench["min_score"],
                max_score=bench["max_score"]
            )
            db.add(db_bench)
        db.commit()


def get_learner_scores(learner_id: int, db: Optional[Session] = None) -> Dict[str, float]:
    """
    Queries assessment_result joined with assessment -> module to get skill_type,
    and returns the latest score per skill_type (using the highest attempt_no per
    assessment_id, most recent submitted_at on ties).

    :param learner_id: Unique integer ID of the learner.
    :param db: Optional SQLAlchemy Session. If omitted, uses SessionLocal context.
    :return: Dictionary mapping canonical skill_type to its latest score (e.g. {'Reading & Pronunciation': 85.0}).
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # Query assessment_result joined with assessment and module
        results = (
            db.query(models.AssessmentResult, models.Module.skill_type)
            .join(models.Assessment, models.AssessmentResult.assessment_id == models.Assessment.assessment_id)
            .join(models.Module, models.Assessment.module_id == models.Module.module_id)
            .filter(models.AssessmentResult.learner_id == learner_id)
            .order_by(
                models.AssessmentResult.assessment_id,
                desc(models.AssessmentResult.attempt_no),
                desc(models.AssessmentResult.submitted_at),
                desc(models.AssessmentResult.result_id)
            )
            .all()
        )

        # 1. Group by assessment_id to keep the result with the highest attempt_no (and most recent submitted_at on ties)
        latest_per_assessment: Dict[int, tuple[models.AssessmentResult, str]] = {}
        for res, raw_skill in results:
            ass_id = res.assessment_id
            if ass_id not in latest_per_assessment:
                latest_per_assessment[ass_id] = (res, raw_skill)

        # 2. For each canonical skill_type, find the latest score across all assessments
        scores_by_skill: Dict[str, float] = {}
        # Track most recent submitted_at / result_id per canonical skill type
        latest_meta_per_skill: Dict[str, tuple[Any, int]] = {}

        for ass_id, (res, raw_skill) in latest_per_assessment.items():
            canonical_skill = normalize_skill_type(raw_skill)
            if not canonical_skill:
                continue

            sub_at = res.submitted_at
            res_id = res.result_id

            if canonical_skill not in latest_meta_per_skill:
                latest_meta_per_skill[canonical_skill] = (sub_at, res_id)
                scores_by_skill[canonical_skill] = float(res.score)
            else:
                curr_sub_at, curr_res_id = latest_meta_per_skill[canonical_skill]
                # Compare submitted_at / result_id to keep the most recent assessment result
                if (sub_at and curr_sub_at and sub_at > curr_sub_at) or (sub_at == curr_sub_at and res_id > curr_res_id):
                    latest_meta_per_skill[canonical_skill] = (sub_at, res_id)
                    scores_by_skill[canonical_skill] = float(res.score)

        return scores_by_skill

    finally:
        if close_db:
            db.close()


def predict_proficiency(learner_id: int, db: Optional[Session] = None) -> Dict[str, str]:
    """
    Computes proficiency levels per skill_type (Reading & Pronunciation, Word Formation,
    Grammar, Literature). Looks up matching row in proficiency_benchmark
    (skill_type + min_score <= score <= max_score) and returns {skill_type: level_name}.
    If no assessment_result exists yet for a skill, returns level_name = "FOUNDATIONAL" as default.

    :param learner_id: Unique integer ID of the learner.
    :param db: Optional SQLAlchemy Session. If omitted, uses SessionLocal context.
    :return: Dictionary mapping canonical skill_type to level_name string.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        ensure_default_benchmarks(db)
        scores = get_learner_scores(learner_id, db=db)
        proficiency_predictions: Dict[str, str] = {}

        for skill in CANONICAL_SKILL_TYPES:
            if skill not in scores:
                # Default to FOUNDATIONAL if no assessment_result exists yet
                proficiency_predictions[skill] = "FOUNDATIONAL"
            else:
                score = scores[skill]
                # Query proficiency_benchmark table for matching skill_type and score range
                benchmark = (
                    db.query(models.ProficiencyBenchmark)
                    .filter(
                        models.ProficiencyBenchmark.skill_type == skill,
                        models.ProficiencyBenchmark.min_score <= score,
                        models.ProficiencyBenchmark.max_score >= score
                    )
                    .first()
                )

                if benchmark:
                    proficiency_predictions[skill] = benchmark.level_name
                else:
                    # Fallback benchmark lookup tier if exact row not found in benchmark table
                    if score < 45.0:
                        proficiency_predictions[skill] = "FOUNDATIONAL"
                    elif score < 75.0:
                        proficiency_predictions[skill] = "FUNCTIONAL"
                    else:
                        proficiency_predictions[skill] = "PROFICIENT"

        return proficiency_predictions

    finally:
        if close_db:
            db.close()
