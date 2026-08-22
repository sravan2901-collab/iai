import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models
from app.services.learning_path_engine import get_active_path

db = SessionLocal()

print("Fetching active path for Learner 100 with target_lang='en':")
active_en = get_active_path(100, target_lang="en", db=db)

if active_en:
    print(f"Path ID: {active_en['path_id']}")
    for pl in active_en['path_lessons']:
        print(f"   -> Lesson ID {pl['lesson_id']}: '{pl['title']}' | Target: '{pl['target_text']}'")

db.close()
