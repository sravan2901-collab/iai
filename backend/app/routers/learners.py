"""
Learners Engine REST API Router for AksharAI Language Literacy Platform.

Exposes REST endpoints for:
1. GET  /api/learners/{learner_id}/proficiency
2. POST /api/learners/{learner_id}/learning-path/generate
3. GET  /api/learners/{learner_id}/learning-path
4. GET  /api/learners/{learner_id}/recommendations
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from app.services.proficiency_engine import predict_proficiency
from app.services.learning_path_engine import generate_learning_path, get_active_path
from app.services.recommendation_engine import generate_recommendations, get_recommendations

router = APIRouter(prefix="/api/learners", tags=["Learner Engine & Adaptive Services"])


def _verify_learner_access(
    learner_id: int,
    current_learner: Optional[models.Learner],
    db: Session
) -> models.Learner:
    """
    Validates learner existence and ensures strict authentication and multi-tenant authorization.
    Rejects unauthenticated callers (401) and unauthorized cross-tenant requests (403).
    """
    target_learner = db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
    if not target_learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID {learner_id} not found."
        )

    if not current_learner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access learner data."
        )

    if current_learner.learner_id != learner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot access another learner's learning path or recommendations."
        )

    return target_learner


@router.get("/{learner_id}/proficiency", summary="Get Learner Proficiency Level per Skill")
def get_learner_proficiency_api(
    learner_id: int,
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    GET /api/learners/{learner_id}/proficiency
    Returns predicted proficiency level per skill_type for the authenticated learner.
    """
    _verify_learner_access(learner_id, current_learner=current_learner, db=db)
    return predict_proficiency(learner_id, db=db)


@router.post("/{learner_id}/learning-path/generate", summary="Generate New Adaptive Learning Path")
def generate_learner_learning_path_api(
    learner_id: int,
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    POST /api/learners/{learner_id}/learning-path/generate
    Generates a new adaptive learning path for the authenticated learner, returning path_id and full path.
    """
    _verify_learner_access(learner_id, current_learner=current_learner, db=db)
    path_id = generate_learning_path(learner_id, db=db)
    active_path = get_active_path(learner_id, db=db)
    return {
        "path_id": path_id,
        "learning_path": active_path
    }


@router.get("/{learner_id}/learning-path", summary="Get Active Learning Path")
def get_learner_active_path_api(
    learner_id: int,
    lang: Optional[str] = Query(None),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    GET /api/learners/{learner_id}/learning-path
    Returns the current ACTIVE learning path for the authenticated learner matching target lang.
    """
    _verify_learner_access(learner_id, current_learner=current_learner, db=db)
    active_path = get_active_path(learner_id, target_lang=lang, db=db)
    if not active_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ACTIVE learning path found for learner {learner_id}."
        )
    return active_path


@router.get("/{learner_id}/recommendations", summary="Get Lesson Recommendations")
def get_learner_recommendations_api(
    learner_id: int,
    limit: int = Query(3, ge=1, le=10),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    GET /api/learners/{learner_id}/recommendations
    Returns recent lesson recommendations for the authenticated learner.
    """
    _verify_learner_access(learner_id, current_learner=current_learner, db=db)
    recs = get_recommendations(learner_id, limit=limit, db=db)
    if not recs:
        generate_recommendations(learner_id, limit=limit, db=db)
        recs = get_recommendations(learner_id, limit=limit, db=db)
    return recs
