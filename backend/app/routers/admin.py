"""
Admin Content Studio REST API Router for AksharAI Language Literacy Platform.

Provides management endpoints for admins/educators to:
- View platform content statistics and repository summaries
- Create and delete language curriculums, modules, and lessons
- Manage learning content across all supported languages
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter(prefix="/api/admin", tags=["Admin Content Studio & Content Management"])


# --- Request Schemas ---

class AdminLanguageCreate(BaseModel):
    lang_name: str
    iso_code: str


class AdminCurriculumCreate(BaseModel):
    lang_id: int
    title: str
    level: str = "FOUNDATIONAL"
    description: Optional[str] = None


class AdminModuleCreate(BaseModel):
    curriculum_id: int
    module_name: str
    sequence_no: int = 1
    skill_type: str = "Reading & Pronunciation"


class AdminLessonCreate(BaseModel):
    module_id: int
    title: str
    content_type: str = "Voice Practice"
    content_url: Optional[str] = None
    target_text: Optional[str] = None
    phonetic_script: Optional[str] = None
    difficulty_level: str = "FOUNDATIONAL"


# --- Endpoints ---

@router.get("/summary", summary="Get Content Repository Summary & Counts")
def get_content_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns platform statistics: counts of languages, curriculums, modules, lessons,
    assessments, and learners, along with full lists of languages and curriculums.
    """
    languages = db.query(models.Language).all()
    curriculums = db.query(models.Curriculum).all()

    lang_list = [{"lang_id": l.lang_id, "lang_name": l.lang_name, "iso_code": l.iso_code} for l in languages]
    curr_list = [
        {
            "curriculum_id": c.curriculum_id,
            "lang_id": c.lang_id,
            "title": c.title,
            "level": c.level,
            "description": c.description
        } for c in curriculums
    ]

    return {
        "languages_count": len(languages),
        "curriculums_count": len(curriculums),
        "modules_count": db.query(models.Module).count(),
        "lessons_count": db.query(models.Lesson).count(),
        "assessments_count": db.query(models.Assessment).count(),
        "learners_count": db.query(models.Learner).count(),
        "languages": lang_list,
        "curriculums": curr_list
    }


@router.get("/modules", summary="Get All Content Modules")
def get_all_modules(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Returns all modules in the system joined with curriculum title and language details.
    """
    modules = (
        db.query(models.Module, models.Curriculum, models.Language)
        .join(models.Curriculum, models.Module.curriculum_id == models.Curriculum.curriculum_id)
        .join(models.Language, models.Curriculum.lang_id == models.Language.lang_id)
        .order_by(models.Module.module_id)
        .all()
    )

    result = []
    for m, c, l in modules:
        result.append({
            "module_id": m.module_id,
            "curriculum_id": m.curriculum_id,
            "module_name": m.module_name,
            "sequence_no": m.sequence_no,
            "skill_type": m.skill_type,
            "curriculum_title": c.title,
            "lang_id": l.lang_id,
            "lang_name": l.lang_name,
            "iso_code": l.iso_code,
            "lessons_count": len(m.lessons)
        })

    return result


@router.get("/lessons", summary="Get All Repository Lessons")
def get_all_lessons(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Returns all lessons in the repository joined with module, curriculum, and language.
    """
    lessons = (
        db.query(models.Lesson, models.Module, models.Curriculum, models.Language)
        .join(models.Module, models.Lesson.module_id == models.Module.module_id)
        .join(models.Curriculum, models.Module.curriculum_id == models.Curriculum.curriculum_id)
        .join(models.Language, models.Curriculum.lang_id == models.Language.lang_id)
        .order_by(models.Lesson.lesson_id.desc())
        .all()
    )

    result = []
    for les, m, c, l in lessons:
        result.append({
            "lesson_id": les.lesson_id,
            "module_id": les.module_id,
            "title": les.title,
            "content_type": les.content_type,
            "content_url": les.content_url,
            "target_text": les.target_text,
            "phonetic_script": les.phonetic_script,
            "difficulty_level": les.difficulty_level,
            "module_name": m.module_name,
            "skill_type": m.skill_type,
            "curriculum_title": c.title,
            "lang_name": l.lang_name,
            "iso_code": l.iso_code
        })

    return result


@router.post("/languages", summary="Add New Language")
def create_language(payload: AdminLanguageCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Adds a new language to the platform.
    """
    existing = db.query(models.Language).filter(models.Language.iso_code == payload.iso_code.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language with ISO code '{payload.iso_code}' already exists."
        )

    new_lang = models.Language(
        lang_name=payload.lang_name.strip(),
        iso_code=payload.iso_code.lower().strip()
    )
    db.add(new_lang)
    db.commit()
    db.refresh(new_lang)

    return {
        "status": "success",
        "message": f"Language '{new_lang.lang_name}' added successfully.",
        "lang_id": new_lang.lang_id,
        "iso_code": new_lang.iso_code
    }


@router.post("/curriculums", summary="Add New Curriculum")
def create_curriculum(payload: AdminCurriculumCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Adds a new curriculum under a language.
    """
    lang = db.query(models.Language).filter(models.Language.lang_id == payload.lang_id).first()
    if not lang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language ID {payload.lang_id} not found."
        )

    new_curr = models.Curriculum(
        lang_id=payload.lang_id,
        title=payload.title.strip(),
        level=payload.level.upper().strip(),
        description=payload.description
    )
    db.add(new_curr)
    db.commit()
    db.refresh(new_curr)

    return {
        "status": "success",
        "message": f"Curriculum '{new_curr.title}' created successfully.",
        "curriculum_id": new_curr.curriculum_id
    }


@router.post("/modules", summary="Add New Module")
def create_module(payload: AdminModuleCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Creates a new learning module under a curriculum.
    """
    curr = db.query(models.Curriculum).filter(models.Curriculum.curriculum_id == payload.curriculum_id).first()
    if not curr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curriculum ID {payload.curriculum_id} not found."
        )

    new_mod = models.Module(
        curriculum_id=payload.curriculum_id,
        module_name=payload.module_name.strip(),
        sequence_no=payload.sequence_no,
        skill_type=payload.skill_type.strip()
    )
    db.add(new_mod)
    db.commit()
    db.refresh(new_mod)

    return {
        "status": "success",
        "message": f"Module '{new_mod.module_name}' created successfully.",
        "module_id": new_mod.module_id,
        "curriculum_id": new_mod.curriculum_id
    }


@router.post("/lessons", summary="Add New Lesson to Module")
def create_lesson(payload: AdminLessonCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Creates and persists a new lesson in the repository under a specified module.
    """
    mod = db.query(models.Module).filter(models.Module.module_id == payload.module_id).first()
    if not mod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module ID {payload.module_id} not found."
        )

    new_les = models.Lesson(
        module_id=payload.module_id,
        title=payload.title.strip(),
        content_type=payload.content_type.strip(),
        content_url=payload.content_url or f"/audio/lessons/{payload.module_id}_practice.mp3",
        target_text=payload.target_text.strip() if payload.target_text else None,
        phonetic_script=payload.phonetic_script,
        difficulty_level=payload.difficulty_level.upper().strip()
    )
    db.add(new_les)
    db.commit()
    db.refresh(new_les)

    return {
        "status": "success",
        "message": f"Lesson '{new_les.title}' created successfully.",
        "lesson_id": new_les.lesson_id,
        "module_id": new_les.module_id
    }


@router.delete("/lessons/{lesson_id}", summary="Delete Lesson from Repository")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Removes a lesson from the content repository.
    """
    les = db.query(models.Lesson).filter(models.Lesson.lesson_id == lesson_id).first()
    if not les:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson ID {lesson_id} not found."
        )

    title = les.title
    db.delete(les)
    db.commit()

    return {
        "status": "success",
        "message": f"Lesson '{title}' (ID {lesson_id}) deleted successfully.",
        "lesson_id": lesson_id
    }


@router.delete("/modules/{module_id}", summary="Delete Module")
def delete_module(module_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Removes a module and its associated lessons.
    """
    mod = db.query(models.Module).filter(models.Module.module_id == module_id).first()
    if not mod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module ID {module_id} not found."
        )

    mod_name = mod.module_name
    db.delete(mod)
    db.commit()

    return {
        "status": "success",
        "message": f"Module '{mod_name}' (ID {module_id}) deleted successfully.",
        "module_id": module_id
    }
