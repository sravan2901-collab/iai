from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, curriculum, voice, assessment, learning_path

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

            prog_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(progress_tracking)")).fetchall()]
            if prog_cols and "time_spent_min" not in prog_cols:
                conn.execute(text("ALTER TABLE progress_tracking ADD COLUMN time_spent_min INTEGER DEFAULT 0"))

            lp_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(learning_path)")).fetchall()]
            if lp_cols and "completion_percentage" not in lp_cols:
                conn.execute(text("ALTER TABLE learning_path ADD COLUMN completion_percentage FLOAT DEFAULT 0.0"))
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

        languages = db.query(models.Language).all()
        for lang in languages:
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
                        module_name="Alphabets & Phonics and Everyday Greetings",
                        sequence_no=1,
                        skill_type="READING"
                    )
                    m2 = models.Module(
                        curriculum_id=curriculum.curriculum_id,
                        module_name="ATM & Banking, Health & Prescription, Digital Payment",
                        sequence_no=2,
                        skill_type="COMPREHENSION"
                    )
                    m3 = models.Module(
                        curriculum_id=curriculum.curriculum_id,
                        module_name="Workplace Communication & Customer Service Dialogue",
                        sequence_no=3,
                        skill_type="VOICE"
                    )
                    db.add_all([m1, m2, m3])
                    db.commit()
                    db.refresh(m1)
                    db.refresh(m2)
                    db.refresh(m3)

                    # Seed Lessons for Module 1 (Phonics & Greetings)
                    l1 = models.Lesson(
                        module_id=m1.module_id,
                        title="Alphabets & Phonics Fundamentals",
                        content_type="READING",
                        target_text="A B C D E F G",
                        difficulty_level="FOUNDATIONAL"
                    )
                    l2 = models.Lesson(
                        module_id=m1.module_id,
                        title="Everyday Greetings & Basic Vocabulary",
                        content_type="READING",
                        target_text="Hello, Good Morning, Thank You",
                        difficulty_level="FOUNDATIONAL"
                    )

                    # Seed Lessons for Module 2 (Banking, Health & Payment)
                    l3 = models.Lesson(
                        module_id=m2.module_id,
                        title="ATM & Banking Functional Reading",
                        content_type="COMPREHENSION",
                        target_text="Withdraw cash, enter PIN, check balance",
                        difficulty_level="FUNCTIONAL"
                    )
                    l4 = models.Lesson(
                        module_id=m2.module_id,
                        title="Health & Prescription Literacy",
                        content_type="COMPREHENSION",
                        target_text="Take 1 tablet after meals twice daily",
                        difficulty_level="FUNCTIONAL"
                    )
                    l5 = models.Lesson(
                        module_id=m2.module_id,
                        title="Digital Payment & Receipt Confirmation",
                        content_type="COMPREHENSION",
                        target_text="Scan QR code, enter amount, payment successful",
                        difficulty_level="FUNCTIONAL"
                    )

                    # Seed Lessons for Module 3 (Workplace & Customer Service)
                    l6 = models.Lesson(
                        module_id=m3.module_id,
                        title="Workplace Communication & Professional Greetings",
                        content_type="VOICE",
                        target_text="Good morning team, let us discuss today's objectives clearly",
                        difficulty_level="PROFICIENT"
                    )
                    l7 = models.Lesson(
                        module_id=m3.module_id,
                        title="Customer Service Dialogue & Voice Practice",
                        content_type="VOICE",
                        target_text="Welcome to our service desk. How may I assist you today?",
                        difficulty_level="PROFICIENT"
                    )
                    db.add_all([l1, l2, l3, l4, l5, l6, l7])
                    db.commit()

        db.close()
    except Exception as e:
        print(f"[SEED CURRICULUM NOTICE] Could not seed curriculum data: {e}")

ensure_schema_migrations()
seed_languages()
seed_curriculum_data()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router Modules
app.include_router(auth.router)
app.include_router(curriculum.router)
app.include_router(voice.router)
app.include_router(assessment.router)
app.include_router(learning_path.router)

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "weeks_1_2_status": "Learning Content Management & Assessment Framework 100% Implemented"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AksharAI FastAPI Gateway"}
