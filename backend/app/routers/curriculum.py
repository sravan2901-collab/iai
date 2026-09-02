from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.content_repository import MultilingualContentRepository

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

@router.get("/pillars/{lang_param}")
def get_curriculum_pillars(lang_param: str, db: Session = Depends(get_db)):
    """
    Returns the 3 core curriculums (Spoken, Written, Reading) and their 8 progressive sub-modules for the requested language.
    """
    # Resolve language ID
    lang_obj = None
    if lang_param.isdigit():
        lang_obj = db.query(models.Language).filter(models.Language.lang_id == int(lang_param)).first()
    else:
        lang_obj = db.query(models.Language).filter(models.Language.iso_code == lang_param.lower()).first()
    
    if not lang_obj:
        lang_obj = db.query(models.Language).filter(models.Language.iso_code == 'en').first()
    
    lang_id = lang_obj.lang_id if lang_obj else 1

    curriculums = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang_id).all()
    
    res = {
        "lang_id": lang_id,
        "lang_code": lang_obj.iso_code if lang_obj else "en",
        "lang_name": lang_obj.lang_name if lang_obj else "English",
        "pillars": []
    }

    skill_type_map = {
        "SPOKEN": {"id": 1, "title": "Spoken Curriculum", "color": "from-amber-500 to-orange-600"},
        "WRITTEN": {"id": 2, "title": "Written Curriculum", "color": "from-blue-500 to-indigo-600"},
        "READING": {"id": 3, "title": "Reading Curriculum", "color": "from-emerald-500 to-teal-600"}
    }

    for c in curriculums:
        modules = db.query(models.Module).filter(models.Module.curriculum_id == c.curriculum_id).order_by(models.Module.sequence_no).all()
        for mod in modules:
            st = mod.skill_type.upper() if mod.skill_type else "SPOKEN"
            if st not in ["SPOKEN", "WRITTEN", "READING"]:
                st = "SPOKEN" if "SPOKEN" in st or "VOICE" in st else ("WRITTEN" if "WRITE" in st else "READING")

            lessons = db.query(models.Lesson).filter(models.Lesson.module_id == mod.module_id).all()

            # Find or create pillar in res
            pillar_entry = next((p for p in res["pillars"] if p["skill_type"] == st), None)
            if not pillar_entry:
                meta = skill_type_map.get(st, skill_type_map["SPOKEN"])
                pillar_entry = {
                    "id": meta["id"],
                    "title": f"{c.title.split(' - ')[-1] if ' - ' in c.title else c.title}",
                    "skill_type": st,
                    "color": meta["color"],
                    "sub_modules_count": 0,
                    "sub_modules": []
                }
                res["pillars"].append(pillar_entry)

            les_list = [
                {
                    "lesson_id": les.lesson_id,
                    "title": les.title,
                    "content_type": les.content_type,
                    "target_text": les.target_text,
                    "phonetic_script": les.phonetic_script,
                    "difficulty_level": les.difficulty_level
                } for les in lessons
            ]

            pillar_entry["sub_modules"].append({
                "module_id": mod.module_id,
                "module_name": mod.module_name,
                "sequence_no": mod.sequence_no,
                "stage": les_list[0]["difficulty_level"] if les_list else f"STAGE_{mod.sequence_no}",
                "lessons": les_list
            })
            pillar_entry["sub_modules_count"] = len(pillar_entry["sub_modules"])

    return res

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
