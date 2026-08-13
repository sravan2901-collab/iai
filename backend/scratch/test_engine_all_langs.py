import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models
from app.services.learning_path_engine import generate_learning_path, get_active_path

db = SessionLocal()

for lang in ["en", "hi", "te", "ta", "es"]:
    path_id = generate_learning_path(100, target_lang=lang, db=db)
    active = get_active_path(100, db=db)
    lessons_count = len(active.get("path_lessons", [])) if active else 0
    print(f"Lang '{lang}': path_id={path_id}, active_path_id={active.get('path_id') if active else None}, lessons_count={lessons_count}")

db.close()
