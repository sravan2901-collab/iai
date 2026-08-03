from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from typing import Optional

router = APIRouter(prefix="/api/learning-path", tags=["Adaptive Learning Path Generator"])

LANGUAGE_CONTENT = {
    "en": {
        "path_title": "English Language Literacy Roadmap",
        "milestones": [
            {
                "id": 1,
                "milestone_number": 1,
                "title": "Phonemes & Alphabet Fundamentals",
                "description": "Master letter-sound associations, long/short vowels, and consonant blends.",
                "progress_percentage": 100,
                "is_completed": True,
                "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "Vowel Sounds & Phoneme Synthesis", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "Consonant Blends & Syllables", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2,
                "milestone_number": 2,
                "title": "Vocabulary & Sentence Grammar",
                "description": "Expand vocabulary, master verb tenses, prefixes, suffixes, and sentence construction.",
                "progress_percentage": 40,
                "is_completed": False,
                "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "Noun-Verb Agreement & Tenses", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "Prefixes, Suffixes & Root Words", "status": "IN_PROGRESS", "score": 0}
                ]
            },
            {
                "id": 3,
                "milestone_number": 3,
                "title": "Advanced Literary Fluency & Expression",
                "description": "Comprehend complex literary passages and express thoughts fluently.",
                "progress_percentage": 0,
                "is_completed": False,
                "status": "LOCKED",
                "lessons": [
                    {"id": 5, "title": "Prose & Passage Comprehension", "status": "LOCKED", "score": 0},
                    {"id": 6, "title": "Fluent Speech & Public Articulation", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "te": {
        "path_title": "తెలుగు భాషా అక్షరాస్యత కార్యాచరణ సాధన",
        "milestones": [
            {
                "id": 1,
                "milestone_number": 1,
                "title": "అక్షరాలు, వర్ణమాల మరియు గుణింతాలు",
                "description": "అచ్చులు, హల్లులు, గుణింతపు గుర్తులు మరియు ఒత్తుల ఉచ్చారణలో నైపుణ్యం సాధించండి.",
                "progress_percentage": 100,
                "is_completed": True,
                "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "అచ్చులు మరియు హల్లుల ఉచ్చారణ", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "గుణింతాలు మరియు ఒత్తుల సాధన", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2,
                "milestone_number": 2,
                "title": "పదజాలం, సంధులు మరియు వాక్య నిర్మాణం",
                "description": "పర్యాయపదాలు, నానార్థాలు, సంధులు మరియు వ్యాకరణ వాక్య నిర్మాణం నేర్చుకోండి.",
                "progress_percentage": 40,
                "is_completed": False,
                "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "తెలుగు సంధులు మరియు సమాసాలు", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "వాక్య నిర్మాణం మరియు వ్యాకరణం", "status": "IN_PROGRESS", "score": 0}
                ]
            },
            {
                "id": 3,
                "milestone_number": 3,
                "title": "సాహిత్య గద్య పఠనం మరియు భావ వ్యక్తీకరణ",
                "description": "ఉన్నత సాహిత్య గద్యాలను చదవడం మరియు అనర్గళంగా మాట్లాడటం.",
                "progress_percentage": 0,
                "is_completed": False,
                "status": "LOCKED",
                "lessons": [
                    {"id": 5, "title": "సాహిత్య గద్య పఠనం మరియు అర్థ గ్రహణ", "status": "LOCKED", "score": 0},
                    {"id": 6, "title": "అనర్గళ భాషా ప్రసంగం", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "hi": {
        "path_title": "हिन्दी भाषा साक्षरता मार्गदर्शिका",
        "milestones": [
            {
                "id": 1,
                "milestone_number": 1,
                "title": "वर्णमाला, स्वर एवं मात्रा ज्ञान",
                "description": "स्वर, व्यंजन, मात्राएँ एवं वर्ण संयोजन में दक्षता प्राप्त करें।",
                "progress_percentage": 100,
                "is_completed": True,
                "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "स्वर एवं व्यंजन उच्चारण", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "मात्राएँ एवं संयुक्त अक्षर", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2,
                "milestone_number": 2,
                "title": "शब्दावली, संधि एवं वाक्य व्याकरण",
                "description": "पर्यायवाची, विलोम शब्द, संधि एवं व्याकरणिक वाक्य रचना सीखें।",
                "progress_percentage": 40,
                "is_completed": False,
                "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "हिंदी संधि एवं समास", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "शुद्ध वाक्य रचना एवं व्याकरण", "status": "IN_PROGRESS", "score": 0}
                ]
            },
            {
                "id": 3,
                "milestone_number": 3,
                "title": "उच्च साहित्यिक वाचन एवं अभिव्यक्ति",
                "description": "साहित्यिक गद्यांश वाचन और धाराप्रवाह वाचन में दक्षता।",
                "progress_percentage": 0,
                "is_completed": False,
                "status": "LOCKED",
                "lessons": [
                    {"id": 5, "title": "साहित्यिक गद्यांश वाचन एवं बोध", "status": "LOCKED", "score": 0},
                    {"id": 6, "title": "धाराप्रवाह भाषा अभिव्यक्ति", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    }
}

@router.get("/active")
def get_active_learning_path(
    lang: Optional[str] = Query("en"),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    target_lang = lang if lang in LANGUAGE_CONTENT else "en"
    content = LANGUAGE_CONTENT[target_lang]

    if current_learner:
        path = db.query(models.LearningPath).filter(models.LearningPath.learner_id == current_learner.learner_id).first()
        if path:
            return {
                "path_id": path.path_id,
                "learner_id": current_learner.learner_id,
                "target_lang": target_lang,
                "title": content["path_title"],
                "current_tier": path.current_tier or "FOUNDATIONAL",
                "completion_percentage": path.completion_percentage or 35.0,
                "milestones": content["milestones"]
            }

    return {
        "path_id": 999,
        "learner_id": 0,
        "target_lang": target_lang,
        "title": content["path_title"],
        "current_tier": "FOUNDATIONAL",
        "completion_percentage": 35.0,
        "milestones": content["milestones"]
    }
