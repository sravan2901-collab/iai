from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from app.database import get_db
from app import models, schemas
from app.auth import get_optional_current_learner

router = APIRouter(prefix="/api/recommendations", tags=["AI Personalized Learning Engine (Milestone 2)"])

MULTI_LANG_RECOMMENDATIONS = {
    "en": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "Alphabets & Phonics Fundamentals", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "Everyday Greetings & Basic Vocabulary", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "ATM & Banking Functional Reading", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "Reading score is below 50%. Recommendation model prioritized Phonics & Alphabet sound association to build foundational literacy."
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "ATM & Banking Functional Reading", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "Health & Medical Prescription Literacy", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "Digital Payment & Receipt Confirmation", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "Comprehension score is below 50%. Recommendation model prioritized practical functional reading scenarios (ATM & Prescription reading)."
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "Workplace Communication & Professional Greetings", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "Customer Service Dialogue & Voice Practice", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "Phoneme Articulation Coach", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "Voice score is below 50%. Recommendation model prioritized speech pronunciation coaching and conversational dialogue scenarios."
        }
    },
    "te": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "అక్షరాలు, వర్ణమాల మరియు ఉచ్చారణ", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "దైనందిన సంభాషణ మరియు శుభాకాంక్షలు", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "ఏటీఎం మరియు బ్యాంకింగ్ పరిజ్ఞానం", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "చదవడం స్కోరు 50% కంటే తక్కువగా ఉంది. అక్షర గుర్తింపు మరియు ఉచ్చారణ సాధనకు ప్రాధాన్యత ఇవ్వబడింది."
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "ఏటీఎం మరియు బ్యాంకింగ్ పరిజ్ఞానం", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "వైద్య చికిత్స మరియు ప్రిస్క్రిప్షన్ పఠనం", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "డిజిటల్ చెల్లింపు మరియు రసీదు నిర్ధారణ", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "అర్థం చేసుకోవడం స్కోరు తక్కువగా ఉంది. రోజువారీ ఉపయోగకరమైన ఏటీఎం మరియు వైద్య పఠనానికి ప్రాధాన్యత ఇవ్వబడింది."
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "కార్యాలయ వృత్తిపరమైన మాట్లాడే పరిజ్ఞానం", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "వినియోగదారుల సేవా సంభాషణ సాధన", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "ధ్వని ఉచ్చారణ శిక్షణ", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "మాట్లాడటం స్కోరు 50% కంటే తక్కువగా ఉంది. స్పష్టమైన మాట్లాడే సంభాషణల సాధనకు ప్రాధాన్యత ఇవ్వబడింది."
        }
    },
    "hi": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "वर्णमाला एवं स्वर उच्चारण", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "दैनिक बातचीत एवं अभिवादन", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "एटीएम एवं बैंकिंग साक्षरता", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "पठन स्कोर 50% से कम है। सिफारिश मॉडल ने अक्षर पहचान और स्वर उच्चारण को प्राथमिकता दी है।"
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "एटीएम एवं बैंकिंग साक्षरता", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "चिकित्सा एवं पर्चा वाचन", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "डिजिटल भुगतान एवं रसीद पुष्टि", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "बोधगम्यता स्कोर कम है। व्यावहारिक एटीएम बैंकिंग एवं पर्चा वाचन को प्राथमिकता दी गई है।"
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "कार्यस्थल पेशेवर भाषा वाचन", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "ग्राहक सेवा संवाद एवं वाचन अभ्यास", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "ध्वनि उच्चारण कोचिंग", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "वाचन स्कोर 50% से कम है। सिफारिश मॉडल ने संवाद वाचन और उच्चारण अभ्यास को प्राथमिकता दी है।"
        }
    },
    "ta": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "எழுத்துக்கள் மற்றும் உச்சரிப்பு பயிற்சி", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "அன்றாட வாழ்த்துக்கள் மற்றும் சொற்கள்", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "ஏடிஎம் மற்றும் வங்கி வாசிப்பு", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "வாசிப்பு மதிப்பெண் 50% க்கும் குறைவாக உள்ளது. எழுத்து அறிமுகம் மற்றும் உச்சரிப்புக்கு முன்னுரிமை அளிக்கப்பட்டது."
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "ஏடிஎம் மற்றும் வங்கி வாசிப்பு", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "மருத்துவ மருந்து சீட்டு வாசிப்பு", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "டிஜிட்டல் பணம் செலுத்துதல் உறுதிப்படுத்தல்", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "புரிதல் மதிப்பெண் குறைவாக உள்ளது. அன்றாட ஏடிஎம் மற்றும் மருத்துவ வாசிப்புக்கு முன்னுரிமை அளிக்கப்பட்டது."
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "அலுவலக தொடர்பு பயிற்சி", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "வாடிக்கையாளர் சேவை பேச்சு பயிற்சி", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "ஒலி உச்சரிப்பு பயிற்சி", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "பேச்சு மதிப்பெண் 50% க்கும் குறைவாக உள்ளது. தெளிவான உரையாடல் பேச்சு பயிற்சிக்கு முன்னுரிமை அளிக்கப்பட்டது."
        }
    },
    "bn": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "বর্ণমালা ও মৌলিক উচ্চারণ", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "দৈনন্দিন সম্ভাষণ ও পরিচিতি", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "এটিএম ও ব্যাংকিং পঠন", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "পঠন স্কোর ৫০% এর নিচে। বর্ণ চেনার জন্য উচ্চারণ ও বর্ণমালায় প্রাধান্য দেওয়া হয়েছে।"
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "এটিএম ও ব্যাংকিং পঠন", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "চিকিৎসা ও প্রেসক্রিপশন পঠন", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "ডিজিটাল পেমেন্ট ও রশিদ নিশ্চিতকরণ", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "বোঝার স্কোর কম। ব্যবহারিক এটিএম ও চিকিৎসা সংক্রান্ত পঠনে অগ্রাধিকার দেওয়া হয়েছে।"
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "কর্মক্ষেত্রের পেশাদার বাক্য অনুশীলন", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "গ্রাহক সেবা বাক্য ও বাচন চর্চা", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "উচ্চারণ কোচিং", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "বাচন স্কোর ৫০% এর নিচে। স্পষ্ট বাক্য উচ্চারণ চর্চায় অগ্রাধিকার দেওয়া হয়েছে।"
        }
    },
    "mr": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "वर्णमाला व मूळाक्षरे उच्चार", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "दैनंदिन संवाद व नमस्कार", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "एटीएम व बँकिंग वाचन", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "वाचन गुण ५०% पेक्षा कमी आहेत. मूळाक्षरे ओळख आणि उच्चार सरावाला प्राधान्य दिले आहे."
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "एटीएम व बँकिंग वाचन", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "आरोग्य व औषध चिठ्ठी वाचन", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "डिजिटल पेमेंट व पावती खात्री", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "आकलन गुण कमी आहेत. व्यवहारातील एटीएम व औषध चिठ्ठी वाचनाला प्राधान्य दिले गेले आहे."
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "व्यावसायिक संवाद व संभाषण", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "ग्राहक सेवा संभाषण व वाचन सराव", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "उच्चार सराव कोचिंग", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "उच्चार गुण ५०% पेक्षा कमी आहेत. स्पष्ट संभाषण सरावाला प्राधान्य दिले आहे."
        }
    },
    "kn": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಉಚ್ಚಾರಣೆ ಅಭ್ಯಾಸ", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "ದೈನಂದಿನ ಶುಭಾಶಯಗಳು ಮತ್ತು ಪದಗಳು", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "ಎಟಿಎಂ ಮತ್ತು ಬ್ಯಾಂಕಿಂಗ್ ಓದುವಿಕೆ", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "ಓದುವ ಅಂಕ 50% ಕ್ಕಿಂತ ಕಡಿಮೆಯಿದೆ. ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ ಮತ್ತು ಉಚ್ಚಾರಣೆಗೆ ಆದ್ಯತೆ ನೀಡಲಾಗಿದೆ."
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "ಎಟಿಎಂ ಮತ್ತು ಬ್ಯಾಂಕಿಂಗ್ ಓದುವಿಕೆ", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "ವೈದ್ಯಕೀಯ ಚೀಟಿ ಓದುವಿಕೆ", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "ಡಿಜಿಟಲ್ ಪಾವತಿ ಮತ್ತು ರಶೀದಿ ದೃಢೀಕರಣ", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "ಅರ್ಥೈಸಿಕೊಳ್ಳುವಿಕೆ ಅಂಕ ಕಡಿಮೆಯಿದೆ. ಪ್ರಾಯೋಗಿಕ ಎಟಿಎಂ ಮತ್ತು ವೈದ್ಯಕೀಯ ಚೀಟಿ ಓದುವಿಕೆಗೆ ಆದ್ಯತೆ ನೀಡಲಾಗಿದೆ."
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "ವೃತ್ತಿಪರ ಮಾತನಾಡುವ ಅಭ್ಯಾಸ", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "ಗ್ರಾಹಕ ಸೇವಾ ಸಂಭಾಷಣೆ ಅಭ್ಯಾಸ", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "ಧ್ವನಿ ಉಚ್ಚಾರಣೆ ತರಬೇತಿ", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "ಮಾತನಾಡುವ ಅಂಕ 50% ಕ್ಕಿಂತ ಕಡಿಮೆಯಿದೆ. ಸ್ಪಷ್ಟ ಸಂಭಾಷಣೆ ಅಭ್ಯಾಸಕ್ಕೆ ಆದ್ಯತೆ ನೀಡಲಾಗಿದೆ."
        }
    },
    "es": {
        "READING": {
            "modules": [
                {"module_id": 1, "title": "Fundamentos del Alfabeto y Fonética", "skill_type": "READING", "priority_weight": 0.95},
                {"module_id": 2, "title": "Saludos Cotidianos y Vocabulario Básico", "skill_type": "READING", "priority_weight": 0.85},
                {"module_id": 3, "title": "Lectura Funcional de Cajero y Banco", "skill_type": "COMPREHENSION", "priority_weight": 0.60}
            ],
            "rationale": "El puntaje de lectura es inferior al 50%. El modelo recomendó fonética y asociación de sonidos para construir alfabetización básica."
        },
        "COMPREHENSION": {
            "modules": [
                {"module_id": 1, "title": "Lectura Funcional de Cajero y Banco", "skill_type": "COMPREHENSION", "priority_weight": 0.95},
                {"module_id": 2, "title": "Lectura de Recetas Médicas", "skill_type": "COMPREHENSION", "priority_weight": 0.90},
                {"module_id": 3, "title": "Confirmación de Pagos Digitales y Recibos", "skill_type": "COMPREHENSION", "priority_weight": 0.80}
            ],
            "rationale": "El puntaje de comprensión es bajo. El modelo priorizó lecturas prácticas funcionales (Cajero automático y recetas médicas)."
        },
        "VOICE": {
            "modules": [
                {"module_id": 1, "title": "Comunicación Profesional en el Trabajo", "skill_type": "VOICE", "priority_weight": 0.95},
                {"module_id": 2, "title": "Diálogo de Servicio al Cliente y Práctica de Voz", "skill_type": "VOICE", "priority_weight": 0.90},
                {"module_id": 3, "title": "Entrenador de Articulación Fonética", "skill_type": "VOICE", "priority_weight": 0.80}
            ],
            "rationale": "El puntaje de voz es inferior al 50%. El modelo priorizó el entrenamiento de pronunciación y diálogos conversacionales."
        }
    }
}

@router.get("/adaptive-plan", response_model=schemas.AdaptiveRecommendationOut)
def get_adaptive_learning_recommendation(
    lang: Optional[str] = Query(None, description="ISO language code (e.g. en, te, hi, ta, bn, mr, kn, es)"),
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    if not profile:
        profile = models.LearnerProfile(
            learner_id=learner.learner_id,
            first_name=learner.username,
            literacy_level="FOUNDATIONAL",
            reading_pct=45.0,
            comprehension_pct=60.0,
            voice_pct=55.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    r_pct = profile.reading_pct or 0.0
    c_pct = profile.comprehension_pct or 0.0
    v_pct = profile.voice_pct or 0.0

    skills = {
        "READING": r_pct,
        "COMPREHENSION": c_pct,
        "VOICE": v_pct
    }

    weakest_skill = min(skills, key=skills.get)

    # Variance and Confidence Score
    variance = sum((val - (r_pct + c_pct + v_pct)/3.0)**2 for val in skills.values()) / 3.0
    confidence = round(min(0.98, max(0.65, 0.75 + math.sqrt(variance)/100.0)), 2)

    # Multi-lingual language code determination
    if lang:
        target_iso = lang.lower()
    else:
        lang_id = learner.current_lang_id or 1
        lang_obj = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
        target_iso = lang_obj.iso_code if lang_obj else "en"

    lang_data = MULTI_LANG_RECOMMENDATIONS.get(target_iso, MULTI_LANG_RECOMMENDATIONS["en"])
    recommendation_item = lang_data.get(weakest_skill, lang_data["READING"])

    return {
        "learner_id": learner.learner_id,
        "primary_focus_skill": weakest_skill,
        "confidence_score": confidence,
        "reading_pct": r_pct,
        "comprehension_pct": c_pct,
        "voice_pct": v_pct,
        "recommended_modules": recommendation_item["modules"],
        "rationale": recommendation_item["rationale"]
    }

@router.get("/predict-proficiency", response_model=schemas.ProficiencyPredictionOut)
def predict_learner_proficiency(
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    current_lvl = profile.literacy_level if profile else "FOUNDATIONAL"
    r_pct = profile.reading_pct if profile else 50.0
    c_pct = profile.comprehension_pct if profile else 50.0
    v_pct = profile.voice_pct if profile else 50.0

    avg_score = (r_pct + c_pct + v_pct) / 3.0

    if current_lvl == "FOUNDATIONAL":
        next_lvl = "FUNCTIONAL"
        days = max(3, int((75.0 - avg_score) * 0.4)) if avg_score < 75.0 else 1
    elif current_lvl == "FUNCTIONAL":
        next_lvl = "PROFICIENT"
        days = max(5, int((90.0 - avg_score) * 0.5)) if avg_score < 90.0 else 2
    else:
        next_lvl = "MASTERY"
        days = 0

    growth_rate = round(min(15.0, max(2.5, (avg_score / 10.0) + (profile.streak_count if profile else 1) * 0.5)), 1)

    return {
        "learner_id": learner.learner_id,
        "current_level": current_lvl,
        "predicted_next_level": next_lvl,
        "estimated_days_to_mastery": days,
        "accuracy_growth_rate": growth_rate,
        "skill_breakdown": {
            "reading": r_pct,
            "comprehension": c_pct,
            "voice": v_pct,
            "composite_average": round(avg_score, 1)
        }
    }

@router.post("/personalized-lessons", response_model=schemas.PersonalizedLessonOut)
def generate_personalized_lesson(
    skill_type: Optional[str] = None,
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    lang_id = learner.current_lang_id or 1
    lang = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
    iso = lang.iso_code if lang else "en"

    if not skill_type:
        skills = {
            "READING": profile.reading_pct or 0.0 if profile else 50.0,
            "COMPREHENSION": profile.comprehension_pct or 0.0 if profile else 50.0,
            "VOICE": profile.voice_pct or 0.0 if profile else 50.0
        }
        skill_type = min(skills, key=skills.get)

    level = profile.literacy_level if profile else "FOUNDATIONAL"

    if skill_type == "READING":
        exercise = {
            "lesson_id": f"gen_read_{learner.learner_id}",
            "target_skill": "READING",
            "language_code": iso,
            "difficulty": level,
            "exercise_type": "PHONICS_FLASHCARD",
            "title": "Adaptive Phonics & Syllable Trainer",
            "instructions": "Listen to the letter sound and select the matching word.",
            "practice_content": [
                {"symbol": "A / அ / अ", "sound_prompt": "apple", "options": ["Apple", "Ball", "Cat"], "correct": "Apple"},
                {"symbol": "B / ಬ / ব", "sound_prompt": "ball", "options": ["Dog", "Ball", "Elephant"], "correct": "Ball"}
            ]
        }
    elif skill_type == "COMPREHENSION":
        exercise = {
            "lesson_id": f"gen_comp_{learner.learner_id}",
            "target_skill": "COMPREHENSION",
            "language_code": iso,
            "difficulty": level,
            "exercise_type": "FUNCTIONAL_CONTEXT_READING",
            "title": "ATM & Financial Literacy Scenario",
            "instructions": "Read the receipt details and answer the comprehension question.",
            "practice_content": [
                {"passage": "ATM Withdrawal Receipt: Amount ₹500, Account XXXX1234, Balance ₹4,500", "question": "What is the remaining account balance?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        }
    else:
        exercise = {
            "lesson_id": f"gen_voice_{learner.learner_id}",
            "target_skill": "VOICE",
            "language_code": iso,
            "difficulty": level,
            "exercise_type": "PRONUNCIATION_COACH",
            "title": "Professional Speech Articulation",
            "instructions": "Tap microphone and speak the prompt phrase clearly.",
            "practice_content": [
                {"prompt_phrase": "Good morning, how can I help you today?", "target_phonemes": ["g", "d", "m", "n", "ng"]}
            ]
        }

    return exercise

@router.get("/recommended-content", response_model=List[schemas.ContentRecommendationOut])
def get_recommended_content(
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    v_pct = profile.voice_pct if profile else 50.0
    r_pct = profile.reading_pct if profile else 50.0

    return [
        {
            "category": "Interactive Speech Coach",
            "title": "Customer Service Dialogue Audio Practice",
            "skill_type": "VOICE",
            "relevance_score": 0.96 if v_pct < 60 else 0.75,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "Hello, welcome to our office."}
        },
        {
            "category": "Functional Literacy Flashcards",
            "title": "Medical Prescription & Pharmacy Signs",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "Health"}
        },
        {
            "category": "Phonics Mastery",
            "title": "Vowel Blends & Consonant Clusters",
            "skill_type": "READING",
            "relevance_score": 0.88 if r_pct < 60 else 0.70,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ]
