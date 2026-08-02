import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models import Learner, LearnerProfile, AssessmentResult, LearningPath, Recommendation, VoiceSession, ProgressTracking, LearningReport, LearnerAchievement, LearnerRegistrationProgress

def wipe_all_accounts_completely():
    db = SessionLocal()
    try:
        print("\n=================== WIPING ALL ACCOUNTS (INCLUDING PRIMARY ACCOUNT) ===================")
        
        # Delete dependent tables
        db.query(LearnerAchievement).delete()
        db.query(LearningReport).delete()
        db.query(ProgressTracking).delete()
        db.query(VoiceSession).delete()
        db.query(Recommendation).delete()
        db.query(LearningPath).delete()
        db.query(AssessmentResult).delete()
        db.query(LearnerRegistrationProgress).delete()
        
        # Delete LearnerProfiles and Learners
        num_profiles = db.query(LearnerProfile).delete()
        num_learners = db.query(Learner).delete()
        
        db.commit()
        
        print(f"[SUCCESS] Deleted {num_profiles} Learner Profile Records")
        print(f"[SUCCESS] Deleted {num_learners} Learner Account Records (Including Primary Account)")
        print(f"[SUCCESS] Remaining Learners in Database: {db.query(Learner).count()}")
        print("=================== DATABASE TOTALLY WIPED (0 ACCOUNTS REMAINING)! ===================\n")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during database wipe: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    wipe_all_accounts_completely()
