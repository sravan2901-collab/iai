import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models import Learner
from app.auth import get_password_hash, verify_password

def set_password():
    db = SessionLocal()
    email = "sravan2901@gmail.com"
    target_pass = "Elsa$123"

    learner = db.query(Learner).filter(Learner.email == email).first()
    if not learner:
        print(f"Learner {email} not found.")
        return

    new_hash = get_password_hash(target_pass)
    learner.password_hash = new_hash
    db.commit()
    db.refresh(learner)

    print(f"SUCCESS: Set password for {email} to exact string: '{target_pass}'")
    print(f"Verification Check: {verify_password(target_pass, learner.password_hash)}")

if __name__ == "__main__":
    set_password()
