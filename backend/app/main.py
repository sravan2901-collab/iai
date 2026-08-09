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
            {"iso_code": "kn", "lang_name": "Kannada (ಕನ್ನಡ)"},
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

ensure_schema_migrations()
seed_languages()

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
