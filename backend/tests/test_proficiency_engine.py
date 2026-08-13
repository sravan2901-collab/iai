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

        # 2. Get or create a seeded test learner
        test_email = "proficiency_test_learner@aksharai.com"
        learner = db.query(models.Learner).filter(models.Learner.email == test_email).first()
        if not learner:
            learner = models.Learner(
                email=test_email,
                username="prof_test_user",
                password_hash="seeded_hash_123"
            )
            db.add(learner)
            db.commit()
            db.refresh(learner)

        learner_id = learner.learner_id
        print(f"\n[TEST SEED] Learner ID: {learner_id} (email: {test_email})")

        # 3. Create or find test language & curriculum
        lang = db.query(models.Language).filter(models.Language.iso_code == "en").first()
        if not lang:
            lang = models.Language(iso_code="en", lang_name="English")
            db.add(lang)
            db.commit()
            db.refresh(lang)

        curr = db.query(models.Curriculum).filter(models.Curriculum.lang_id == lang.lang_id).first()
        if not curr:
            curr = models.Curriculum(lang_id=lang.lang_id, title="English Literacy", level="FOUNDATIONAL")
            db.add(curr)
            db.commit()
            db.refresh(curr)

        # 4. Seed 3 Modules for specific skills: Reading & Pronunciation, Word Formation, Literature
        # (Grammar will deliberately be left un-assessed to test FOUNDATIONAL default)
        skills_to_seed = [
            ("Reading & Pronunciation Module", "Reading & Pronunciation", 85.0),
            ("Word Formation Module", "Word Formation", 60.0),
            ("Literature Module", "Literature", 30.0)
        ]

        for mod_name, skill_type, test_score in skills_to_seed:
            mod = db.query(models.Module).filter(
                models.Module.curriculum_id == curr.curriculum_id,
                models.Module.module_name == mod_name
            ).first()
            if not mod:
                mod = models.Module(
                    curriculum_id=curr.curriculum_id,
                    module_name=mod_name,
                    sequence_no=1,
                    skill_type=skill_type
                )
                db.add(mod)
                db.commit()
                db.refresh(mod)

            ass = db.query(models.Assessment).filter(models.Assessment.module_id == mod.module_id).first()
            if not ass:
                ass = models.Assessment(
                    module_id=mod.module_id,
                    assessment_type="MODULE_QUIZ",
                    title=f"Quiz for {mod_name}",
                    total_marks=100
                )
                db.add(ass)
                db.commit()
                db.refresh(ass)

            # Clean previous test results for clean run
            db.query(models.AssessmentResult).filter(
                models.AssessmentResult.learner_id == learner_id,
                models.AssessmentResult.assessment_id == ass.assessment_id
            ).delete()
            db.commit()

            # Add Attempt 1 (older, lower score)
            res_att1 = models.AssessmentResult(
                learner_id=learner_id,
                assessment_id=ass.assessment_id,
                score=test_score - 10.0,
                attempt_no=1,
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(res_att1)

            # Add Attempt 2 (latest attempt_no, higher score)
            res_att2 = models.AssessmentResult(
                learner_id=learner_id,
                assessment_id=ass.assessment_id,
                score=test_score,
                attempt_no=2,
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(res_att2)
            db.commit()

        # 5. Execute get_learner_scores()
        scores = get_learner_scores(learner_id, db=db)
        print("\n--- LATEST SCORES PER SKILL TYPE (get_learner_scores) ---")
        for skill, score in scores.items():
            print(f"  * {skill:<25} : {score} / 100.0")

        # 6. Execute predict_proficiency()
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
