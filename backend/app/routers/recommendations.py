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

NATIVE_LEVEL_TRANSLATIONS = {
    "en": {
        "FOUNDATIONAL": "Foundational Literacy",
        "FUNCTIONAL": "Functional Literacy",
        "PROFICIENT": "Proficient Literacy",
        "MASTERY": "Advanced Mastery",
        "summary_tpl": "Based on current learning velocity, learner is projected to reach {next_lvl} in {days} days with a {growth}% weekly accuracy growth rate."
    },
    "te": {
        "FOUNDATIONAL": "ప్రాథమిక అక్షరాస్యత",
        "FUNCTIONAL": "కార్యాచరణ అక్షరాస్యత",
        "PROFICIENT": "నైపుణ్యతా అక్షరాస్యత",
        "MASTERY": "ఉన్నత పాండిత్యం",
        "summary_tpl": "ప్రస్తుత అభ్యాస వేగం ప్రకారం, అభ్యర్థి {days} రోజుల్లో {next_lvl} స్థాయికి చేరుకుంటారని అంచనా వేయబడింది."
    },
    "hi": {
        "FOUNDATIONAL": "बुनियादी साक्षरता",
        "FUNCTIONAL": "कार्यात्मक साक्षरता",
        "PROFICIENT": "प्रवीण साक्षरता",
        "MASTERY": "उच्च दक्षता",
        "summary_tpl": "वर्तमान सीखने की गति के आधार पर, शिक्षार्थी के {days} दिनों में {next_lvl} स्तर तक पहुँचने का अनुमान है।"
    },
    "ta": {
        "FOUNDATIONAL": "அடிப்படை எழுத்தறிவு",
        "FUNCTIONAL": "செயல்பாட்டு எழுத்தறிவு",
        "PROFICIENT": "நிறைவு எழுத்தறிவு",
        "MASTERY": "உயர் தேர்ச்சி",
        "summary_tpl": "தற்போதைய கற்றல் வேகத்தின் அடிப்படையில், கற்பவர் {days} நாட்களில் {next_lvl} நிலையை அடைவார் என கணிக்கப்பட்டுள்ளது."
    },
    "bn": {
        "FOUNDATIONAL": "প্রাথমিক সাক্ষরতা",
        "FUNCTIONAL": "কার্যকরী সাক্ষরতা",
        "PROFICIENT": "দক্ষ সাক্ষরতা",
        "MASTERY": "উচ্চ পাণ্ডিত্য",
        "summary_tpl": "বর্তমান শেখার গতির ওপর ভিত্তি করে, শিক্ষার্থী {days} দিনের মধ্যে {next_lvl} স্তরে পৌঁছাবে বলে অনুমান করা হচ্ছে।"
    },
    "mr": {
        "FOUNDATIONAL": "मूलभूत साक्षरता",
        "FUNCTIONAL": "कार्यात्मक साक्षरता",
        "PROFICIENT": "प्रवीण साक्षरता",
        "MASTERY": "उच्च प्रभुत्व",
        "summary_tpl": "सध्याच्या शिकण्याच्या वेगानुसार, विद्यार्थी {days} दिवसांत {next_lvl} पातळी गाठण्याचा अंदाज आहे."
    },
    "kn": {
        "FOUNDATIONAL": "ಮೂಲಭೂತ ಸಾಕ್ಷರತೆ",
        "FUNCTIONAL": "ಕಾರ್ಯಾತ್ಮಕ ಸಾಕ್ಷರತೆ",
        "PROFICIENT": "ಪ್ರವೀಣ ಸಾಕ್ಷರತೆ",
        "MASTERY": "ಉನ್ನತ ಪಾಂಡಿತ್ಯ",
        "summary_tpl": "ಪ್ರಸ್ತುತ ಕಲಿಕೆಯ ವೇಗದ ಆಧಾರದ ಮೇಲೆ, ಕಲಿಯುವವರು {days} ದಿನಗಳಲ್ಲಿ {next_lvl} ಹಂತವನ್ನು ತಲುಪುತ್ತಾರೆ ಎಂದು ಅಂದಾಜಿಸಲಾಗಿದೆ."
    },
    "es": {
        "FOUNDATIONAL": "Alfabetización Básica",
        "FUNCTIONAL": "Alfabetización Funcional",
        "PROFICIENT": "Alfabetización Avanzada",
        "MASTERY": "Maestría Completa",
        "summary_tpl": "Según el ritmo de aprendizaje actual, se prevé que el estudiante alcance el nivel {next_lvl} en {days} días."
    }
}

@router.get("/predict-proficiency", response_model=schemas.ProficiencyPredictionOut)
def predict_learner_proficiency(
    lang: Optional[str] = Query(None, description="ISO language code (e.g. en, te, hi, ta, bn, mr, kn, es)"),
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

    # Resolve target language for native level translations
    if lang:
        target_iso = lang.lower()
    else:
        lang_id = learner.current_lang_id or 1
        lang_obj = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
        target_iso = lang_obj.iso_code if lang_obj else "en"

    lang_tr = NATIVE_LEVEL_TRANSLATIONS.get(target_iso, NATIVE_LEVEL_TRANSLATIONS["en"])
    native_curr = lang_tr.get(current_lvl, current_lvl)
    native_next = lang_tr.get(next_lvl, next_lvl)

    summary = lang_tr["summary_tpl"].format(next_lvl=native_next, days=days, growth=growth_rate)

    return {
        "learner_id": learner.learner_id,
        "current_level": current_lvl,
        "predicted_next_level": next_lvl,
        "native_current_level": native_curr,
        "native_next_level": native_next,
        "estimated_days_to_mastery": days,
        "accuracy_growth_rate": growth_rate,
        "skill_breakdown": {
            "reading": r_pct,
            "comprehension": c_pct,
            "voice": v_pct,
            "composite_average": round(avg_score, 1)
        },
        "prediction_summary": summary
    }

PERSONALIZED_LESSONS_BY_LANG = {
    "en": {
        "READING": {
            "title": "Adaptive Phonics & Syllable Trainer",
            "instructions": "Listen to the letter sound and select the matching word.",
            "practice_content": [
                {"symbol": "A / a", "sound_prompt": "apple", "options": ["Apple", "Ball", "Cat"], "correct": "Apple"},
                {"symbol": "B / b", "sound_prompt": "ball", "options": ["Dog", "Ball", "Elephant"], "correct": "Ball"}
            ]
        },
        "COMPREHENSION": {
            "title": "ATM & Financial Literacy Scenario",
            "instructions": "Read the receipt details and answer the comprehension question.",
            "practice_content": [
                {"passage": "ATM Withdrawal Receipt: Amount $500, Account XXXX1234, Balance $4,500", "question": "What is the remaining account balance?", "options": ["$500", "$4,500", "$5,000"], "correct": "$4,500"}
            ]
        },
        "VOICE": {
            "title": "Professional Speech Articulation",
            "instructions": "Tap microphone and speak the prompt phrase clearly.",
            "practice_content": [
                {"prompt_phrase": "Good morning, how can I help you today?", "target_phonemes": ["g", "d", "m", "n", "ng"]}
            ]
        }
    },
    "te": {
        "READING": {
            "title": "తెలుగు అక్షరాలు మరియు గుణింతపు సాధన",
            "instructions": "అక్షరం శబ్దాన్ని విని సరైన పదాన్ని ఎంచుకోండి.",
            "practice_content": [
                {"symbol": "అ / ఆ", "sound_prompt": "అమ్మ", "options": ["అమ్మ", "ఆవు", "ఇల్లు"], "correct": "అమ్మ"},
                {"symbol": "క / కా", "sound_prompt": "కాకి", "options": ["కమలం", "కాకి", "కిటికి"], "correct": "కాకి"}
            ]
        },
        "COMPREHENSION": {
            "title": "ఏటీఎం మరియు ఆర్థిక రసీదు పఠనం",
            "instructions": "రసీదు వివరాలను చదివి సరైన సమాధానం ఇవ్వండి.",
            "practice_content": [
                {"passage": "ఏటీఎం ఉపసంహరణ రసీదు: విత్ డ్రా మొత్తం ₹500, మిగిలిన నిల్వ ₹4,500", "question": "ఖాతాలో మిగిలిన నిల్వ ఎంత?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        },
        "VOICE": {
            "title": "స్పష్టమైన మాట్లాడే ఉచ్చారణ సాధన",
            "instructions": "మైక్రోఫోన్ నొక్కి వాక్యాన్ని స్పష్టంగా ఉచ్చరించండి.",
            "practice_content": [
                {"prompt_phrase": "శుభోదయం, నేటి పని లక్ష్యాలను చర్చిద్దాం", "target_phonemes": ["శు", "భో", "ద", "యం"]}
            ]
        }
    },
    "hi": {
        "READING": {
            "title": "हिंदी अक्षर एवं मात्रा वाचन अभ्यास",
            "instructions": "अक्षर की ध्वनि सुनें और सही शब्द चुनें।",
            "practice_content": [
                {"symbol": "अ / आ", "sound_prompt": "अनार", "options": ["अनार", "आम", "इमली"], "correct": "अनार"},
                {"symbol": "क / का", "sound_prompt": "कमल", "options": ["कमल", "कागज", "किताब"], "correct": "कमल"}
            ]
        },
        "COMPREHENSION": {
            "title": "एटीएम एवं वित्तीय रसीद वाचन",
            "instructions": "रसीद का विवरण पढ़ें और प्रश्न का उत्तर दें।",
            "practice_content": [
                {"passage": "एटीएम निकासी रसीद: राशि ₹500, शेष राशि ₹4,500", "question": "खाते में शेष राशि कितनी है?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        },
        "VOICE": {
            "title": "स्पष्ट वाचन एवं उच्चारण अभ्यास",
            "instructions": "माइक दबाएं और वाक्य को स्पष्ट रूप से बोलें।",
            "practice_content": [
                {"prompt_phrase": "नमस्ते, मैं आपकी क्या सहायता कर सकता हूँ", "target_phonemes": ["न", "म", "स्", "ते"]}
            ]
        }
    },
    "ta": {
        "READING": {
            "title": "தமிழ் எழுத்து மற்றும் உச்சரிப்பு பயிற்சி",
            "instructions": "எழுத்தின் ஒலியைக் கேட்டு சரியான சொல்லைத் தேர்ந்தெடுக்கவும்.",
            "practice_content": [
                {"symbol": "அ / ஆ", "sound_prompt": "அம்மா", "options": ["அம்மா", "ஆடு", "இலை"], "correct": "அம்மா"}
            ]
        },
        "COMPREHENSION": {
            "title": "ஏடிஎம் மற்றும் வங்கி ரசீது வாசிப்பு",
            "instructions": "ரசீது விவரங்களைப் படித்து சரியான பதிலைக் கூறவும்.",
            "practice_content": [
                {"passage": "ஏடிஎம் பணம் எடுத்தல் ரசீது: தொகை ₹500, மீதி இருப்பு ₹4,500", "question": "கணக்கில் உள்ள மீதி இருப்பு எவ்வளவு?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        },
        "VOICE": {
            "title": "தெளிவான பேச்சு உச்சரிப்பு பயிற்சி",
            "instructions": "மைக்ரோஃபோனை அழுத்தி வாக்கியத்தைத் தெளிவாகப் பேசவும்.",
            "practice_content": [
                {"prompt_phrase": "காலை வணக்கம், உங்களுக்கு எவ்வாறு உதவ முடியும்", "target_phonemes": ["கா", "லை", "வ", "ணக்", "கம்"]}
            ]
        }
    },
    "bn": {
        "READING": {
            "title": "বাংলা বর্ণমালা ও ধ্বনি প্রশিক্ষণ",
            "instructions": "বর্ণের উচ্চারণ শুনুন এবং সঠিক শব্দ বাছাই করুন।",
            "practice_content": [
                {"symbol": "অ / আ", "sound_prompt": "আম", "options": ["আম", "ইট", "উট"], "correct": "আম"}
            ]
        },
        "COMPREHENSION": {
            "title": "এটিএম ও আর্থিক রসিদ পঠন",
            "instructions": "রসিদের বিবরণ পড়ুন এবং প্রশ্নের সঠিক উত্তর দিন।",
            "practice_content": [
                {"passage": "এটিএম উত্তোলন রসিদ: পরিমাণ ₹৫০০, অবশিষ্ট ব্যালেন্স ₹৪,৫০০", "question": "অ্যাকাউন্টে অবশিষ্ট ব্যালেন্স কত?", "options": ["₹৫০০", "₹৪,৫০০", "₹৫,০০০"], "correct": "₹৪,৫০০"}
            ]
        },
        "VOICE": {
            "title": "স্পষ্ট বাক্য বাচন চর্চা",
            "instructions": "মাইক্রোফোন চেপে বাক্যটি স্পষ্টভাবে বলুন।",
            "practice_content": [
                {"prompt_phrase": "শুভ সকাল, আপনাকে কীভাবে সাহায্য করতে পারি", "target_phonemes": ["শু", "ভ", "স", "কা", "ল"]}
            ]
        }
    },
    "mr": {
        "READING": {
            "title": "मराठी मूळाक्षरे व उच्चार सराव",
            "instructions": "अक्षराचा आवाज ऐका आणि योग्य शब्द निवडा.",
            "practice_content": [
                {"symbol": "अ / आ", "sound_prompt": "अननस", "options": ["अननस", "आंबा", "इमारत"], "correct": "अननस"}
            ]
        },
        "COMPREHENSION": {
            "title": "एटीएम व वित्तीय पावती वाचन",
            "instructions": "पावतीचा तपशील वाचा आणि प्रश्नाचे उत्तर द्या.",
            "practice_content": [
                {"passage": "एटीएम पैसे काढल्याची पावती: रक्कम ₹500, शिल्लक रक्कम ₹4,500", "question": "खात्यातील शिल्लक रक्कम किती आहे?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        },
        "VOICE": {
            "title": "स्पष्ट संभाषण व वाचन सराव",
            "instructions": "मायक्रोफोन दाबा आणि वाक्य स्पष्टपणे बोला.",
            "practice_content": [
                {"prompt_phrase": "नमस्कार, मी तुम्हाला कशी मदत करू शकेन", "target_phonemes": ["न", "म", "स्", "का", "र"]}
            ]
        }
    },
    "kn": {
        "READING": {
            "title": "ಕನ್ನಡ ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಸ್ವರ ತರಬೇತಿ",
            "instructions": "ಅಕ್ಷರದ ಶಬ್ದವನ್ನು ಕೇಳಿ ಸರಿಯಾದ ಪದವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
            "practice_content": [
                {"symbol": "ಅ / ಆ", "sound_prompt": "ಅರಸ", "options": ["ಅರಸ", "ಆನೆ", "ಇಲಿ"], "correct": "ಅರಸ"}
            ]
        },
        "COMPREHENSION": {
            "title": "ಎಟಿಎಂ ಮತ್ತು ಹಣಕಾಸು ರಶೀದಿ ಓದುವಿಕೆ",
            "instructions": "ರಶೀದಿ ವಿವರಗಳನ್ನು ಓದಿ ಸರಿಯಾದ ಉತ್ತರ ನೀಡಿ.",
            "practice_content": [
                {"passage": "ಎಟಿಎಂ ಹಣ ಹಿಂಪಡೆದ ರಶೀದಿ: ಮೊತ್ತ ₹500, ಬಾಕಿ ಮೊತ್ತ ₹4,500", "question": "ಖಾತೆಯಲ್ಲಿರುವ ಬಾಕಿ ಮೊತ್ತ ಎಷ್ಟು?", "options": ["₹500", "₹4,500", "₹5,000"], "correct": "₹4,500"}
            ]
        },
        "VOICE": {
            "title": "ಸ್ಪಷ್ಟ ಮಾತನಾಡುವ ಉಚ್ಚಾರಣೆ ಅಭ್ಯಾಸ",
            "instructions": "ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ವಾಕ್ಯವನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ.",
            "practice_content": [
                {"prompt_phrase": "ಶುಭೋದಯ, ನಾನು ನಿಮಗೆ ಹೇಗೆ ನೆರವಾಗಲಿ", "target_phonemes": ["ಶು", "ಭೋ", "ದ", "ಯ"]}
            ]
        }
    },
    "es": {
        "READING": {
            "title": "Entrenador de Fonética y Sílabas en Español",
            "instructions": "Escuche el sonido de la letra y seleccione la palabra correspondiente.",
            "practice_content": [
                {"symbol": "A / a", "sound_prompt": "manzana", "options": ["Manzana", "Pelota", "Gato"], "correct": "Manzana"}
            ]
        },
        "COMPREHENSION": {
            "title": "Escenario de Lectura Funcional de Cajero",
            "instructions": "Lea los detalles del recibo y responda la pregunta.",
            "practice_content": [
                {"passage": "Recibo de cajero: Monto $500, Saldo restante $4,500", "question": "¿Cuál es el saldo restante?", "options": ["$500", "$4,500", "$5,000"], "correct": "$4,500"}
            ]
        },
        "VOICE": {
            "title": "Articulación de Voz Profesional",
            "instructions": "Toque el micrófono y pronuncie la frase claramente.",
            "practice_content": [
                {"prompt_phrase": "Buenos días, ¿en qué puedo ayudarle hoy?", "target_phonemes": ["b", "n", "s", "d", "s"]}
            ]
        }
    }
}

@router.post("/personalized-lessons", response_model=schemas.PersonalizedLessonOut)
def generate_personalized_lesson(
    skill_type: Optional[str] = Query(None),
    lang: Optional[str] = Query(None, description="ISO language code (e.g. en, te, hi, ta, bn, mr, kn, es)"),
    db: Session = Depends(get_db),
    learner: Optional[models.Learner] = Depends(get_optional_current_learner)
):
    if not learner:
        learner = db.query(models.Learner).first()
    if not learner:
        raise HTTPException(status_code=404, detail="No learner account found.")

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    
    # Resolve target language ISO
    if lang:
        iso = lang.lower()
    else:
        lang_id = learner.current_lang_id or 1
        lang_obj = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
        iso = lang_obj.iso_code if lang_obj else "en"

    if not skill_type:
        skills = {
            "READING": profile.reading_pct or 0.0 if profile else 50.0,
            "COMPREHENSION": profile.comprehension_pct or 0.0 if profile else 50.0,
            "VOICE": profile.voice_pct or 0.0 if profile else 50.0
        }
        skill_type = min(skills, key=skills.get)

    level = profile.literacy_level if profile else "FOUNDATIONAL"
    lang_lessons = PERSONALIZED_LESSONS_BY_LANG.get(iso, PERSONALIZED_LESSONS_BY_LANG["en"])
    lesson_data = lang_lessons.get(skill_type, lang_lessons["READING"])

    ex_type = "PHONICS_FLASHCARD" if skill_type == "READING" else ("FUNCTIONAL_CONTEXT_READING" if skill_type == "COMPREHENSION" else "PRONUNCIATION_COACH")

    return {
        "lesson_id": f"gen_{skill_type.lower()}_{learner.learner_id}_{iso}",
        "target_skill": skill_type,
        "language_code": iso,
        "difficulty": level,
        "exercise_type": ex_type,
        "title": lesson_data["title"],
        "instructions": lesson_data["instructions"],
        "practice_content": lesson_data["practice_content"]
    }

RECOMMENDED_CONTENT_BY_LANG = {
    "en": [
        {
            "category": "Interactive Speech Coach",
            "title": "Customer Service & Workplace Speech Practice",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "Good morning, welcome to our office. How can I assist you today?"}
        },
        {
            "category": "Functional Literacy Flashcards",
            "title": "Medical Prescription & Pharmacy Labels",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "Medical & Pharmacy"}
        },
        {
            "category": "Phonics Mastery",
            "title": "Alphabet Vowel Sounds & Phonics Cards",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "te": [
        {
            "category": "ఇంటరాక్టివ్ స్పీచ్ కోచ్",
            "title": "కార్యాలయ వృత్తిపరమైన మాట్లాడే సాధన",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "శుభోదయం, మా కార్యాలయానికి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?"}
        },
        {
            "category": "ఉపయోగకరమైన అక్షరాస్యత ఫ్లాష్ కార్డ్‌లు",
            "title": "వైద్య ప్రిస్క్రిప్షన్ మరియు ఔషధ వివరాలు",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "వైద్యం"}
        },
        {
            "category": "అక్షర సమగ్రత",
            "title": "తెలుగు అచ్చులు మరియు గుణింతపు సాధన కార్డ్‌లు",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "hi": [
        {
            "category": "इंटरएक्टिव स्पीच कोच",
            "title": "कार्यस्थल पेशेवर भाषा वाचन अभ्यास",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "नमस्ते, हमारे कार्यालय में आपका स्वागत है। मैं आपकी क्या सहायता कर सकता हूँ?"}
        },
        {
            "category": "कार्यात्मक साक्षरता फ्लैशकार्ड",
            "title": "चिकित्सा पर्चा एवं दवा निर्देश वाचन",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "स्वास्थ्य एवं चिकित्सा"}
        },
        {
            "category": "वर्णमाला दक्षता",
            "title": "हिंदी स्वर एवं मात्रा अभ्यास कार्ड",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "ta": [
        {
            "category": "இன்டராக்டிவ் பேச்சு பயிற்சியாளர்",
            "title": "அலுவலக பேச்சு மற்றும் உரையாடல் பயிற்சி",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "வணக்கம், எங்கள் அலுவலகத்திற்கு நல்வரவு."}
        },
        {
            "category": "செயல்பாட்டு எழுத்தறிவு கார்டுகள்",
            "title": "மருத்துவ சீட்டு மற்றும் மருந்து குறிப்புகள்",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "மருத்துவம்"}
        },
        {
            "category": "எழுத்து பயிற்சி",
            "title": "தமிழ் எழுத்துக்கள் மற்றும் ஒலி பயிற்சி",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "bn": [
        {
            "category": "ইন্টারেক্টিভ স্পিচ কোচ",
            "title": "কর্মক্ষেত্রের পেশাদার বাক্যালাপ চর্চা",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "শুভ সকাল, আমাদের কার্যালয়ে স্বাগতম।"}
        },
        {
            "category": "কার্যকরী সাক্ষরতা ফ্ল্যাশকার্ড",
            "title": "চিকিৎসা প্রেসক্রিপশন ও ঔষধ নির্দেশিকা",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "চিকিৎসা"}
        },
        {
            "category": "বর্ণমালা দক্ষতা",
            "title": "বাংলা বর্ণমালা ও স্বরধ্বনি চর্চা কার্ড",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "mr": [
        {
            "category": "इंटरॲक्टिव्ह स्पीच कोच",
            "title": "व्यावसायिक संवाद व संभाषण सराव",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "नमस्कार, आमच्या कार्यालयात आपले स्वागत आहे."}
        },
        {
            "category": "कार्यात्मक साक्षरता फ्लॅशकार्ड्स",
            "title": "औषध चिठ्ठी व वैद्यकीय माहिती वाचन",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "आरोग्य"}
        },
        {
            "category": "मूळाक्षरे प्रभुत्व",
            "title": "मराठी मूळाक्षरे व उच्चार सराव कार्ड्स",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "kn": [
        {
            "category": "ಇಂಟರ್ಯಾಕ್ಟಿವ್ ಸ್ಪೀಚ್ ಕೋಚ್",
            "title": "ವೃತ್ತಿಪರ ಮಾತನಾಡುವ ಸಂಭಾಷಣೆ ಅಭ್ಯಾಸ",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "ನಮಸ್ಕಾರ, ನಮ್ಮ ಕಚೇರಿಗೆ ಸ್ವಾಗತ."}
        },
        {
            "category": "ಕಾರ್ಯಾತ್ಮಕ ಸಾಕ್ಷರತೆ ಫ್ಲ್ಯಾಶ್ ಕಾರ್ಡ್‌ಗಳು",
            "title": "ವೈದ್ಯಕೀಯ ಚೀಟಿ ಮತ್ತು ಔಷಧಿ ಓದುವಿಕೆ",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "ವೈದ್ಯಕೀಯ"}
        },
        {
            "category": "ಅಕ್ಷರಮಾಲೆ ಪ್ರಾವೀಣ್ಯ",
            "title": "ಕನ್ನಡ ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಸ್ವರ ತರಬೇತಿ ಕಾರ್ಡ್‌ಗಳು",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ],
    "es": [
        {
            "category": "Entrenador de Voz Interactivo",
            "title": "Práctica de Diálogo de Servicio al Cliente",
            "skill_type": "VOICE",
            "relevance_score": 0.96,
            "content_payload": {"type": "AUDIO_DIALOGUE", "duration_sec": 120, "script": "Buenos días, bienvenido a nuestra oficina. ¿En qué puedo ayudarle hoy?"}
        },
        {
            "category": "Tarjetas de Alfabetización Funcional",
            "title": "Lectura de Recetas Médicas y Etiquetas",
            "skill_type": "COMPREHENSION",
            "relevance_score": 0.91,
            "content_payload": {"type": "FLASHCARD_SUITE", "card_count": 10, "topic": "Salud"}
        },
        {
            "category": "Dominio de Fonética",
            "title": "Tarjetas de Sonidos del Alfabeto y Vocales",
            "skill_type": "READING",
            "relevance_score": 0.88,
            "content_payload": {"type": "PHONICS_GAME", "level": "FOUNDATIONAL"}
        }
    ]
}

@router.get("/recommended-content", response_model=List[schemas.ContentRecommendationOut])
def get_recommended_content(
    lang: Optional[str] = Query(None, description="ISO language code (e.g. en, te, hi, ta, bn, mr, kn, es)"),
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

    # Resolve target language ISO
    if lang:
        iso = lang.lower()
    else:
        lang_id = learner.current_lang_id or 1
        lang_obj = db.query(models.Language).filter(models.Language.lang_id == lang_id).first()
        iso = lang_obj.iso_code if lang_obj else "en"

    items = RECOMMENDED_CONTENT_BY_LANG.get(iso, RECOMMENDED_CONTENT_BY_LANG["en"])

    # Adjust relevance scores dynamically based on learner's weaknesses
    adjusted_items = []
    for item in items:
        score = item["relevance_score"]
        if item["skill_type"] == "VOICE" and v_pct < 60:
            score = 0.98
        elif item["skill_type"] == "READING" and r_pct < 60:
            score = 0.95

        adjusted_items.append({
            "category": item["category"],
            "title": item["title"],
            "skill_type": item["skill_type"],
            "relevance_score": score,
            "content_payload": item["content_payload"]
        })

    # Sort items by relevance score descending
    adjusted_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    return adjusted_items
