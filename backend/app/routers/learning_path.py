from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/learning-path", tags=["Learning Path"])

LANGUAGE_CONTENT = {
    "en": {
        "milestones": [
            {
                "step": 1,
                "title": "Milestone 1: Foundational Phonics & Letter Recognition",
                "category": "Everyday Essentials",
                "lessons": [
                    {"lesson_id": 1, "title": "Greetings & Everyday Phrases", "content_type": "Voice Practice", "target_text": "Hello, how are you today?"},
                    {"lesson_id": 2, "title": "Numbers One to Ten", "content_type": "Voice Practice", "target_text": "One Two Three Four Five Six Seven Eight Nine Ten"}
                ]
            },
            {
                "step": 2,
                "title": "Milestone 2: Functional Reading & Financial Literacy",
                "category": "Digital & Healthcare Literacy",
                "lessons": [
                    {"lesson_id": 3, "title": "ATM PIN Security Guidelines", "content_type": "Functional Reading", "target_text": "Never share your ATM PIN with anyone"},
                    {"lesson_id": 4, "title": "Reading Digital Payment Receipts", "content_type": "Functional Reading", "target_text": "Payment successful One Hundred Rupees"}
                ]
            },
            {
                "step": 3,
                "title": "Milestone 3: Workplace Literacy & Voice Fluency",
                "category": "Workplace Communication",
                "lessons": [
                    {"lesson_id": 5, "title": "Workplace Safety & Polite Communication", "content_type": "Voice Practice", "target_text": "Thank you for your assistance today"},
                    {"lesson_id": 6, "title": "Customer Service Conversation", "content_type": "Voice Practice", "target_text": "Please provide me with a receipt"}
                ]
            }
        ]
    }
}

class GeneratePathRequest(BaseModel):
    proficiency_level: str
    lang: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    status: str

@router.get("/active")
def get_active_learning_path(
    lang: Optional[str] = "en",
    db: Session = Depends(get_db),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    target_lang = lang or "en"
    if target_lang not in LANGUAGE_CONTENT:
        target_lang = "en"
    
    learning_path = None
    literacy_level = "FOUNDATIONAL"

    if current_learner:
        learning_path = db.query(models.LearningPath).filter(
            models.LearningPath.learner_id == current_learner.learner_id,
            models.LearningPath.status == "ACTIVE"
        ).first()

        profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == current_learner.learner_id).first()
        if profile and profile.literacy_level:
            literacy_level = profile.literacy_level

    milestones_data = LANGUAGE_CONTENT[target_lang]["milestones"]
    level = learning_path.current_level if learning_path else literacy_level
    target_level = learning_path.target_proficiency if learning_path else "ALPHABET_SOUNDS"
    
    if level == "FOUNDATIONAL":
        completion = 15
    elif level == "FUNCTIONAL":
        completion = 50
    else:
        completion = 85

    milestones = []
    for m in milestones_data:
        ms_status = "LOCKED"
        ms_completion = 0
        if m["step"] == 1:
            ms_status = "UNLOCKED"
            ms_completion = 100 if level in ["FUNCTIONAL", "PROFICIENT"] else 30
        elif m["step"] == 2:
            ms_status = "UNLOCKED" if level in ["FUNCTIONAL", "PROFICIENT"] else "LOCKED"
            ms_completion = 100 if level == "PROFICIENT" else (40 if level == "FUNCTIONAL" else 0)
        elif m["step"] == 3:
            ms_status = "UNLOCKED" if level == "PROFICIENT" else "LOCKED"
            ms_completion = 20 if level == "PROFICIENT" else 0
            
        lessons = []
        for l in m["lessons"]:
            l_status = "LOCKED"
            if m["step"] == 1:
                if l["lesson_id"] == 1:
                    l_status = "COMPLETED" if level != "FOUNDATIONAL" else "ACTIVE"
                else:
                    l_status = "COMPLETED" if level != "FOUNDATIONAL" else "UNLOCKED"
            elif m["step"] == 2:
                if l["lesson_id"] == 3:
                    l_status = "ACTIVE" if level == "FUNCTIONAL" else ("COMPLETED" if level == "PROFICIENT" else "LOCKED")
                else:
                    l_status = "UNLOCKED" if level in ["FUNCTIONAL", "PROFICIENT"] else "LOCKED"
            elif m["step"] == 3:
                l_status = "ACTIVE" if level == "PROFICIENT" else "LOCKED"
                
            lessons.append({
                "lesson_id": l["lesson_id"],
                "title": l["title"],
                "content_type": l["content_type"],
                "target_text": l["target_text"],
                "status": l_status
            })
            
        milestones.append({
            "step": m["step"],
            "title": m["title"],
            "category": m["category"],
            "status": ms_status,
            "completion": ms_completion,
            "lessons": lessons
        })

    return {
        "path_id": learning_path.path_id if learning_path else 1,
        "path_title": f"Adaptive Learning Roadmap — Track: {level}",
        "language": {"lang_id": target_lang, "lang_name": "English", "iso_code": target_lang},
        "current_level": level,
        "target_level": target_level,
        "completion_percentage": completion,
        "milestones": milestones
    }
