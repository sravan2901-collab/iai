import sys
import os

# Adjust python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, SessionLocal
from app import models
from sqlalchemy import text

def clear_all_learner_accounts():
    print("=" * 70)
    print("           AKSHARAI — CLEAR LEARNER ACCOUNTS & PROFILES")
    print("=" * 70)

    db = SessionLocal()
    try:
        # Delete from dependent tables first
        tables_to_clear = [
            "learner_registration_progress",
            "learner_achievement",
            "learning_report",
            "progress_tracking",
            "voice_session",
            "recommendation",
            "path_lesson",
            "learning_path",
            "assessment_result",
            "learner_profile",
            "learner"
        ]

        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys = OFF;"))
            for table_name in tables_to_clear:
                try:
                    result = conn.execute(text(f"DELETE FROM {table_name};"))
                    print(f"[CLEAR] Table '{table_name}' cleared ({result.rowcount} rows deleted).")
                except Exception as ex:
                    print(f"[SKIP] Table '{table_name}': {ex}")
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            conn.commit()

        print("\n[SUCCESS] All learner accounts, profiles, and registration records have been cleared.")
        print("Seed curriculum data (languages, modules, lessons) remains intact.")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] Failed to clear accounts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_learner_accounts()
