from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/assessment", tags=["Generic Initial Assessment & Learning Path Generation"])

DIAGNOSTIC_QUESTIONS_BY_LANG = {
    "en": [
        {
            "stage": 1,
            "skill_type": "READING",
            "question_title": "Stage 1: Reading & Phoneme Recognition",
            "question_text": "Select the word that starts with the letter 'B' /b/ sound:",
            "options": [
                {"id": "a", "text": "Ball", "is_correct": True},
                {"id": "b", "text": "Sun", "is_correct": False},
                {"id": "c", "text": "Cat", "is_correct": False},
                {"id": "d", "text": "Tree", "is_correct": False}
            ]
        },
        {
            "stage": 2,
            "skill_type": "COMPREHENSION",
            "question_title": "Stage 2: Comprehension & Functional Literacy",
            "question_text": "Select the correct meaning for the notice: 'DANGER - DO NOT TOUCH'",
            "options": [
                {"id": "a", "text": "Unsafe / Keep Away", "is_correct": True},
                {"id": "b", "text": "Free Entry", "is_correct": False},
                {"id": "c", "text": "Welcome Entrance", "is_correct": False},
                {"id": "d", "text": "Open Store", "is_correct": False}
            ]
        },
        {
            "stage": 3,
            "skill_type": "VOICE_SPEECH",
            "question_title": "Stage 3: Voice & Speech Pronunciation Assessment",
            "question_text": "Press the microphone button and read aloud the sentence below:",
            "target_text": "Welcome to AksharAI literacy training"
        }
    ],
    "te": [
        {
            "stage": 1,
            "skill_type": "READING",
            "question_title": "దశ 1: అక్షర పఠనం మరియు ధ్వని గుర్తింపు (Reading & Phonemes)",
            "question_text": "'బ' /b/ శబ్దంతో ప్రారంభమయ్యే పదాన్ని ఎంచుకోండి:",
            "options": [
                {"id": "a", "text": "బంతి (Ball)", "is_correct": True},
                {"id": "b", "text": "సూర్యుడు (Sun)", "is_correct": False},
                {"id": "c", "text": "పిల్లి (Cat)", "is_correct": False},
                {"id": "d", "text": "చెట్టు (Tree)", "is_correct": False}
            ]
        },
        {
            "stage": 2,
            "skill_type": "COMPREHENSION",
            "question_title": "దశ 2: అవగాహన మరియు రోజువారీ అక్షరాస్యత (Comprehension)",
            "question_text": "గమనిక: 'ప్రమాదం - ముట్టుకోవద్దు' యొక్క సరైన అర్థం ఎంచుకోండి:",
            "options": [
                {"id": "a", "text": "అపాయకరం / దూరంగా ఉండండి", "is_correct": True},
                {"id": "b", "text": "ఉచిత ప్రవేశం", "is_correct": False},
                {"id": "c", "text": "స్వాగత ద్వారం", "is_correct": False},
                {"id": "d", "text": "దుకాణం తెరిచి ఉంది", "is_correct": False}
            ]
        },
        {
            "stage": 3,
            "skill_type": "VOICE_SPEECH",
            "question_title": "దశ 3: ధ్వని ఉచ్చారణ మరియు మాటల అంచనా (Voice Assessment)",
            "question_text": "మైక్రోఫోన్ నొక్కి క్రింది వాక్యాన్ని బిగ్గరగా చదవండి:",
            "target_text": "అక్షరAI అక్షరాస్యత శిక్షణకు స్వాగతం"
        }
    ],
    "hi": [
        {
            "stage": 1,
            "skill_type": "READING",
            "question_title": "चरण 1: अक्षर वाचन और ध्वनि पहचान (Reading & Phonemes)",
            "question_text": "'ब' /b/ ध्वनि से शुरू होने वाला शब्द चुनें:",
            "options": [
                {"id": "a", "text": "बस (Bus)", "is_correct": True},
                {"id": "b", "text": "सूरज (Sun)", "is_correct": False},
                {"id": "c", "text": "बिल्ली (Cat)", "is_correct": False},
                {"id": "d", "text": "पेड़ (Tree)", "is_correct": False}
            ]
        },
        {
            "stage": 2,
            "skill_type": "COMPREHENSION",
            "question_title": "चरण 2: समझ और व्यावहारिक साक्षरता (Comprehension)",
            "question_text": "सूचना: 'खतरा - छूना मना है' का सही अर्थ चुनें:",
            "options": [
                {"id": "a", "text": "असुरक्षित / दूर रहें", "is_correct": True},
                {"id": "b", "text": "मुफ्त प्रवेश", "is_correct": False},
                {"id": "c", "text": "स्वागत द्वार", "is_correct": False},
                {"id": "d", "text": "दुकान खुली है", "is_correct": False}
            ]
        },
        {
            "stage": 3,
            "skill_type": "VOICE_SPEECH",
            "question_title": "चरण 3: वाणी उच्चारण और भाषण मूल्यांकन (Voice Assessment)",
            "question_text": "माइक बटन दबाएं और नीचे दिए गए वाक्य को जोर से पढ़ें:",
            "target_text": "अक्षरAI साक्षरता प्रशिक्षण में आपका स्वागत है"
        }
    ],
    "ta": [
        {
            "stage": 1,
            "skill_type": "READING",
            "question_title": "நிலை 1: வாசிப்பு மற்றும் ஒலி அறிதல் (Reading & Phonemes)",
            "question_text": "'ப' /b/ ஒலியுடன் தொடங்கும் சொல்லைத் தேர்ந்தெடுக்கவும்:",
            "options": [
                {"id": "a", "text": "பந்து (Ball)", "is_correct": True},
                {"id": "b", "text": "சூரியன் (Sun)", "is_correct": False},
                {"id": "c", "text": "பூனை (Cat)", "is_correct": False},
                {"id": "d", "text": "மரம் (Tree)", "is_correct": False}
            ]
        },
        {
            "stage": 2,
            "skill_type": "COMPREHENSION",
            "question_title": "நிலை 2: புரிதல் மற்றும் நடைமுறை எழுத்தறிவு (Comprehension)",
            "question_text": "அறிவிப்பு: 'ஆபத்து - தொடாதே' என்பதன் சரியான பொருளைத் தேர்ந்தெடுக்கவும்:",
            "options": [
                {"id": "a", "text": "பாதுகாப்பற்றது / விலகி இருங்கள்", "is_correct": True},
                {"id": "b", "text": "இலவச அனுமதி", "is_correct": False},
                {"id": "c", "text": "வரவேற்பு வாயில்", "is_correct": False},
                {"id": "d", "text": "கடை திறந்துள்ளது", "is_correct": False}
            ]
        },
        {
            "stage": 3,
            "skill_type": "VOICE_SPEECH",
            "question_title": "நிலை 3: குரல் உச்சரிப்பு மற்றும் பேச்சு மதிப்பீடு (Voice Assessment)",
            "question_text": "மைக் பொத்தானை அழுத்தி கீழே உள்ள வாக்கியத்தை சத்தமாக படிக்கவும்:",
            "target_text": "அக்ஷர்AI எழுத்தறிவு பயிற்சிக்கு நல்வரவு"
        }
    ],
    "bn": [
        {
            "stage": 1,
            "skill_type": "READING",
            "question_title": "ধাপ ১: পাঠ ও ধ্বনি সনাক্তকরণ (Reading & Phonemes)",
            "question_text": "'ব' /b/ ধ্বনি দিয়ে শুরু হওয়া শব্দটি নির্বাচন করুন:",
            "options": [
                {"id": "a", "text": "বল (Ball)", "is_correct": True},
                {"id": "b", "text": "সূর্য (Sun)", "is_correct": False},
                {"id": "c", "text": "বিড়াল (Cat)", "is_correct": False},
                {"id": "d", "text": "গাছ (Tree)", "is_correct": False}
            ]
        },
        {
            "stage": 2,
            "skill_type": "COMPREHENSION",
            "question_title": "ধাপ ২: উপলব্ধি ও ব্যবহারিক সাক্ষরতা (Comprehension)",
            "question_text": "বিজ্ঞপ্তি: 'বিপদ - স্পর্শ করবেন না' এর সঠিক অর্থ নির্বাচন করুন:",
            "options": [
                {"id": "a", "text": "অনিরাপদ / দূরে থাকুন", "is_correct": True},
                {"id": "b", "text": "বিনামূল্যে প্রবেশ", "is_correct": False},
                {"id": "c", "text": "স্বাগত তোরণ", "is_correct": False},
                {"id": "d", "text": "দোকান খোলা আছে", "is_correct": False}
            ]
        },
        {
            "stage": 3,
            "skill_type": "VOICE_SPEECH",
            "question_title": "ধাপ ৩: কণ্ঠস্বর উচ্চারণ ও ব্যাকরণ মূল্যায়ন (Voice Assessment)",
            "question_text": "মাইক্রোফোন বোতাম চাপুন এবং নীচের বাক্যটি উচ্চস্বরে পড়ুন:",
            "target_text": "অক্ষরAI সাক্ষরতা প্রশিক্ষণে আপনাকে স্বাগতম"
        }
    ],
    "mr": [
        {
            "stage": 1,
            "skill_type": "READING",
            "question_title": "टप्पा १: वाचन आणि ध्वनी ओळख (Reading & Phonemes)",
            "question_text": "'ब' /b/ ध्वनीने सुरू होणारा शब्द निवडा:",
            "options": [
                {"id": "a", "text": "बस (Bus)", "is_correct": True},
                {"id": "b", "text": "सूर्य (Sun)", "is_correct": False},
                {"id": "c", "text": "मांजर (Cat)", "is_correct": False},
                {"id": "d", "text": "झाड (Tree)", "is_correct": False}
            ]
        },
        {
            "stage": 2,
            "skill_type": "COMPREHENSION",
            "question_title": "टप्पा २: आकलन आणि व्यावहारिक साक्षरता (Comprehension)",
            "question_text": "सूचना: 'धोका - हात लावू नका' चा अचूक अर्थ निवडा:",
            "options": [
                {"id": "a", "text": "असुरक्षित / लांब राहा", "is_correct": True},
                {"id": "b", "text": "मोफत प्रवेश", "is_correct": False},
                {"id": "c", "text": "स्वागत द्वार", "is_correct": False},
                {"id": "d", "text": "दुकान उघडे आहे", "is_correct": False}
            ]
        },
        {
            "stage": 3,
            "skill_type": "VOICE_SPEECH",
            "question_title": "टप्पा ३: स्वर उच्चारण आणि भाषण मूल्यांकन (Voice Assessment)",
            "question_text": "मायक्रोफोन बटण दाबा आणि खालील वाक्य मोठ्याने वाचा:",
            "target_text": "अक्षरAI साक्षरता प्रशिक्षणात आपले स्वागत आहे"
        }
    ]
}

class InitialAssessmentAnswer(BaseModel):
    stage: int
    skill_type: str
    selected_option_id: Optional[str] = None
    spoken_text: Optional[str] = None
    is_correct: Optional[bool] = False

class InitialAssessmentSubmitPayload(BaseModel):
    learner_id: Optional[int] = None
    lang: Optional[str] = "en"
    answers: List[InitialAssessmentAnswer]

@router.get("/diagnostic-questions")
def get_diagnostic_questions(
    lang: Optional[str] = "en",
    db: Session = Depends(get_db)
):
    """
    Returns generic 3-stage initial assessment questions for neo-learners in their native language:
    Stage 1: Reading & Phoneme Recognition Assessment
    Stage 2: Comprehension & Functional Literacy Assessment
    Stage 3: Voice & Speech Pronunciation Assessment
    """
    target_lang = lang if lang in DIAGNOSTIC_QUESTIONS_BY_LANG else "en"
    return DIAGNOSTIC_QUESTIONS_BY_LANG[target_lang]

@router.post("/submit")
def submit_initial_assessment(payload: InitialAssessmentSubmitPayload, db: Session = Depends(get_db)):
    """
    Evaluates the generic initial assessment, establishes the proficiency benchmark,
    and returns a structured Adaptive Learning Path Roadmap in the learner's native language.
    """
    reading_score = 0
    comprehension_score = 0
    voice_score = 0

    for ans in payload.answers:
        if ans.skill_type == "READING":
            if ans.is_correct:
                reading_score = 35
        elif ans.skill_type == "COMPREHENSION":
            if ans.is_correct:
                comprehension_score = 35
        elif ans.skill_type == "VOICE_SPEECH":
            voice_score = 30

    total_score = reading_score + comprehension_score + voice_score

    # Determine Proficiency Benchmark Level
    if total_score >= 80:
        level = "PROFICIENT"
        target_level = "FLUENCY_MASTERY"
    elif total_score >= 50:
        level = "FUNCTIONAL"
        target_level = "DIGITAL_FINANCIAL"
    else:
        level = "FOUNDATIONAL"
        target_level = "ALPHABET_SOUNDS"

    # Structured Adaptive Learning Path Roadmap
    from app.routers.learning_path import LANGUAGE_CONTENT
    
    target_lang = payload.lang or "en"
    if target_lang not in LANGUAGE_CONTENT:
        target_lang = "en"

    milestones_data = LANGUAGE_CONTENT[target_lang]["milestones"]
    
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

    learning_path = {
        "path_title": f"Adaptive Learning Roadmap — Track: {level}",
        "current_level": level,
        "target_level": target_level,
        "completion_percentage": 15 if level == "FOUNDATIONAL" else (50 if level == "FUNCTIONAL" else 85),
        "milestones": milestones
    }

    # Update Learner Profile & Learning Path in database if learner_id provided
    if payload.learner_id:
        if payload.lang:
            learner = db.query(models.Learner).filter(models.Learner.learner_id == payload.learner_id).first()
            if learner:
                learner.current_lang_id = payload.lang
                db.commit()
        profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == payload.learner_id).first()
        if profile:
            profile.literacy_level = level
            profile.total_points += total_score
            db.commit()

        # Create or Update LearningPath record
        existing_path = db.query(models.LearningPath).filter(models.LearningPath.learner_id == payload.learner_id).first()
        if not existing_path:
            db_path = models.LearningPath(
                learner_id=payload.learner_id,
                target_proficiency=target_level,
                current_level=level,
                status="ACTIVE"
            )
            db.add(db_path)
            db.commit()

    return {
        "status": "success",
        "total_score": total_score,
        "skill_breakdown": {
            "reading_score": reading_score,
            "comprehension_score": comprehension_score,
            "voice_score": voice_score
        },
        "proficiency_level": level,
        "learning_path": learning_path
    }

@router.get("/benchmarks")
def get_proficiency_benchmarks(db: Session = Depends(get_db)):
    return [
        {"level_name": "FOUNDATIONAL", "min_score": 0, "max_score": 49, "description": "Basic letter recognition, phonics, and initial sounds"},
        {"level_name": "FUNCTIONAL", "min_score": 50, "max_score": 79, "description": "Everyday signs, ATM screens, prescription reading & basic speech"},
        {"level_name": "PROFICIENT", "min_score": 80, "max_score": 100, "description": "Workplace literacy, complex text comprehension & speech fluency"}
    ]
