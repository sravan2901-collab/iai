import sys
import os
import json
from fastapi.testclient import TestClient

# Add backend root directory to sys.path so imports resolve cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def run_learners_router_test():
    print("=" * 80)
    print("        AKSHARAI LEARNERS REST API ROUTER INTEGRATION TEST")
    print("=" * 80)

    client = TestClient(app)
    valid_learner_id = 100
    invalid_learner_id = 999999

    # --------------------------------------------------------------------------
    # 1. GET /api/learners/{learner_id}/proficiency
    # --------------------------------------------------------------------------
    print(f"\n[TEST 1] GET /api/learners/{valid_learner_id}/proficiency")
    res1 = client.get(f"/api/learners/{valid_learner_id}/proficiency")
    print(f"  -> HTTP {res1.status_code}")
    print(f"  -> Response JSON: {res1.json()}")
    assert res1.status_code == 200, f"Expected 200, got {res1.status_code}"
    assert "Reading & Pronunciation" in res1.json(), "Missing skill key"

    print(f"\n[TEST 1.1] GET /api/learners/{invalid_learner_id}/proficiency (Invalid Learner)")
    res1_inv = client.get(f"/api/learners/{invalid_learner_id}/proficiency")
    print(f"  -> HTTP {res1_inv.status_code}")
    print(f"  -> Response JSON: {res1_inv.json()}")
    assert res1_inv.status_code == 404, f"Expected 404, got {res1_inv.status_code}"
    assert res1_inv.json() == {"detail": f"Learner with ID {invalid_learner_id} not found."}

    # --------------------------------------------------------------------------
    # 2. POST /api/learners/{learner_id}/learning-path/generate
    # --------------------------------------------------------------------------
    print(f"\n[TEST 2] POST /api/learners/{valid_learner_id}/learning-path/generate")
    res2 = client.post(f"/api/learners/{valid_learner_id}/learning-path/generate")
    print(f"  -> HTTP {res2.status_code}")
    print(f"  -> Response JSON summary: path_id = {res2.json().get('path_id')}")
    assert res2.status_code == 200, f"Expected 200, got {res2.status_code}"
    assert "path_id" in res2.json(), "Missing path_id in response"
    assert "learning_path" in res2.json(), "Missing learning_path in response"

    print(f"\n[TEST 2.1] POST /api/learners/{invalid_learner_id}/learning-path/generate (Invalid Learner)")
    res2_inv = client.post(f"/api/learners/{invalid_learner_id}/learning-path/generate")
    print(f"  -> HTTP {res2_inv.status_code}")
    print(f"  -> Response JSON: {res2_inv.json()}")
    assert res2_inv.status_code == 404, f"Expected 404, got {res2_inv.status_code}"

    # --------------------------------------------------------------------------
    # 3. GET /api/learners/{learner_id}/learning-path
    # --------------------------------------------------------------------------
    print(f"\n[TEST 3] GET /api/learners/{valid_learner_id}/learning-path")
    res3 = client.get(f"/api/learners/{valid_learner_id}/learning-path")
    print(f"  -> HTTP {res3.status_code}")
    print(f"  -> Response JSON path_id = {res3.json().get('path_id')}, target = {res3.json().get('target_proficiency')}")
    assert res3.status_code == 200, f"Expected 200, got {res3.status_code}"
    assert res3.json()["status"] == "ACTIVE", "Path status should be ACTIVE"

    print(f"\n[TEST 3.1] GET /api/learners/{invalid_learner_id}/learning-path (Invalid Learner)")
    res3_inv = client.get(f"/api/learners/{invalid_learner_id}/learning-path")
    print(f"  -> HTTP {res3_inv.status_code}")
    print(f"  -> Response JSON: {res3_inv.json()}")
    assert res3_inv.status_code == 404, f"Expected 404, got {res3_inv.status_code}"

    # --------------------------------------------------------------------------
    # 4. GET /api/learners/{learner_id}/recommendations
    # --------------------------------------------------------------------------
    print(f"\n[TEST 4] GET /api/learners/{valid_learner_id}/recommendations")
    res4 = client.get(f"/api/learners/{valid_learner_id}/recommendations")
    print(f"  -> HTTP {res4.status_code}")
    print(f"  -> Recommendations count = {len(res4.json())}")
    assert res4.status_code == 200, f"Expected 200, got {res4.status_code}"
    assert isinstance(res4.json(), list), "Expected list of recommendations"

    print(f"\n[TEST 4.1] GET /api/learners/{invalid_learner_id}/recommendations (Invalid Learner)")
    res4_inv = client.get(f"/api/learners/{invalid_learner_id}/recommendations")
    print(f"  -> HTTP {res4_inv.status_code}")
    print(f"  -> Response JSON: {res4_inv.json()}")
    assert res4_inv.status_code == 404, f"Expected 404, got {res4_inv.status_code}"

    print("\n" + "=" * 80)
    print("        ALL 8 REST API ENDPOINT TESTS PASSED SUCCESSFULLY (100%)")
    print("=" * 80)


if __name__ == "__main__":
    run_learners_router_test()
