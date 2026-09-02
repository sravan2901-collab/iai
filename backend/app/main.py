from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, curriculum, voice, assessment, learning_path, progress, recommendation

# Create tables in development mode if not already created
Base.metadata.create_all(bind=engine)

def ensure_schema_migrations():
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            cols = [row[1] for row in conn.execute(text("PRAGMA table_info(assessment_result)")).fetchall()]
            if cols and "question_id" not in cols:
                conn.execute(text("ALTER TABLE assessment_result ADD COLUMN question_id INTEGER REFERENCES assessment_question(question_id)"))
            if cols and "is_correct" not in cols:
                conn.execute(text("ALTER TABLE assessment_result ADD COLUMN is_correct BOOLEAN DEFAULT 0"))
            if cols and "user_answer" not in cols:
                conn.execute(text("ALTER TABLE assessment_result ADD COLUMN user_answer TEXT"))

            profile_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(learner_profile)")).fetchall()]
            if profile_cols and "reading_pct" not in profile_cols:
                conn.execute(text("ALTER TABLE learner_profile ADD COLUMN reading_pct FLOAT DEFAULT 0.0"))
            if profile_cols and "comprehension_pct" not in profile_cols:
                conn.execute(text("ALTER TABLE learner_profile ADD COLUMN comprehension_pct FLOAT DEFAULT 0.0"))
            if profile_cols and "voice_pct" not in profile_cols:
                conn.execute(text("ALTER TABLE learner_profile ADD COLUMN voice_pct FLOAT DEFAULT 0.0"))
            if profile_cols and "last_activity_date" not in profile_cols:
                conn.execute(text("ALTER TABLE learner_profile ADD COLUMN last_activity_date DATE"))

            prog_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(progress_tracking)")).fetchall()]
            if prog_cols and "time_spent_min" not in prog_cols:
                conn.execute(text("ALTER TABLE progress_tracking ADD COLUMN time_spent_min INTEGER DEFAULT 0"))

            lp_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(learning_path)")).fetchall()]
            if lp_cols and "completion_percentage" not in lp_cols:
                conn.execute(text("ALTER TABLE learning_path ADD COLUMN completion_percentage FLOAT DEFAULT 0.0"))

            rep_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(learning_report)")).fetchall()]
            if rep_cols and "summary_json" not in rep_cols:
                conn.execute(text("ALTER TABLE learning_report ADD COLUMN summary_json TEXT"))
            if rep_cols and "narrative" not in rep_cols:
                conn.execute(text("ALTER TABLE learning_report ADD COLUMN narrative TEXT"))

            # Phase 4: Recommendation table — make lesson_id nullable + add new columns
            rec_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(recommendation)")).fetchall()]
            if rec_cols and "priority" not in rec_cols:
                # SQLite doesn't support ALTER COLUMN, so recreate the table
                conn.execute(text("ALTER TABLE recommendation RENAME TO recommendation_old"))
                conn.execute(text("""
                    CREATE TABLE recommendation (
                        recommendation_id INTEGER PRIMARY KEY,
                        learner_id INTEGER NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
                        lesson_id INTEGER REFERENCES lesson(lesson_id) ON DELETE CASCADE,
                        recommended_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reason VARCHAR(500),
                        model_version VARCHAR(50) DEFAULT 'rule-based',
                        priority VARCHAR(20) DEFAULT 'MEDIUM',
                        skill_focus VARCHAR(50) DEFAULT 'READING',
                        rec_type VARCHAR(50) DEFAULT 'practice_weak_area',
                        title VARCHAR(200)
                    )
                """))
                conn.execute(text("""
                    INSERT INTO recommendation (recommendation_id, learner_id, lesson_id, recommended_on, reason, model_version)
                    SELECT recommendation_id, learner_id, lesson_id, recommended_on, reason, model_version
                    FROM recommendation_old
                """))
                conn.execute(text("DROP TABLE recommendation_old"))

            # Phase 4: AI Generated Content table (created by Base.metadata.create_all)
            conn.commit()
    except Exception as e:
        print(f"[DB MIGRATION NOTICE] Auto-migration skipped or failed: {e}")

def seed_languages():
    try:
        from app.database import SessionLocal
        from app import models
        db = SessionLocal()
        supported = [
            {"iso_code": "en", "lang_name": "English"},
            {"iso_code": "te", "lang_name": "Telugu (తెలుగు)"},
            {"iso_code": "hi", "lang_name": "Hindi (हिन्दी)"},
            {"iso_code": "ta", "lang_name": "Tamil (தமிழ்)"},
            {"iso_code": "bn", "lang_name": "Bengali (বাংলা)"},
            {"iso_code": "mr", "lang_name": "Marathi (मराठी)"},
            {"iso_code": "kn", "lang_name": "Kannada (కನ್ನಡ)"},
            {"iso_code": "es", "lang_name": "Spanish (Español)"}
        ]
        for item in supported:
            existing = db.query(models.Language).filter(models.Language.iso_code == item["iso_code"]).first()
            if not existing:
                new_lang = models.Language(iso_code=item["iso_code"], lang_name=item["lang_name"])
                db.add(new_lang)
        db.commit()
        db.close()
    except Exception as e:
        print(f"[SEED LANGUAGES NOTICE] Could not seed languages: {e}")

def seed_curriculum_data():
    try:
        from app.database import SessionLocal
        from app import models
        db = SessionLocal()

        NATIVE_DATA = {
            "en": {
                "m1": "Alphabets & Phonics and Everyday Greetings",
                "m2": "ATM & Banking, Health & Prescription, Digital Payment",
                "m3": "Workplace Communication & Customer Service Dialogue",
                "l1": ("Alphabets & Phonics Fundamentals", "A B C D E F G"),
                "l2": ("Everyday Greetings & Basic Vocabulary", "Hello, Good Morning, Thank You"),
                "l3": ("ATM & Banking Functional Reading", "Withdraw cash, enter PIN, check balance"),
                "l4": ("Health & Medical Prescription Literacy", "Take 1 tablet after meals twice daily"),
                "l5": ("Digital Payment & Receipt Confirmation", "Scan QR code, enter amount, payment successful"),
                "l6": ("Workplace Communication & Professional Greetings", "Good morning team, let us discuss today's objectives clearly"),
                "l7": ("Customer Service Dialogue & Voice Practice", "Welcome to our service desk. How may I assist you today?")
            },
            "te": {
                "m1": "అక్షరాలు, వర్ణమాల మరియు దైనందిన శుభాకాంక్షలు",
                "m2": "ఏటీఎం బ్యాంకింగ్, వైద్య ప్రిస్క్రిప్షన్ మరియు డిజిటల్ చెల్లింపులు",
                "m3": "కార్యాలయ సంభాషణ మరియు వినియోగదారుల సేవా సంభాషణ",
                "l1": ("వర్ణమాల మరియు హల్లుల ఉచ్చారణ", "అ ఆ ఇ ఈ ఉ ఊ ఋ ఎ ఏ ఐ ఒ ఓ ఔ"),
                "l2": ("దైనందిన సంభాషణ మరియు శుభాకాంక్షలు", "నమస్కారం, ఉదయాభినందనలు, ధన్యవాదాలు"),
                "l3": ("ఏటీఎం మరియు బ్యాంకింగ్ పరిజ్ఞానం", "నగదు ఉపసంహరణ, పిన్ నమోదు, నిల్వ తనిఖీ"),
                "l4": ("వైద్య చికిత్స మరియు ప్రిస్క్రిప్షన్ పఠనం", "భోజనం తర్వాత రోజుకు రెండు సార్లు టాబ్లెట్ తీసుకోండి"),
                "l5": ("డిజిటల్ చెల్లింపు మరియు రసీదు నిర్ధారణ", "క్యూఆర్ కోడ్ స్కాన్ చేయండి, మొత్తాన్ని నమోదు చేయండి"),
                "l6": ("కార్యాలయ వృత్తిపరమైన మాట్లాడే పరిజ్ఞానం", "శుభోదయం, నేటి పని లక్ష్యాలను స్పష్టంగా చర్చిద్దాం"),
                "l7": ("వినియోగదారుల సేవా సంభాషణ సాధన", "మా సేవా కేంద్రానికి స్వాగతం, నేను మీకు ఎలా సహాయపడగలను")
            },
            "hi": {
                "m1": "वर्णमाला, स्वर एवं दैनिक अभिवादन",
                "m2": "एटीएम बैंकिंग, स्वास्थ्य पर्चा एवं डिजिटल भुगतान",
                "m3": "कार्यस्थल संचार एवं ग्राहक सेवा संवाद",
                "l1": ("वर्णमाला एवं स्वर उच्चारण", "अ आ इ ई उ ऊ ऋ ए ऐ ओ औ"),
                "l2": ("दैनिक बातचीत एवं अभिवादन", "नमस्ते, सुप्रभात, धन्यवाद"),
                "l3": ("एटीएम एवं बैंकिंग साक्षरता", "नकद निकासी, पिन दर्ज करें, शेष राशि जांचें"),
                "l4": ("चिकित्सा एवं पर्चा वाचन", "भोजन के बाद दिन में दो बार एक गोली लें"),
                "l5": ("डिजिटल भुगतान एवं रसीद पुष्टि", "क्यूआर कोड स्कैन करें, राशि दर्ज करें, भुगतान सफल"),
                "l6": ("कार्यस्थल पेशेवर भाषा वाचन", "सुप्रभात टीम, आइए आज के लक्ष्यों पर चर्चा करें"),
                "l7": ("ग्राहक सेवा संवाद एवं वाचन अभ्यास", "हमारे सेवा केंद्र में आपका स्वागत है, मैं आपकी क्या सहायता कर सकता हूँ")
            },
            "ta": {
                "m1": "எழுத்துக்கள், உச்சரிப்பு மற்றும் அன்றாட வாழ்த்துக்கள்",
                "m2": "ஏடிஎம் வங்கி, மருத்துவ குறிப்பு மற்றும் டிஜிட்டல் செலுத்தல்",
                "m3": "அலுவலக உரையாடல் மற்றும் வாடிக்கையாளர் சேவை",
                "l1": ("எழுத்துக்கள் மற்றும் உச்சரிப்பு பயிற்சி", "அ ஆ இ ஈ உ ஊ எ ஏ ஐ ஒ ஓ ஔ"),
                "l2": ("அன்றாட வாழ்த்துக்கள் மற்றும் சொற்கள்", "வணக்கம், காலை வணக்கம், நன்றி"),
                "l3": ("ஏடிஎம் மற்றும் வங்கி வாசிப்பு", "பணம் எடுப்பது, பின் எண்ணை உள்ளிடவும், இருப்பை சரிபார்க்கவும்"),
                "l4": ("மருத்துவ மருந்து சீட்டு வாசிப்பு", "உணவுக்குப் பிறகு நாளில் இருவேளை ஒரு மாத்திரை சாப்பிடவும்"),
                "l5": ("டிஜிட்டல் பணம் செலுத்துதல் உறுதிப்படுத்தல்", "QR குறியீட்டை ஸ்கேன் செய்யவும், தொகையை உள்ளிடவும்"),
                "l6": ("அலுவலக தொடர்பு பயிற்சி", "காலை வணக்கம், இன்றைய இலக்குகளை தெளிவாக விவாதிப்போம்"),
                "l7": ("வாடிக்கையாளர் சேவை பேச்சு பயிற்சி", "எங்கள் சேவை மையத்திற்கு நல்வரவு, உங்களுக்கு எவ்வாறு உதவ முடியும்")
            },
            "bn": {
                "m1": "বর্ণমালা, স্বরধ্বনি এবং দৈনন্দিন সম্ভাষণ",
                "m2": "এটিএম ব্যাংকিং, প্রেসক্রিপশন এবং ডিজিটাল পেমেন্ট",
                "m3": "কর্মক্ষেত্রের কথোপকথন এবং গ্রাহক সেবা বাক্য",
                "l1": ("বর্ণমালা ও মৌলিক উচ্চারণ", "অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ"),
                "l2": ("দৈনন্দিন সম্ভাষণ ও পরিচিতি", "নমস্কার, শুভ সকাল, ধন্যবাদ"),
                "l3": ("এটিএম ও ব্যাংকিং পঠন", "টাকা তোলা, পিন নম্বর দিন, ব্যালেন্স চেক করুন"),
                "l4": ("চিকিৎসা ও প্রেসক্রিপশন পঠন", "খাবারের পর দিনে দুবার একটা করে ট্যাবলেট খাবেন"),
                "l5": ("ডিজিটাল পেমেন্ট ও রশিদ নিশ্চিতকরণ", "কিউআর কোড স্ক্যান করুন, পরিমাণ লিখুন"),
                "l6": ("কর্মক্ষেত্রের পেশাদার বাক্য অনুশীলন", "শুভ সকাল, আসুন আজকের কাজের লক্ষ্য পরিষ্কারভাবে আলোচনা করি"),
                "l7": ("গ্রাহক সেবা বাক্য ও বাচন চর্চা", "আমাদের সেবা কেন্দ্রে স্বাগতম, আপনাকে কীভাবে সাহায্য করতে পারি")
            },
            "mr": {
                "m1": "वर्णमाला, स्वर व दैनंदिन नमस्कार",
                "m2": "एटीएम बँकिंग, औषध चिठ्ठी व डिजिटल पेमेंट",
                "m3": "कामाच्या ठिकाणचा संवाद व ग्राहक सेवा संभाषण",
                "l1": ("वर्णमाला व मूळाक्षरे उच्चार", "अ आ इ ई उ ऊ ऋ ए ऐ ओ औ"),
                "l2": ("दैनंदिन संवाद व नमस्कार", "नमस्कार, शुभ सकाळ, धन्यवाद"),
                "l3": ("एटीएम व बँकिंग वाचन", "पैसे काढा, पिन प्रविष्ट करा, शिल्लक तपासा"),
                "l4": ("आरोग्य व औषध चिठ्ठी वाचन", "जेवणानंतर दिवसातून दोनदा एक गोळी घ्या"),
                "l5": ("डिजिटल पेमेंट व पावती खात्री", "क्यूआर कोड स्कॅन करा, रक्कम टाका"),
                "l6": ("व्यावसायिक संवाद व संभाषण", "शुभ सकाळ, चला आजच्या उद्दिष्टांवर चर्चा करूया"),
                "l7": ("ग्राहक सेवा संभाषण व वाचन सराव", "आमच्या सेवा केंद्रात आपले स्वागत आहे, मी कशी मदत करू शकेन")
            },
            "kn": {
                "m1": "ಅಕ್ಷರಮಾಲೆ, ಸ್ವರಗಳು ಮತ್ತು ದೈನಂದಿನ ಶುಭಾಶಯಗಳು",
                "m2": "ಎಟಿಎಂ ಬ್ಯಾಂಕಿಂಗ್, ವೈದ್ಯಕೀಯ ಚೀಟಿ ಮತ್ತು ಡಿಜಿಟಲ್ ಪಾವತಿ",
                "m3": "ಉದ್ಯೋಗಸ್ಥಳದ ಸಂವಹನ ಮತ್ತು ಗ್ರಾಹಕ ಸೇವಾ ಸಂಭಾಷಣೆ",
                "l1": ("ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಉಚ್ಚಾರಣೆ ಅಭ್ಯಾಸ", "ಅ ಆ ಇ ಈ ಉ ಊ ಋ ಎ ಏ ಐ ಒ ಓ ಔ"),
                "l2": ("ದೈನಂದಿನ ಶುಭಾಶಯಗಳು ಮತ್ತು ಪದಗಳು", "ನಮಸ್ಕಾರ, ಶುಭೋದಯ, ಧನ್ಯವಾದಗಳು"),
                "l3": ("ಎಟಿಎಂ ಮತ್ತು ಬ್ಯಾಂಕಿಂಗ್ ಓದುವಿಕೆ", "ಹಣ ಹಿಂಪಡೆಯಿರಿ, ಪಿನ್ ನಮೂದಿಸಿ, ಬಾಕಿ ಪರಿಶೀಲಿಸಿ"),
                "l4": ("ವೈದ್ಯಕೀಯ ಚೀಟಿ ಓದುವಿಕೆ", "ಊಟದ ನಂತರ ದಿನಕ್ಕೆ ಎರಡು ಬಾರಿ ಒಂದು ಮಾತ್ರೆ ತೆಗೆದುಕೊಳ್ಳಿ"),
                "l5": ("ಡಿಜಿಟಲ್ ಪಾವತಿ ಮತ್ತು ರಶೀದಿ ದೃಢೀಕರಣ", "ಕ್ಯೂಆರ್ ಕೋಡ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ, ಮೊತ್ತ ನಮೂದಿಸಿ"),
                "l6": ("ವೃತ್ತಿಪರ ಮಾತನಾಡುವ ಅಭ್ಯಾಸ", "ಶುಭೋದಯ, ಇಂದಿನ ಗುರಿಗಳನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಚರ್ಚಿಸೋಣ"),
                "l7": ("ಗ್ರಾಹಕ ಸೇವಾ ಸಂಭಾಷಣೆ ಅಭ್ಯಾಸ", "ನಮ್ಮ ಸೇವಾ ಕೇಂದ್ರಕ್ಕೆ ಸ್ವಾಗತ, ನಾನು ನಿಮಗೆ ಹೇಗೆ ನೆರವಾಗಲಿ")
            },
            "es": {
                "m1": "Alfabeto, Fonética y Saludos Cotidianos",
                "m2": "Cajero Automático, Salud y Pagos Digitales",
                "m3": "Comunicación Laboral y Servicio al Cliente",
                "l1": ("Fundamentos del Alfabeto y Fonética", "A B C D E F G H I J K L M N Ñ O P Q R S T U V W X Y Z"),
                "l2": ("Saludos Cotidianos y Vocabulario Básico", "Hola, Buenos días, Muchas gracias"),
                "l3": ("Lectura Funcional de Cajero y Banco", "Retirar efectivo, ingrese su PIN, consultar saldo"),
                "l4": ("Lectura de Recetas Médicas", "Tomar 1 pastilla después de las comidas dos veces al día"),
                "l5": ("Confirmación de Pagos Digitales y Recibos", "Escanear código QR, ingrese el monto, pago exitoso"),
                "l6": ("Comunicación Profesional en el Trabajo", "Buenos días equipo, discutamos claramente los objetivos de hoy"),
                "l7": ("Diálogo de Servicio al Cliente y Práctica de Voz", "Bienvenido a nuestro centro de atención, ¿en qué puedo ayudarle hoy?")
            }
        }

        languages = db.query(models.Language).all()
        for lang in languages:
            native = NATIVE_DATA.get(lang.iso_code, NATIVE_DATA["en"])
            for level in ["FOUNDATIONAL", "FUNCTIONAL", "PROFICIENT"]:
                curriculum = db.query(models.Curriculum).filter(
                    models.Curriculum.lang_id == lang.lang_id,
                    models.Curriculum.level == level
                ).first()

                if not curriculum:
                    curriculum = models.Curriculum(
                        lang_id=lang.lang_id,
                        title=f"{lang.lang_name} - {level} Literacy Curriculum",
                        level=level,
                        description=f"Comprehensive {level} literacy curriculum for {lang.lang_name}"
                    )
                    db.add(curriculum)
                    db.commit()
                    db.refresh(curriculum)

                # Seed Modules for this Curriculum if empty
                m_count = db.query(models.Module).filter(models.Module.curriculum_id == curriculum.curriculum_id).count()
                if m_count == 0:
                    m1 = models.Module(
                        curriculum_id=curriculum.curriculum_id,
                        module_name=native["m1"],
                        sequence_no=1,
                        skill_type="READING"
                    )
                    m2 = models.Module(
                        curriculum_id=curriculum.curriculum_id,
                        module_name=native["m2"],
                        sequence_no=2,
                        skill_type="COMPREHENSION"
                    )
                    m3 = models.Module(
                        curriculum_id=curriculum.curriculum_id,
                        module_name=native["m3"],
                        sequence_no=3,
                        skill_type="VOICE"
                    )
                    db.add_all([m1, m2, m3])
                    db.commit()
                    db.refresh(m1)
                    db.refresh(m2)
                    db.refresh(m3)

                    # Seed Lessons
                    l1 = models.Lesson(module_id=m1.module_id, title=native["l1"][0], content_type="READING", target_text=native["l1"][1], difficulty_level="FOUNDATIONAL")
                    l2 = models.Lesson(module_id=m1.module_id, title=native["l2"][0], content_type="READING", target_text=native["l2"][1], difficulty_level="FOUNDATIONAL")

                    l3 = models.Lesson(module_id=m2.module_id, title=native["l3"][0], content_type="COMPREHENSION", target_text=native["l3"][1], difficulty_level="FUNCTIONAL")
                    l4 = models.Lesson(module_id=m2.module_id, title=native["l4"][0], content_type="COMPREHENSION", target_text=native["l4"][1], difficulty_level="FUNCTIONAL")
                    l5 = models.Lesson(module_id=m2.module_id, title=native["l5"][0], content_type="COMPREHENSION", target_text=native["l5"][1], difficulty_level="FUNCTIONAL")

                    l6 = models.Lesson(module_id=m3.module_id, title=native["l6"][0], content_type="VOICE", target_text=native["l6"][1], difficulty_level="PROFICIENT")
                    l7 = models.Lesson(module_id=m3.module_id, title=native["l7"][0], content_type="VOICE", target_text=native["l7"][1], difficulty_level="PROFICIENT")
                    db.add_all([l1, l2, l3, l4, l5, l6, l7])
                    db.commit()

        db.close()
    except Exception as e:
        print(f"[SEED CURRICULUM NOTICE] Could not seed curriculum data: {e}")

ensure_schema_migrations()
seed_languages()
seed_curriculum_data()

# Seed canonical achievement catalog
try:
    from app.services.gamification_service import seed_achievement_catalog
    from app.database import SessionLocal as _GamifySessionLocal
    _gamify_db = _GamifySessionLocal()
    _new_ach_count = seed_achievement_catalog(_gamify_db)
    if _new_ach_count > 0:
        print(f"[SEED ACHIEVEMENTS] [OK] Seeded {_new_ach_count} canonical achievements")
    _gamify_db.close()
except Exception as e:
    print(f"[SEED ACHIEVEMENTS NOTICE] Could not seed achievements: {e}")

# Seed difficulty level content (Absolute Beginner → Mastery) for all languages
try:
    from app.services.seed_difficulty_content import seed_difficulty_content
    from app.database import SessionLocal as _DiffSessionLocal
    db_session = _DiffSessionLocal()
    langs_seeded, lessons_created = seed_difficulty_content(db_session)
    if lessons_created > 0:
        print(f"[SEED DIFFICULTY] ✅ Seeded {lessons_created} lessons across {langs_seeded} languages")
    db_session.close()
except Exception as e:
    print(f"[SEED DIFFICULTY NOTICE] Could not seed difficulty content: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Setup - Explicit allowed origins with credential support (no wildcard mixing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router Modules
from app.routers import learners, admin, reports, recommendations

app.include_router(auth.router)
app.include_router(curriculum.router)
app.include_router(voice.router)
app.include_router(assessment.router)
app.include_router(learning_path.router)
app.include_router(progress.router)
app.include_router(recommendation.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(learners.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "weeks_1_2_status": "Learning Content Management & Assessment Framework 100% Implemented",
        "milestone_2_status": "AI-Based Personalized Learning Engine 100% Implemented"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AksharAI FastAPI Gateway"}
