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
            conn.commit()
    except Exception as e:
        print(f"[DB MIGRATION NOTICE] Auto-migration skipped or failed: {e}")

ensure_schema_migrations()

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
