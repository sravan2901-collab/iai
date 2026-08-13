import sys
import os
import json

# Add backend root directory to sys.path so imports resolve cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models
from app.services.proficiency_engine import get_learner_scores, predict_proficiency
from app.services.learning_path_engine import generate_learning_path, get_active_path


def run_learning_path_engine_test():
    print("=" * 80)
    print("        AKSHARAI LEARNING PATH ENGINE SERVICE VERIFICATION")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 1. Fetch seeded test learner (email: test@aksharai.dev)
        test_email = "test@aksharai.dev"
        learner = db.query(models.Learner).filter(models.Learner.email == test_email).first()
        if not learner:
            print(f"[ERROR] Test learner {test_email} not found in DB. Run load_database.py first.")
            return

        learner_id = learner.learner_id
        print(f"\n[TEST EVALUATION] Learner ID: {learner_id} (email: {test_email}, username: {learner.username})")

        # 2. Print scores and predicted proficiency
        scores = get_learner_scores(learner_id, db=db)
        predictions = predict_proficiency(learner_id, db=db)

        print("\n--- LEARNER SCORES ---")
        for skill, score in scores.items():
            print(f"  * {skill:<25} : {score} / 100.0")

        print("\n--- PREDICTED PROFICIENCY PER SKILL ---")
        for skill, level in predictions.items():
            print(f"  * {skill:<25} : {level}")

        # 3. Call generate_learning_path(learner_id)
        new_path_id = generate_learning_path(learner_id, db=db)
        print(f"\n[PATH GENERATED] Generated New LearningPath ID: {new_path_id}")

        # 4. Fetch and print get_active_path(learner_id)
        active_path_data = get_active_path(learner_id, db=db)

        print("\n--- ACTIVE LEARNING PATH STRUCTURE (get_active_path) ---")
        print(json.dumps(active_path_data, indent=2))

        print("\n" + "=" * 80)
        print("        LEARNING PATH ENGINE TEST EXECUTED SUCCESSFULLY")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    run_learning_path_engine_test()
