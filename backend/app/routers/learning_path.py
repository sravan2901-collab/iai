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
                "id": 1, "milestone_number": 1, "title": "Alphabets & Phonics and Everyday Greetings",
                "description": "Master letter-sound associations, long/short vowels, and consonant blends.",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "Alphabets & Phonics Fundamentals", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "Everyday Greetings & Basic Vocabulary", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "ATM & Banking, Health & Prescription, Digital Payment",
                "description": "Expand functional vocabulary, master ATM PIN entry, medical prescriptions, and digital transactions.",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "ATM & Banking Functional Reading", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "Health & Medical Prescription Literacy", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "Digital Payment & Receipt Confirmation", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "Workplace Communication & Customer Service Dialogue",
                "description": "Comprehend complex workplace dialogues and express thoughts fluently.",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "Workplace Communication & Professional Greetings", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "Customer Service Dialogue & Voice Practice", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "te": {
        "path_title": "తెలుగు భాషా అక్షరాస్యత కార్యాచరణ సాధన",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "అక్షరాలు, వర్ణమాల మరియు దైనందిన శుభాకాంక్షలు",
                "description": "అచ్చులు, హల్లులు, గుణింతపు గుర్తులు మరియు ఒత్తుల ఉచ్చారణలో నైపుణ్యం సాధించండి.",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "వర్ణమాల మరియు హల్లుల ఉచ్చారణ", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "దైనందిన సంభాషణ మరియు శుభాకాంక్షలు", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "ఏటీఎం బ్యాంకింగ్, వైద్య ప్రిస్క్రిప్షన్ మరియు డిజిటల్ చెల్లింపులు",
                "description": "ఏటీఎం వాడకం, వైద్య ప్రిస్క్రిప్షన్ పఠనం మరియు డిజిటల్ చెల్లింపుల పరిజ్ఞానం.",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "ఏటీఎం మరియు బ్యాంకింగ్ పరిజ్ఞానం", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "వైద్య చికిత్స మరియు ప్రిస్క్రిప్షన్ పఠనం", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "డిజిటల్ చెల్లింపు మరియు రసీదు నిర్ధారణ", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "కార్యాలయ సంభాషణ మరియు వినియోగదారుల సేవా సంభాషణ",
                "description": "కార్యాలయ వృత్తిపరమైన సంభాషణ మరియు మాట్లాడే నైపుణ్యం.",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "కార్యాలయ వృత్తిపరమైన మాట్లాడే పరిజ్ఞానం", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "వినియోగదారుల సేవా సంభాషణ సాధన", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "hi": {
        "path_title": "हिन्दी भाषा साक्षरता मार्गदर्शिका",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "वर्णमाला, स्वर एवं दैनिक अभिवादन",
                "description": "स्वर, व्यंजन, मात्राएँ एवं वर्ण संयोजन में दक्षता प्राप्त करें।",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "वर्णमाला एवं स्वर उच्चारण", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "दैनिक बातचीत एवं अभिवादन", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "एटीएम बैंकिंग, स्वास्थ्य पर्चा एवं डिजिटल भुगतान",
                "description": "एटीएम उपयोग, स्वास्थ्य पर्चा वाचन एवं डिजिटल भुगतान ज्ञान।",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "एटीएम एवं बैंकिंग साक्षरता", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "चिकित्सा एवं पर्चा वाचन", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "डिजिटल भुगतान एवं रसीद पुष्टि", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "कार्यस्थल संचार एवं ग्राहक सेवा संवाद",
                "description": "कार्यस्थल पेशेवर भाषा वाचन और धाराप्रवाह अभिव्यक्ति।",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "कार्यस्थल पेशेवर भाषा वाचन", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "ग्राहक सेवा संवाद एवं वाचन अभ्यास", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "ta": {
        "path_title": "தமிழ் மொழி கற்றல் பாதை",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "எழுத்துக்கள், உச்சரிப்பு மற்றும் அன்றாட வாழ்த்துக்கள்",
                "description": "எழுத்துக்கள் மற்றும் உச்சரிப்பு பயிற்சி.",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "எழுத்துக்கள் மற்றும் உச்சரிப்பு பயிற்சி", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "அன்றாட வாழ்த்துக்கள் மற்றும் சொற்கள்", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "ஏடிஎம் வங்கி, மருத்துவ குறிப்பு மற்றும் டிஜிட்டல் செலுத்தல்",
                "description": "ஏடிஎம் மற்றும் வங்கி வாசிப்பு அறிவு.",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "ஏடிஎம் மற்றும் வங்கி வாசிப்பு", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "மருத்துவ மருந்து சீட்டு வாசிப்பு", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "டிஜிட்டல் பணம் செலுத்துதல் உறுதிப்படுத்தல்", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "அலுவலக உரையாடல் மற்றும் வாடிக்கையாளர் சேவை",
                "description": "அலுவலக தொடர்பு மற்றும் வாடிக்கையாளர் சேவை பயிற்சி.",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "அலுவலக தொடர்பு பயிற்சி", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "வாடிக்கையாளர் சேவை பேச்சு பயிற்சி", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "bn": {
        "path_title": "বাংলা ভাষা সাক্ষরতা পথচিত্র",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "বর্ণমালা, স্বরধ্বনি এবং দৈনন্দিন সম্ভাষণ",
                "description": "বর্ণমালা ও মৌলিক উচ্চারণ ধারণা।",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "বর্ণমালা ও মৌলিক উচ্চারণ", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "দৈনন্দিন সম্ভাষণ ও পরিচিতি", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "এটিএম ব্যাংকিং, প্রেসক্রিপশন এবং ডিজিটাল পেমেন্ট",
                "description": "এটিএম ও ব্যাংকিং এবং প্রেসক্রিপশন পঠন।",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "এটিএম ও ব্যাংকিং পঠন", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "চিকিৎসা ও প্রেসক্রিপশন পঠন", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "ডিজিটাল পেমেন্ট ও রশিদ নিশ্চিতকরণ", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "কর্মক্ষেত্রের কথোপকথন এবং গ্রাহক সেবা বাক্য",
                "description": "কর্মক্ষেত্রের পেশাদার বাক্য ও বাচন চর্চা।",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "কর্মক্ষেত্রের পেশাদার বাক্য অনুশীলন", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "গ্রাহক সেবা বাক্য ও বাচন চর্চা", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "mr": {
        "path_title": "मराठी भाषा साक्षरता मार्गदर्शिका",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "वर्णमाला, स्वर व दैनंदिन नमस्कार",
                "description": "वर्णमाला व मूळाक्षरे उच्चार सराव.",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "वर्णमाला व मूळाक्षरे उच्चार", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "दैनंदिन संवाद व नमस्कार", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "एटीएम बँकिंग, औषध चिठ्ठी व डिजिटल पेमेंट",
                "description": "एटीएम व बँकिंग आणि औषध चिठ्ठी वाचन ज्ञान.",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "एटीएम व बँकिंग वाचन", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "आरोग्य व औषध चिठ्ठी वाचन", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "डिजिटल पेमेंट व पावती खात्री", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "कामाच्या ठिकाणचा संवाद व ग्राहक सेवा संभाषण",
                "description": "व्यावसायिक संवाद व ग्राहक सेवा सराव.",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "व्यावसायिक संवाद व संभाषण", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "ग्राहक सेवा संभाषण व वाचन सराव", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "kn": {
        "path_title": "ಕನ್ನಡ ಭಾಷಾ ಸಾಕ್ಷರತಾ ಮಾರ್ಗಸೂಚಿ",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "ಅಕ್ಷರಮಾಲೆ, ಸ್ವರಗಳು ಮತ್ತು ದೈನಂದಿನ ಶುಭಾಶಯಗಳು",
                "description": "ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಉಚ್ಚಾರಣೆ ಅಭ್ಯಾಸ.",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಉಚ್ಚಾರಣೆ ಅಭ್ಯಾಸ", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "ದೈನಂದಿನ ಶುಭಾಶಯಗಳು ಮತ್ತು ಪದಗಳು", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "ಎಟಿಎಂ ಬ್ಯಾಂಕಿಂಗ್, ವೈದ್ಯಕೀಯ ಚೀಟಿ ಮತ್ತು ಡಿಜಿಟಲ್ ಪಾವತಿ",
                "description": "ಎಟಿಎಂ ಮತ್ತು ಬ್ಯಾಂಕಿಂಗ್ ಓದುವಿಕೆ ಜ್ಞಾನ.",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "ಎಟಿಎಂ ಮತ್ತು ಬ್ಯಾಂಕಿಂಗ್ ಓದುವಿಕೆ", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "ವೈದ್ಯಕೀಯ ಚೀಟಿ ಓದುವಿಕೆ", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "ಡಿಜಿಟಲ್ ಪಾವತಿ ಮತ್ತು ರಶೀದಿ ದೃಢೀಕರಣ", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "ಉದ್ಯೋಗಸ್ಥಳದ ಸಂವಹನ ಮತ್ತು ಗ್ರಾಹಕ ಸೇವಾ ಸಂಭಾಷಣೆ",
                "description": "ವೃತ್ತಿಪರ ಮಾತನಾಡುವ ಅಭ್ಯಾಸ.",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "ವೃತ್ತಿಪರ ಮಾತನಾಡುವ ಅಭ್ಯಾಸ", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "ಗ್ರಾಹಕ ಸೇವಾ ಸಂಭಾಷಣೆ ಅಭ್ಯಾಸ", "status": "LOCKED", "score": 0}
                ]
            }
        ]
    },
    "es": {
        "path_title": "Ruta de Alfabetización en Idioma Español",
        "milestones": [
            {
                "id": 1, "milestone_number": 1, "title": "Alfabeto, Fonética y Saludos Cotidianos",
                "description": "Dominio del alfabeto, asociación de sonidos y saludos cotidianos.",
                "progress_percentage": 100, "is_completed": True, "status": "COMPLETED",
                "lessons": [
                    {"id": 1, "title": "Fundamentos del Alfabeto y Fonética", "status": "COMPLETED", "score": 95},
                    {"id": 2, "title": "Saludos Cotidianos y Vocabulario Básico", "status": "COMPLETED", "score": 90}
                ]
            },
            {
                "id": 2, "milestone_number": 2, "title": "Cajero Automático, Salud y Pagos Digitales",
                "description": "Lectura funcional de cajero automático, recetas médicas y pagos digitales.",
                "progress_percentage": 40, "is_completed": False, "status": "IN_PROGRESS",
                "lessons": [
                    {"id": 3, "title": "Lectura Funcional de Cajero y Banco", "status": "COMPLETED", "score": 85},
                    {"id": 4, "title": "Lectura de Recetas Médicas", "status": "IN_PROGRESS", "score": 0},
                    {"id": 5, "title": "Confirmación de Pagos Digitales y Recibos", "status": "LOCKED", "score": 0}
                ]
            },
            {
                "id": 3, "milestone_number": 3, "title": "Comunicación Laboral y Servicio al Cliente",
                "description": "Comprensión de diálogos laborales y articulación fluida.",
                "progress_percentage": 0, "is_completed": False, "status": "LOCKED",
                "lessons": [
                    {"id": 6, "title": "Comunicación Profesional en el Trabajo", "status": "LOCKED", "score": 0},
                    {"id": 7, "title": "Diálogo de Servicio al Cliente y Práctica de Voz", "status": "LOCKED", "score": 0}
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

    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == learner_id,
        models.LearningPath.status == "ACTIVE"
    ).order_by(models.LearningPath.path_id.desc()).first()
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

def trigger_adaptive_replanning(learner_id: int, path: models.LearningPath, db: Session):
    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner_id).first()
    if not profile:
        return False, "No profile found"

    # Step 3.3: Recalculate reading_pct, comprehension_pct, voice_pct from recent scores
    recent_voice = db.query(models.PronunciationScore).join(models.VoiceSession).filter(
        models.VoiceSession.learner_id == learner_id
    ).order_by(models.PronunciationScore.score_id.desc()).limit(5).all()

    if recent_voice:
        profile.voice_pct = round(sum(s.overall_score for s in recent_voice) / len(recent_voice), 1)

    r_pct = profile.reading_pct or 0.0
    c_pct = profile.comprehension_pct or 0.0
    v_pct = profile.voice_pct or 0.0

    skills = {"READING": r_pct, "COMPREHENSION": c_pct, "VOICE": v_pct}
    new_weakest_skill = min(skills, key=skills.get)
    new_weakest_score = skills[new_weakest_skill]

    if new_weakest_skill == "READING":
        skill_keywords = ["READING", "Phonics", "Alphabet", "Greetings"]
    elif new_weakest_skill == "COMPREHENSION":
        skill_keywords = ["COMPREHENSION", "ATM", "Banking", "Health", "Prescription", "Digital"]
    else:
        skill_keywords = ["VOICE", "Workplace", "Customer Service", "Dialogue"]

    locked_path_lessons = db.query(models.PathLesson).filter(
        models.PathLesson.path_id == path.path_id,
        models.PathLesson.status == "LOCKED"
    ).all()

    if not locked_path_lessons:
        return False, "No locked lessons to re-order"

    def is_weak_module(pl):
        m = pl.lesson.module
        m_skill = (m.skill_type or "").upper()
        m_name = (m.module_name or "").upper()
        return any(k.upper() in m_skill or k.upper() in m_name for k in skill_keywords)

    weak_locked = [pl for pl in locked_path_lessons if is_weak_module(pl)]
    other_locked = [pl for pl in locked_path_lessons if not is_weak_module(pl)]
    reordered_locked = weak_locked + other_locked

    base_seq = min(pl.sequence_no for pl in locked_path_lessons)
    for idx, pl in enumerate(reordered_locked):
        pl.sequence_no = base_seq + idx

    db.commit()

    reason = f"Adaptive Re-Planning Triggered! Recent performance update: {new_weakest_skill} is now lowest ({new_weakest_score}%). Re-ordered upcoming locked lessons to prioritize {new_weakest_skill} mastery."
    return True, reason

def complete_lesson_workflow(
    learner_id: int,
    lesson_id: int,
    score: float,
    db: Session,
    award_points: bool = True,
    path_lesson_id: Optional[int] = None
):
    lesson = db.query(models.Lesson).filter(models.Lesson.lesson_id == lesson_id).first()
    if not lesson:
        return None

    module_id = lesson.module_id

    path = db.query(models.LearningPath).filter(
        models.LearningPath.learner_id == learner_id,
        models.LearningPath.status == "ACTIVE"
    ).order_by(models.LearningPath.path_id.desc()).first()
    if not path:
        return None

    if path_lesson_id:
        path_lesson = db.query(models.PathLesson).filter(
            models.PathLesson.path_lesson_id == path_lesson_id,
            models.PathLesson.path_id == path.path_id
        ).first()
    else:
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

        uncompleted_path_lessons = db.query(models.PathLesson).filter(
            models.PathLesson.path_id == path.path_id,
            models.PathLesson.status == "LOCKED"
        ).order_by(models.PathLesson.sequence_no).all()

        if uncompleted_path_lessons:
            uncompleted_path_lessons[0].status = "UNLOCKED"
            if len(uncompleted_path_lessons) > 1 and uncompleted_path_lessons[1].lesson.module_id == uncompleted_path_lessons[0].lesson.module_id:
                uncompleted_path_lessons[1].status = "UNLOCKED"
            db.commit()

        profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner_id).first()
        if profile:
            recent_scores = db.query(models.PronunciationScore).join(models.VoiceSession).filter(
                models.VoiceSession.learner_id == learner_id
            ).order_by(models.PronunciationScore.score_id.desc()).limit(5).all()

            if recent_scores:
                avg_voice = sum(s.overall_score for s in recent_scores) / len(recent_scores)
                profile.voice_pct = round(avg_voice, 1)

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

    # Gamification: Update points (if enabled), streak, and check achievements
    from app.services.gamification_service import update_streak, check_and_award_achievements

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner_id).first()
    if profile and award_points:
        profile.total_points = (profile.total_points or 0) + int(score / 10)
        db.commit()

    update_streak(learner_id, db)
    achievements_unlocked = check_and_award_achievements(learner_id, db)

    # Step 3.3: Re-Planning Trigger (After every 3 completed lessons OR module completion)
    replanned = False
    replan_reason = ""
    if completed_path_count % 3 == 0 or is_milestone_completed:
        replanned, replan_reason = trigger_adaptive_replanning(learner_id, path, db)

    return {
        "path_id": path.path_id,
        "lesson_id": lesson_id,
        "status": "COMPLETED",
        "milestone_completed": is_milestone_completed,
        "module_completion_pct": module_completion_pct,
        "path_completion_pct": path.completion_percentage,
        "current_level": path.current_level,
        "replanned": replanned,
        "replan_reason": replan_reason,
        "achievements_unlocked": achievements_unlocked
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
