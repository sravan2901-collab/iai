import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("\n=== CURRENT ACTIVE LEARNING PATH FOR LEARNER 100 ===")
lp = db.query(models.LearningPath).filter(models.LearningPath.learner_id == 100, models.LearningPath.status == "ACTIVE").first()
if lp:
    print(f"Path ID={lp.path_id}, Level={lp.current_level}, Target={lp.target_proficiency}")
    pls = db.query(models.PathLesson, models.Lesson).join(models.Lesson, models.PathLesson.lesson_id == models.Lesson.lesson_id).filter(models.PathLesson.path_id == lp.path_id).all()
    for pl, les in pls:
        module = db.query(models.Module).filter(models.Module.module_id == les.module_id).first()
        curr = db.query(models.Curriculum).filter(models.Curriculum.curriculum_id == module.curriculum_id).first() if module else None
        lang = db.query(models.Language).filter(models.Language.lang_id == curr.lang_id).first() if curr else None
        
        safe_title = les.title.encode('ascii', 'ignore').decode()
        safe_target = les.target_text.encode('ascii', 'ignore').decode()
        lang_code = lang.iso_code if lang else "UNKNOWN"
        print(f"   PathLesson {pl.path_lesson_id} (Lang={lang_code}, Module={module.module_id if module else 'N/A'}): '{safe_title}' | Target: '{safe_target}'")

db.close()
