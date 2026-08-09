from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from typing import Optional
from app.services.sarvam_service import sarvam_service
from app.config import settings

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

async def generate_personalized_path(learner_id: int, lang_code: str, db: Session):
    learner = db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner_id).first()
    
    if not learner or not profile:
        return None

    lang = db.query(models.Language).filter(models.Language.iso_code == lang_code).first()
    if not lang:
        return None

    reading_pct = profile.reading_pct or 0.0
    comprehension_pct = profile.comprehension_pct or 0.0
    voice_pct = profile.voice_pct or 0.0
    literacy_level = profile.literacy_level or "FOUNDATIONAL"

    # Step 2.1 Personalization Rules
    all_strong = (reading_pct >= 70.0 and comprehension_pct >= 70.0 and voice_pct >= 70.0)

    skills = {
        "READING": reading_pct,
        "COMPREHENSION": comprehension_pct,
        "VOICE": voice_pct
    }
    weakest_skill = min(skills, key=skills.get)
    weakest_score = skills[weakest_skill]

    if all_strong:
        skill_keywords = ["FUNCTIONAL", "PROFICIENT", "COMPREHENSION", "VOICE"]
        reason = f"Great job! All skill scores are >= 70% (Reading: {reading_pct}%, Comprehension: {comprehension_pct}%, Voice: {voice_pct}%). Foundational basics skipped — jumped directly to Functional & Advanced modules."
        target_level = "FUNCTIONAL" if literacy_level == "FOUNDATIONAL" else literacy_level
    elif weakest_skill == "READING":
        skill_keywords = ["READING", "Phonics", "Alphabet", "Greetings"]
        reason = f"Reading score ({weakest_score}%) is under 50%. Learner struggles with phonics — prioritizing Module: Alphabets & Phonics and Everyday Greetings."
        target_level = literacy_level
    elif weakest_skill == "COMPREHENSION":
        skill_keywords = ["COMPREHENSION", "ATM", "Banking", "Health", "Prescription", "Digital"]
        reason = f"Comprehension score ({weakest_score}%) is under 50%. Learner struggles with functional reading — prioritizing ATM & Banking, Health & Prescription, Digital Payment lessons."
        target_level = literacy_level
    else:
        skill_keywords = ["VOICE", "Workplace", "Customer Service", "Dialogue"]
        reason = f"Voice score ({weakest_score}%) is under 50%. Learner struggles with pronunciation — prioritizing Workplace Communication, Customer Service Dialogue + extra voice practice."
        target_level = literacy_level

    # Step 2.2 & 2.3 DB-Driven Queries
    curriculum = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == lang.lang_id,
        models.Curriculum.level == target_level
    ).first()

    if not curriculum:
        curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang.lang_id).first()

    if not curriculum:
        return None

    modules = db.query(models.Module).filter(
        models.Module.curriculum_id == curriculum.curriculum_id
    ).order_by(models.Module.sequence_no).all()

    def is_weak_module(m):
        m_skill = (m.skill_type or "").upper()
        m_name = (m.module_name or "").upper()
        return any(k.upper() in m_skill or k.upper() in m_name for k in skill_keywords)

    weak_modules = [m for m in modules if is_weak_module(m)]
    other_modules = [m for m in modules if not is_weak_module(m)]
    sorted_modules = weak_modules + other_modules

    path = db.query(models.LearningPath).filter(models.LearningPath.learner_id == learner_id).first()
    if not path:
        path = models.LearningPath(
            learner_id=learner_id,
            target_proficiency=target_level,
            current_level=target_level,
            status="ACTIVE"
        )
        db.add(path)
        db.commit()
        db.refresh(path)
    else:
        path.target_proficiency = target_level
        path.current_level = target_level
        db.query(models.PathLesson).filter(models.PathLesson.path_id == path.path_id).delete()
        db.commit()

    seq = 1
    milestones = []
    lesson_count = 0
    
    for idx, module in enumerate(sorted_modules):
        module_lessons = db.query(models.Lesson).filter(
            models.Lesson.module_id == module.module_id
        ).all()
        
        difficulty_order = {"FOUNDATIONAL": 1, "FUNCTIONAL": 2, "PROFICIENT": 3}
        module_lessons.sort(key=lambda x: difficulty_order.get(x.difficulty_level, 99))

        milestone_lessons = []
        for lesson in module_lessons:
            # Rule 7: Mark first 2 lessons as UNLOCKED, rest as LOCKED
            status = "UNLOCKED" if lesson_count < 2 else "LOCKED"
            
            path_lesson = models.PathLesson(
                path_id=path.path_id,
                lesson_id=lesson.lesson_id,
                sequence_no=seq,
                status=status
            )
            db.add(path_lesson)
            db.commit()
            db.refresh(path_lesson)
            seq += 1
            lesson_count += 1
            
            milestone_lessons.append({
                "lesson_id": lesson.lesson_id,
                "path_lesson_id": path_lesson.path_lesson_id,
                "title": lesson.title,
                "content_type": lesson.content_type,
                "target_text": lesson.target_text,
                "status": status
            })

        if milestone_lessons:
            milestone_title = f"Milestone {idx + 1}: {module.module_name}"
            milestone_desc = f"Focusing on {module.skill_type}"
            
            milestone_status = "UNLOCKED" if idx == 0 or milestone_lessons[0]["status"] == "UNLOCKED" else "LOCKED"

            milestones.append({
                "step": idx + 1,
                "title": milestone_title,
                "category": module.skill_type,
                "status": milestone_status,
                "completion": 0,
                "description": milestone_desc,
                "lessons": milestone_lessons
            })

    return {
        "path_id": path.path_id,
        "path_title": f"{lang.lang_name} Personalized Literacy Path ({target_level})",
        "current_level": target_level,
        "completion_percentage": 0,
        "personalization_reason": reason,
        "milestones": milestones
    }

@router.get("/active")
async def get_active_learning_path(
    lang: Optional[str] = Query(None),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    target_lang = None
    if lang:
        target_lang = lang

    if not target_lang and current_learner and current_learner.current_lang_id:
        learner_lang = db.query(models.Language).filter(models.Language.lang_id == current_learner.current_lang_id).first()
        if learner_lang:
            target_lang = learner_lang.iso_code

    if not target_lang:
        target_lang = "en"

    path_data = None
    if current_learner:
        path_data = await generate_personalized_path(current_learner.learner_id, target_lang, db)

    if path_data:
        if target_lang != "en" and settings.SARVAM_API_KEY != "mock_sarvam_api_key":
            for milestone in path_data.get("milestones", []):
                milestone["title"] = await sarvam_service.translate_text(
                    milestone["title"], source_lang="en-IN", target_lang=f"{target_lang}-IN"
                )
                milestone["description"] = await sarvam_service.translate_text(
                    milestone["description"], source_lang="en-IN", target_lang=f"{target_lang}-IN"
                )
        return path_data
    
    content = LANGUAGE_CONTENT.get(target_lang, LANGUAGE_CONTENT["en"])
    
    return {
        "path_id": 999,
        "path_title": content["path_title"],
        "current_level": "FOUNDATIONAL",
        "completion_percentage": 35.0,
        "personalization_reason": "Default path (No personalized data found).",
        "milestones": [
            {
                "step": m["milestone_number"],
                "title": m["title"],
                "category": "General",
                "status": "UNLOCKED" if idx == 0 else "LOCKED",
                "completion": m["progress_percentage"],
                "description": m["description"],
                "lessons": [
                    {
                        "lesson_id": l["id"],
                        "title": l["title"],
                        "content_type": "General",
                        "target_text": "",
                        "status": "UNLOCKED" if l["status"] in ["COMPLETED", "IN_PROGRESS"] else "LOCKED"
                    } for l in m["lessons"]
                ]
            } for idx, m in enumerate(content["milestones"])
        ]
    }

@router.post("/generate")
async def generate_path(
    payload: dict = Body(...),
    current_learner: models.Learner = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    lang = payload.get("lang", "en")
    
    path_data = await generate_personalized_path(current_learner.learner_id, lang, db)
    if not path_data:
        raise HTTPException(status_code=404, detail="Could not generate path from DB data.")
        
    return path_data

def complete_lesson_workflow(learner_id: int, lesson_id: int, score: float, db: Session):
    lesson = db.query(models.Lesson).filter(models.Lesson.lesson_id == lesson_id).first()
    if not lesson:
        return None

    module_id = lesson.module_id

    path = db.query(models.LearningPath).filter(models.LearningPath.learner_id == learner_id).first()
    if not path:
        return None

    path_lesson = db.query(models.PathLesson).filter(
        models.PathLesson.path_id == path.path_id,
        models.PathLesson.lesson_id == lesson_id
    ).first()

    if path_lesson:
        path_lesson.status = "COMPLETED"
        db.commit()

        # Step 3.1: Auto-unlock next lesson in sequence
        next_lesson = db.query(models.PathLesson).filter(
            models.PathLesson.path_id == path.path_id,
            models.PathLesson.sequence_no == path_lesson.sequence_no + 1
        ).first()

        if next_lesson and next_lesson.status == "LOCKED":
            next_lesson.status = "UNLOCKED"
            db.commit()

    # Step 3.1: Milestone completion & ProgressTracking table entry
    module_lessons = db.query(models.Lesson).filter(models.Lesson.module_id == module_id).all()
    mod_lesson_ids = [l.lesson_id for l in module_lessons]
    
    total_mod_count = len(mod_lesson_ids)
    completed_mod_count = db.query(models.PathLesson).filter(
        models.PathLesson.path_id == path.path_id,
        models.PathLesson.lesson_id.in_(mod_lesson_ids),
        models.PathLesson.status == "COMPLETED"
    ).count()

    module_completion_pct = round((completed_mod_count / total_mod_count) * 100.0, 1) if total_mod_count > 0 else 100.0

    prog = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.learner_id == learner_id,
        models.ProgressTracking.module_id == module_id
    ).first()

    if not prog:
        prog = models.ProgressTracking(
            learner_id=learner_id,
            module_id=module_id,
            completion_percent=module_completion_pct,
            time_spent_min=10
        )
        db.add(prog)
    else:
        prog.completion_percent = module_completion_pct
        prog.time_spent_min = (prog.time_spent_min or 0) + 5

    # Step 3.1: Update overall path completion percentage
    all_path_lessons = db.query(models.PathLesson).filter(models.PathLesson.path_id == path.path_id).all()
    total_path_count = len(all_path_lessons)
    completed_path_count = sum(1 for pl in all_path_lessons if pl.status == "COMPLETED")
    
    path.completion_percentage = round((completed_path_count / total_path_count) * 100.0, 1) if total_path_count > 0 else 0.0
    db.commit()

    # Step 3.2: Milestone Completion & Unlock Logic + Score Re-evaluation
    is_milestone_completed = (completed_mod_count == total_mod_count and total_mod_count > 0)
    
    if is_milestone_completed:
        if prog:
            prog.completion_percent = 100.0

        # Unlock next milestone's lessons
        uncompleted_path_lessons = db.query(models.PathLesson).filter(
            models.PathLesson.path_id == path.path_id,
            models.PathLesson.status == "LOCKED"
        ).order_by(models.PathLesson.sequence_no).all()

        if uncompleted_path_lessons:
            uncompleted_path_lessons[0].status = "UNLOCKED"
            if len(uncompleted_path_lessons) > 1 and uncompleted_path_lessons[1].lesson.module_id == uncompleted_path_lessons[0].lesson.module_id:
                uncompleted_path_lessons[1].status = "UNLOCKED"
            db.commit()

        # Re-evaluate learner scores (PronunciationScore & LearnerProfile)
        profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner_id).first()
        if profile:
            recent_scores = db.query(models.PronunciationScore).join(models.VoiceSession).filter(
                models.VoiceSession.learner_id == learner_id
            ).order_by(models.PronunciationScore.score_id.desc()).limit(5).all()

            if recent_scores:
                avg_voice = sum(s.overall_score for s in recent_scores) / len(recent_scores)
                profile.voice_pct = round(avg_voice, 1)

            # Update LearningPath.current_level and LearnerProfile.literacy_level upon progression
            if path.completion_percentage >= 50.0 or (profile.reading_pct >= 75 and profile.comprehension_pct >= 75 and profile.voice_pct >= 75):
                if profile.literacy_level == "FOUNDATIONAL":
                    profile.literacy_level = "FUNCTIONAL"
                    path.current_level = "FUNCTIONAL"
                    path.target_proficiency = "FUNCTIONAL"
                elif profile.literacy_level == "FUNCTIONAL":
                    profile.literacy_level = "PROFICIENT"
                    path.current_level = "PROFICIENT"
                    path.target_proficiency = "PROFICIENT"
            
            db.commit()

    return {
        "path_id": path.path_id,
        "lesson_id": lesson_id,
        "status": "COMPLETED",
        "milestone_completed": is_milestone_completed,
        "module_completion_pct": module_completion_pct,
        "path_completion_pct": path.completion_percentage,
        "current_level": path.current_level
    }

@router.patch("/lesson/{path_lesson_id}/status")
async def update_lesson_status(
    path_lesson_id: int,
    payload: dict = Body(...),
    current_learner: models.Learner = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    if not current_learner:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing status")

    path_lesson = db.query(models.PathLesson).filter(models.PathLesson.path_lesson_id == path_lesson_id).first()
    if not path_lesson:
        raise HTTPException(status_code=404, detail="PathLesson not found")

    if new_status == "COMPLETED":
        res = complete_lesson_workflow(current_learner.learner_id, path_lesson.lesson_id, 100.0, db)
        return {"message": "Lesson completed and next lesson unlocked", "status": "COMPLETED", "details": res}
    else:
        path_lesson.status = new_status
        db.commit()
        return {"message": "Status updated successfully", "status": new_status}
