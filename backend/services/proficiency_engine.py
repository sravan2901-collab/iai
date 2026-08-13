"""
Re-export module for services/proficiency_engine.py
"""

from app.services.proficiency_engine import (
    get_learner_scores,
    predict_proficiency,
    normalize_skill_type,
    CANONICAL_SKILL_TYPES,
)

__all__ = [
    "get_learner_scores",
    "predict_proficiency",
    "normalize_skill_type",
    "CANONICAL_SKILL_TYPES",
]
