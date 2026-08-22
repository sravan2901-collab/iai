import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("VERIFYING SPOKEN, WRITTEN, READING CURRICULUMS ACROSS ALL LANGUAGES IN DATABASE")
print("=" * 80)

languages = db.query(models.Language).all()

summary = []

for lang in languages:
    curriculums = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang.lang_id).all()
    c_names = [c.title for c in curriculums]
    print(f"\n[LANGUAGE] {lang.lang_name} (ISO Code: {lang.iso_code}, ID: {lang.lang_id})")
    print(f"  Count of Curriculums: {len(curriculums)}")
    for c in curriculums:
        modules = db.query(models.Module).filter(models.Module.curriculum_id == c.curriculum_id).all()
        print(f"  * Curriculum ID {c.curriculum_id}: '{c.title}' (Level: {c.level}) | Modules: {len(modules)}")
        for m in modules:
            lessons = db.query(models.Lesson).filter(models.Lesson.module_id == m.module_id).all()
            print(f"     └─ Module ID {m.module_id}: '{m.module_name}' (Skill: {m.skill_type}) | Lessons: {len(lessons)}")
    summary.append((lang.lang_name, lang.iso_code, len(curriculums)))

print("\n" + "=" * 80)
print("SUMMARY PER LANGUAGE:")
for name, iso, count in summary:
    print(f"  - {name} ({iso}): {count} Core Curriculums")
print("=" * 80)

db.close()
