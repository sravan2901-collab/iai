from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.content_repository import MultilingualContentRepository
from typing import List, Optional

router = APIRouter(prefix="/api/curriculum", tags=["Curriculum & Lessons"])

@router.get("/languages")
def get_languages(db: Session = Depends(get_db)):
    """
    Returns supported languages list from database or content repository.
    """
    languages = db.query(models.Language).all()
    if not languages:
        return MultilingualContentRepository.get_supported_languages()
    return languages

@router.get("/repository/{lang_code}")
def get_multilingual_content_repository(lang_code: str):
    """
    Returns the complete multilingual content repository for a specified language code (en, hi, te, ta, mr, bn, kn, es).
    """
    return MultilingualContentRepository.get_content_by_language(lang_code)

@router.get("/repository/{lang_code}/search")
def search_multilingual_content(lang_code: str, q: str = Query(..., min_length=1)):
    """
    Searches the multilingual content repository for lessons or phrases matching query string.
    """
    return MultilingualContentRepository.search_content(lang_code, q)

@router.get("/{lang_id}")
def get_curriculum_by_language(lang_id: int, db: Session = Depends(get_db)):
    curriculum = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang_id).first()
    if not curriculum:
        # Fallback to default curriculum
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
