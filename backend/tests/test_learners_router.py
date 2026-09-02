import sys
import os
import json
from fastapi.testclient import TestClient

# Add backend root directory to sys.path so imports resolve cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import create_access_token


def run_learners_router_test():
    print("=" * 80)
    print("        AKSHARAI LEARNERS REST API ROUTER INTEGRATION TEST")
    print("=" * 80)

    client = TestClient(app)
    db = SessionLocal()
    
    # Ensure test learner 100 exists
    learner100 = db.query(models.Learner).filter(models.Learner.learner_id == 100).first()
    if not learner100:
        learner100 = models.Learner(learner_id=100, email="test100@akshar.ai", username="test100", password_hash="hash")
        db.add(learner100)
        db.commit()

    # Ensure test learner 200 exists for cross-tenant testing
    learner200 = db.query(models.Learner).filter(models.Learner.learner_id == 200).first()
    if not learner200:
        learner200 = models.Learner(learner_id=200, email="test200@akshar.ai", username="test200", password_hash="hash")
        db.add(learner200)
        db.commit()

    token100 = create_access_token({"sub": "100", "email": "test100@akshar.ai"})
    auth_headers = {"Authorization": f"Bearer {token100}"}

    # Secondary learner for IDOR cross-tenant test
    token200 = create_access_token({"sub": "200", "email": "test200@akshar.ai"})
    other_headers = {"Authorization": f"Bearer {token200}"}

    valid_learner_id = 100
    invalid_learner_id = 999999

    # --------------------------------------------------------------------------
    # 1. GET /api/learners/{learner_id}/proficiency
    # --------------------------------------------------------------------------
    print(f"\n[TEST 1] GET /api/learners/{valid_learner_id}/proficiency (Authorized)")
    res1 = client.get(f"/api/learners/{valid_learner_id}/proficiency", headers=auth_headers)
    assert res1.status_code == 200, f"Expected 200, got {res1.status_code}"
    print(f"  -> HTTP {res1.status_code}")

    print(f"\n[TEST 1.1] GET /api/learners/{valid_learner_id}/proficiency (Unauthenticated 401)")
    res1_unauth = client.get(f"/api/learners/{valid_learner_id}/proficiency")
    assert res1_unauth.status_code == 401, f"Expected 401, got {res1_unauth.status_code}"
    print(f"  -> HTTP {res1_unauth.status_code} [BLOCKED]")

    print(f"\n[TEST 1.2] GET /api/learners/{valid_learner_id}/proficiency (Cross-Tenant IDOR 403)")
    res1_cross = client.get(f"/api/learners/{valid_learner_id}/proficiency", headers=other_headers)
    assert res1_cross.status_code == 403, f"Expected 403, got {res1_cross.status_code}"
    print(f"  -> HTTP {res1_cross.status_code} [BLOCKED]")

    print(f"\n[TEST 1.3] GET /api/learners/{invalid_learner_id}/proficiency (Invalid Learner 404)")
    res1_inv = client.get(f"/api/learners/{invalid_learner_id}/proficiency", headers=auth_headers)
    assert res1_inv.status_code == 404, f"Expected 404, got {res1_inv.status_code}"
    print(f"  -> HTTP {res1_inv.status_code}")

    # --------------------------------------------------------------------------
    # 2. POST /api/learners/{learner_id}/learning-path/generate
    # --------------------------------------------------------------------------
    print(f"\n[TEST 2] POST /api/learners/{valid_learner_id}/learning-path/generate (Authorized)")
    res2 = client.post(f"/api/learners/{valid_learner_id}/learning-path/generate", headers=auth_headers)
    assert res2.status_code == 200, f"Expected 200, got {res2.status_code}"
    print(f"  -> HTTP {res2.status_code}")

    # --------------------------------------------------------------------------
    # 3. GET /api/learners/{learner_id}/learning-path
    # --------------------------------------------------------------------------
    print(f"\n[TEST 3] GET /api/learners/{valid_learner_id}/learning-path (Authorized)")
    res3 = client.get(f"/api/learners/{valid_learner_id}/learning-path", headers=auth_headers)
    assert res3.status_code == 200, f"Expected 200, got {res3.status_code}"
    print(f"  -> HTTP {res3.status_code}")

    # --------------------------------------------------------------------------
    # 4. GET /api/learners/{learner_id}/recommendations
    # --------------------------------------------------------------------------
    print(f"\n[TEST 4] GET /api/learners/{valid_learner_id}/recommendations (Authorized)")
    res4 = client.get(f"/api/learners/{valid_learner_id}/recommendations", headers=auth_headers)
    assert res4.status_code == 200, f"Expected 200, got {res4.status_code}"
    print(f"  -> HTTP {res4.status_code}")

    db.close()
    print("\n" + "=" * 80)
    print("        ALL SECURITY & ROUTER TESTS PASSED SUCCESSFULLY (100%)")
    print("=" * 80)


if __name__ == "__main__":
    run_learners_router_test()
