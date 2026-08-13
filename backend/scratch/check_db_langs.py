import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()
langs = db.query(models.Language).all()
print("Languages in DB:")
for l in langs:
    print(f"  lang_id={l.lang_id}, language_name={getattr(l, 'language_name', getattr(l, 'name', '') )}, iso_code={getattr(l, 'iso_code', '')}")

curriculums = db.query(models.Curriculum).all()
print("\nCurriculums in DB:")
for c in curriculums:
    print(f"  curriculum_id={c.curriculum_id}, lang_id={c.lang_id}, title={c.title}")

learners = db.query(models.Learner).all()
print("\nLearners in DB:")
for learner in learners:
    print(f"  learner_id={learner.learner_id}, username={getattr(learner, 'username', ''), }, current_lang_id={getattr(learner, 'current_lang_id', '')}")

db.close()
