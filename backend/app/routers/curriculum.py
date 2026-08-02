from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List

router = APIRouter(prefix="/api/curriculum", tags=["Curriculum & Lessons"])

@router.get("/languages", response_model=List[schemas.LanguageOut])
def get_languages(db: Session = Depends(get_db)):
    languages = db.query(models.Language).all()
    if not languages:
        # Default seed return if DB is empty
        return [
            {"lang_id": 1, "lang_name": "Hindi (हिन्दी)", "iso_code": "hi"},
            {"lang_id": 2, "lang_name": "English", "iso_code": "en"},
            {"lang_id": 3, "lang_name": "Tamil (தமிழ்)", "iso_code": "ta"},
            {"lang_id": 4, "lang_name": "Telugu (తెలుగు)", "iso_code": "te"}
        ]
    return languages

@router.get("/{lang_id}")
def get_curriculum_by_language(lang_id: int, db: Session = Depends(get_db)):
    curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang_id).first()
    if not curriculum:
        # Fallback to Hindi default
        curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == 1).first()
    
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found for selected language")

    modules = db.query(models.Module).filter(models.Module.curriculum_id == curriculum.curriculum_id).order_by(models.Module.sequence_no).all()
    
    res_modules = []
    for mod in modules:
        lessons = db.query(models.Lesson).filter(models.Lesson.module_id == mod.module_id).all()
        res_modules.append({
            "module_id": mod.module_id,
            "module_name": mod.module_name,
            "sequence_no": mod.sequence_no,
            "skill_type": mod.skill_type,
            "lessons": [
                {
                    "lesson_id": les.lesson_id,
                    "title": les.title,
                    "content_type": les.content_type,
                    "target_text": les.target_text,
                    "phonetic_script": les.phonetic_script,
                    "difficulty_level": les.difficulty_level
                } for les in lessons
            ]
        })

    return {
        "curriculum_id": curriculum.curriculum_id,
        "lang_id": curriculum.lang_id,
        "title": curriculum.title,
        "description": curriculum.description,
        "modules": res_modules
    }

@router.get("/lesson/{lesson_id}", response_model=schemas.LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
