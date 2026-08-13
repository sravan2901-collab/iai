import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

modules = db.query(models.Module).all()
print(f"Total Modules in DB: {len(modules)}")

for m in modules:
    lessons = db.query(models.Lesson).filter(models.Lesson.module_id == m.module_id).all()
    if "Workplace" in m.module_name or "Communication" in m.module_name or "Work" in m.module_name or m.curriculum_id == 2:
        print(f"Module ID={m.module_id}, Curriculum ID={m.curriculum_id}, Name='{m.module_name.encode('ascii', 'ignore').decode()}', Skill='{m.skill_type}'")
        for l in lessons:
            print(f"   -> Lesson ID={l.lesson_id}, Title='{l.title.encode('ascii', 'ignore').decode()}', Type='{l.content_type}', Diff='{l.difficulty_level}'")
            print(f"      Target: '{l.target_text.encode('ascii', 'ignore').decode()}'")

db.close()
