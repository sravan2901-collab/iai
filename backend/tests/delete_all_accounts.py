import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models import Learner, LearnerProfile
from app.auth import get_password_hash

def delete_all_accounts_and_reset():
    db = SessionLocal()
    try:
        print("\n=================== DELETING ALL LEARNER ACCOUNTS ===================")
        
        # Delete all learner profiles and learner accounts
        num_profiles = db.query(LearnerProfile).delete()
        num_learners = db.query(Learner).delete()
        
        db.commit()
        print(f"[SUCCESS] Deleted {num_profiles} Learner Profile Records")
        print(f"[SUCCESS] Deleted {num_learners} Learner Account Records")
        
        # Provision primary account for sravan2901@gmail.com with password 'Elsa$123'
        email = "sravan2901@gmail.com"
        exact_pass = "Elsa$123"
        hashed = get_password_hash(exact_pass)
        
        primary_learner = Learner(
            email=email,
            username="sravan2901",
            password_hash=hashed,
            current_lang_id=1,
            is_email_verified=True
        )
        db.add(primary_learner)
        db.commit()
        db.refresh(primary_learner)
        
        primary_profile = LearnerProfile(
            learner_id=primary_learner.learner_id,
            first_name="Sravan",
            last_name="Kumar",
            literacy_level="FOUNDATIONAL",
            streak_count=1,
            total_points=50
        )
        db.add(primary_profile)
        db.commit()
        
        print(f"[SUCCESS] Re-initialized fresh account for '{email}' with password '{exact_pass}' (Learner ID: {primary_learner.learner_id})")
        print("=================== ALL ACCOUNTS DELETED & FRESH INITIALIZATION COMPLETED! ===================\n")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during account deletion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_accounts_and_reset()
