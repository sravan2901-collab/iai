import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("Deleting all existing PathLessons, LearningPaths, Lessons, Modules, and Curriculums...")

db.query(models.PathLesson).delete()
db.query(models.LearningPath).delete()
db.query(models.Lesson).delete()
db.query(models.Module).delete()
db.query(models.Curriculum).delete()
db.commit()

print("Deleted all old curriculum, module, and lesson data successfully.")

languages = db.query(models.Language).all()

three_curriculums_config = [
    {
        "title": "Spoken Curriculum",
        "level": "FOUNDATIONAL",
        "description": "Clean slate curriculum for spoken language practice, pronunciation, and oral communication.",
        "module_name": "Spoken Foundation Module",
        "skill_type": "SPOKEN",
        "content_type": "Voice Practice",
        "lesson_title": "Blank Spoken Practice Lesson",
        "target_text": "Practice spoken words clearly",
        "phonetic_script": "['Spoken', 'Practice']"
    },
    {
        "title": "Written Curriculum",
        "level": "FOUNDATIONAL",
        "description": "Clean slate curriculum for written language practice, spelling, and sentence composition.",
        "module_name": "Written Foundation Module",
        "skill_type": "WRITTEN",
        "content_type": "Written Practice",
        "lesson_title": "Blank Written Practice Lesson",
        "target_text": "Write simple words correctly",
        "phonetic_script": "['Written', 'Practice']"
    },
    {
        "title": "Reading Curriculum",
        "level": "FOUNDATIONAL",
        "description": "Clean slate curriculum for reading comprehension, phonics, and literary understanding.",
        "module_name": "Reading Foundation Module",
        "skill_type": "READING",
        "content_type": "Functional Reading",
        "lesson_title": "Blank Reading Practice Lesson",
        "target_text": "Read text with accuracy and understanding",
        "phonetic_script": "['Reading', 'Practice']"
    }
]

total_curriculums = 0
total_modules = 0
total_lessons = 0

for lang in languages:
    for cfg in three_curriculums_config:
        curr = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} - {cfg['title']}",
            level=cfg["level"],
            description=f"{cfg['description']} ({lang.lang_name})"
        )
        db.add(curr)
        db.commit()
        db.refresh(curr)
        total_curriculums += 1
        
        mod = models.Module(
            curriculum_id=curr.curriculum_id,
            module_name=cfg["module_name"],
            sequence_no=1,
            skill_type=cfg["skill_type"]
        )
        db.add(mod)
        db.commit()
        db.refresh(mod)
        total_modules += 1
        
        les = models.Lesson(
            module_id=mod.module_id,
            title=cfg["lesson_title"],
            content_type=cfg["content_type"],
            content_url=f"/audio/{lang.iso_code}/blank_{cfg['skill_type'].lower()}.mp3",
            target_text=cfg["target_text"],
            phonetic_script=cfg["phonetic_script"],
            difficulty_level="FOUNDATIONAL"
        )
        db.add(les)
        db.commit()
        total_lessons += 1

print(f"Created exactly {total_curriculums} Curriculums, {total_modules} Modules, and {total_lessons} Lessons across all {len(languages)} languages!")
db.close()
