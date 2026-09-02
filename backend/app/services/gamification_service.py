"""
Gamification Service — AksharAI
Handles:
1. Seeding of the canonical Achievement catalog (idempotent at startup)
2. Calendar-day based streak calculation and updating (LearnerProfile.last_activity_date)
3. Dynamic checking and awarding of learner achievements across lessons, voice sessions, streaks, and points
"""
import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app import models

# Canonical Achievement Catalog definition
CANONICAL_ACHIEVEMENTS = [
    {
        "achievement_name": "First Lesson Complete",
        "description": "Completed your first interactive lesson in the curriculum.",
        "criteria": "complete_1_lesson"
    },
    {
        "achievement_name": "First Voice Practice",
        "description": "Completed your first speech pronunciation session.",
        "criteria": "complete_1_voice"
    },
    {
        "achievement_name": "Perfect Pronunciation",
        "description": "Scored a perfect 100% on any pronunciation practice session.",
        "criteria": "voice_score_100"
    },
    {
        "achievement_name": "3-Day Streak",
        "description": "Maintained a 3-day daily learning practice streak.",
        "criteria": "streak_3_days"
    },
    {
        "achievement_name": "7-Day Streak",
        "description": "Maintained a 7-day daily learning practice streak.",
        "criteria": "streak_7_days"
    },
    {
        "achievement_name": "30-Day Streak",
        "description": "Maintained a 30-day daily learning practice streak.",
        "criteria": "streak_30_days"
    },
    {
        "achievement_name": "Module Complete",
        "description": "Reached 100% completion on any curriculum module.",
        "criteria": "module_100_percent"
    },
    {
        "achievement_name": "Path Complete",
        "description": "Reached 100% completion on your personalized learning path.",
        "criteria": "path_100_percent"
    },
    {
        "achievement_name": "100 Points",
        "description": "Earned 100 total literacy points.",
        "criteria": "points_100"
    },
    {
        "achievement_name": "500 Points",
        "description": "Earned 500 total literacy points.",
        "criteria": "points_500"
    }
]


def seed_achievement_catalog(db: Session) -> int:
    """
    Seeds canonical achievements into the Achievement table idempotently.
    Ensures no duplicates are created on repeated backend startups.
    Returns count of newly inserted achievements.
    """
    inserted_count = 0
    for item in CANONICAL_ACHIEVEMENTS:
        existing = db.query(models.Achievement).filter(
            models.Achievement.achievement_name == item["achievement_name"]
        ).first()
        if not existing:
            ach = models.Achievement(
                achievement_name=item["achievement_name"],
                description=item["description"],
                criteria=item["criteria"]
            )
            db.add(ach)
            inserted_count += 1
    if inserted_count > 0:
        db.commit()
    return inserted_count


def update_streak(learner_id: int, db: Session) -> int:
    """
    Updates the learner's daily practice streak based on calendar days.
    
    Logic:
    - Same calendar day: streak_count unchanged (min 1).
    - Exactly 1 day earlier (yesterday): streak_count += 1.
    - Anything else (gap >= 2 days, or first activity ever): streak_count = 1.
    - Always sets last_activity_date = today and commits.
    
    Returns the updated streak_count.
    """
    profile = db.query(models.LearnerProfile).filter(
        models.LearnerProfile.learner_id == learner_id
    ).first()

    if not profile:
        return 1

    today = datetime.date.today()
    last_date = profile.last_activity_date

    # Normalize if stored as datetime or date
    if isinstance(last_date, datetime.datetime):
        last_date = last_date.date()
    elif isinstance(last_date, str):
        try:
            last_date = datetime.date.fromisoformat(last_date[:10])
        except Exception:
            last_date = None

    if last_date is None:
        # First activity ever
        profile.streak_count = 1
    else:
        delta_days = (today - last_date).days
        if delta_days == 0:
            # Same day: maintain current streak (ensure at least 1)
            profile.streak_count = max(1, profile.streak_count or 1)
        elif delta_days == 1:
            # Consecutive day: increment streak
            profile.streak_count = (profile.streak_count or 0) + 1
        else:
            # Gap of 2+ days or clock reset: reset streak to 1
            profile.streak_count = 1

    profile.last_activity_date = today
    db.commit()
    db.refresh(profile)
    return profile.streak_count


def check_and_award_achievements(
    learner_id: int, 
    db: Session, 
    voice_score: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Checks all canonical achievements against the learner's current progress,
    streak, points, and voice scores.
    Awards any newly earned achievements that the learner does not already possess.
    
    Returns a list of newly unlocked achievements: [{"achievement_id": ..., "achievement_name": ..., ...}]
    """
    profile = db.query(models.LearnerProfile).filter(
        models.LearnerProfile.learner_id == learner_id
    ).first()

    if not profile:
        return []

    # 1. Fetch already earned achievement IDs for this learner
    earned_rows = db.query(models.LearnerAchievement).filter(
        models.LearnerAchievement.learner_id == learner_id
    ).all()
    earned_ids = set(r.achievement_id for r in earned_rows)

    # 2. Query learner progress state
    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == learner_id,
        models.LearningPath.status == "ACTIVE"
    ).order_by(models.LearningPath.path_id.desc()).first()

    completed_lessons_count = 0
    if path:
        completed_lessons_count = db.query(models.PathLesson).filter(
            models.PathLesson.path_id == path.path_id,
            models.PathLesson.status == "COMPLETED"
        ).count()

    # Voice session scores
    voice_scores = db.query(models.PronunciationScore.overall_score).join(
        models.VoiceSession
    ).filter(
        models.VoiceSession.learner_id == learner_id
    ).all()

    voice_count = len(voice_scores)
    max_voice_score = max([s[0] for s in voice_scores], default=0.0)
    if voice_score is not None and voice_score > max_voice_score:
        max_voice_score = voice_score
    if voice_score is not None and voice_count == 0:
        voice_count = 1

    # Module 100% completions
    has_completed_module = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.learner_id == learner_id,
        models.ProgressTracking.completion_percent >= 100.0
    ).first() is not None

    # Path completion
    is_path_completed = (path.completion_percentage >= 100.0) if path else False

    streak_count = profile.streak_count or 0
    total_points = profile.total_points or 0

    # 3. Evaluate criteria for all catalog achievements
    catalog = db.query(models.Achievement).all()
    newly_unlocked = []

    for ach in catalog:
        if ach.achievement_id in earned_ids:
            continue

        is_met = False
        crit = ach.criteria or ""

        if crit == "complete_1_lesson":
            is_met = (completed_lessons_count >= 1)
        elif crit == "complete_1_voice":
            is_met = (voice_count >= 1)
        elif crit == "voice_score_100":
            is_met = (max_voice_score >= 100.0)
        elif crit == "streak_3_days":
            is_met = (streak_count >= 3)
        elif crit == "streak_7_days":
            is_met = (streak_count >= 7)
        elif crit == "streak_30_days":
            is_met = (streak_count >= 30)
        elif crit == "module_100_percent":
            is_met = has_completed_module
        elif crit == "path_100_percent":
            is_met = is_path_completed
        elif crit == "points_100":
            is_met = (total_points >= 100)
        elif crit == "points_500":
            is_met = (total_points >= 500)

        if is_met:
            la = models.LearnerAchievement(
                learner_id=learner_id,
                achievement_id=ach.achievement_id,
                earned_on=func.now()
            )
            db.add(la)
            newly_unlocked.append({
                "achievement_id": ach.achievement_id,
                "achievement_name": ach.achievement_name,
                "description": ach.description,
                "criteria": ach.criteria
            })

    if newly_unlocked:
        db.commit()

    return newly_unlocked
