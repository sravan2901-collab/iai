"""
Learning Reports Router — AksharAI
Handles:
1. POST /api/reports/generate — Generates and persists AI pedagogical progress report snapshots
2. GET /api/reports/history — Lists the authenticated learner's generated reports
3. GET /api/reports/{report_id} — Retrieves a specific report's full narrative & data snapshot
"""
import json
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from app.routers.progress import build_learner_progress_snapshot
from app.services.ai_course_generator import ai_course_generator

router = APIRouter(prefix="/api/reports", tags=["Learning Reports"])


@router.post("/generate")
async def generate_learning_report(
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Generates a new comprehensive progress snapshot and AI pedagogical narrative report.
    Persists the report in the LearningReport table and returns the complete report payload.
    """
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 1. Build authoritative progress snapshot using shared aggregation logic
    snapshot = build_learner_progress_snapshot(current_learner, db)

    # 2. Generate pedagogical AI narrative (falls back gracefully to rule-based or None if unavailable)
    narrative = None
    try:
        narrative = await ai_course_generator.generate_report_narrative(snapshot)
    except Exception as ai_err:
        print(f"[REPORTS ROUTER NOTICE] AI narrative generation notice: {ai_err}")
        narrative = None

    # 3. Persist to LearningReport table
    today_str = datetime.date.today().isoformat()
    overall_progress = snapshot.get("profile", {}).get("overall_pct", 0.0)

    report_record = models.LearningReport(
        learner_id=current_learner.learner_id,
        reporting_period=today_str,
        overall_progress=overall_progress,
        summary_json=json.dumps(snapshot),
        narrative=narrative
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return {
        "report_id": report_record.report_id,
        "learner_id": report_record.learner_id,
        "reporting_period": report_record.reporting_period,
        "generated_at": str(report_record.generated_at),
        "overall_progress": report_record.overall_progress,
        "narrative": report_record.narrative,
        "snapshot": snapshot
    }


@router.get("/history")
async def get_report_history(
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Returns list of past learning reports generated for the authenticated learner,
    ordered by most recent first.
    """
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    reports = db.query(models.LearningReport).filter(
        models.LearningReport.learner_id == current_learner.learner_id
    ).order_by(
        models.LearningReport.generated_at.desc()
    ).all()

    return [
        {
            "report_id": r.report_id,
            "reporting_period": r.reporting_period,
            "overall_progress": r.overall_progress,
            "generated_at": str(r.generated_at),
            "has_narrative": bool(r.narrative)
        }
        for r in reports
    ]


@router.get("/{report_id}")
async def get_report_detail(
    report_id: int,
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Returns the complete snapshot data and AI narrative for a specific learning report.
    Guarded so learners can only access their own reports.
    """
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")

    report = db.query(models.LearningReport).filter(
        models.LearningReport.report_id == report_id
    ).first()

    if not report or report.learner_id != current_learner.learner_id:
        raise HTTPException(status_code=404, detail="Learning report not found or unauthorized access")

    parsed_snapshot = {}
    if report.summary_json:
        try:
            parsed_snapshot = json.loads(report.summary_json)
        except Exception:
            parsed_snapshot = {}

    return {
        "report_id": report.report_id,
        "learner_id": report.learner_id,
        "reporting_period": report.reporting_period,
        "generated_at": str(report.generated_at),
        "overall_progress": report.overall_progress,
        "narrative": report.narrative,
        "snapshot": parsed_snapshot
    }
