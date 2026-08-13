import sys
import os
from datetime import datetime, timezone

# Add backend root directory to sys.path so imports resolve cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app import models
from app.services.proficiency_engine import get_learner_scores, predict_proficiency, ensure_default_benchmarks


def run_proficiency_engine_test():
    print("=" * 80)
    print("        AKSHARAI PROFICIENCY ENGINE SERVICE VERIFICATION")
    print("=" * 80)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed benchmarks
        ensure_default_benchmarks(db)

        # Query seeded test learner from seed_data_test.sql (email: test@aksharai.dev)
        test_email = "test@aksharai.dev"
        learner = db.query(models.Learner).filter(models.Learner.email == test_email).first()
        learner_id = learner.learner_id if learner else 100
        print(f"\n[TEST EVALUATION] Testing Learner ID: {learner_id} (email: {test_email if learner else 'fallback'})")

        # Execute get_learner_scores()
        scores = get_learner_scores(learner_id, db=db)
        print("\n--- LATEST SCORES PER SKILL TYPE (get_learner_scores) ---")
        for skill, score in scores.items():
            print(f"  * {skill:<25} : {score} / 100.0")

        # Execute predict_proficiency()
        predictions = predict_proficiency(learner_id, db=db)
        print("\n--- PREDICTED PROFICIENCY LEVELS PER SKILL TYPE (predict_proficiency) ---")
        for skill, level in predictions.items():
            print(f"  * {skill:<25} : {level}")

        print("\n" + "=" * 80)
        print("        PROFICIENCY ENGINE TEST EXECUTED SUCCESSFULLY")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    run_proficiency_engine_test()
