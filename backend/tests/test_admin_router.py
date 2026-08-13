import sys
import os
from fastapi.testclient import TestClient

# Add backend root directory to sys.path so imports resolve cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def run_admin_router_test():
    print("=" * 80)
    print("        AKSHARAI ADMIN CONTENT STUDIO REST API INTEGRATION TEST")
    print("=" * 80)

    client = TestClient(app)

    # 1. GET /api/admin/summary
    print("\n[TEST 1] GET /api/admin/summary")
    res1 = client.get("/api/admin/summary")
    print(f"  -> HTTP {res1.status_code}")
    print(f"  -> Summary stats: languages = {res1.json().get('languages_count')}, modules = {res1.json().get('modules_count')}, lessons = {res1.json().get('lessons_count')}")
    assert res1.status_code == 200, f"Expected 200, got {res1.status_code}"
    assert "languages_count" in res1.json(), "Missing languages_count key"

    # 2. GET /api/admin/modules
    print("\n[TEST 2] GET /api/admin/modules")
    res2 = client.get("/api/admin/modules")
    print(f"  -> HTTP {res2.status_code}")
    print(f"  -> Modules count = {len(res2.json())}")
    assert res2.status_code == 200, f"Expected 200, got {res2.status_code}"
    assert isinstance(res2.json(), list), "Expected list of modules"

    # 3. GET /api/admin/lessons
    print("\n[TEST 3] GET /api/admin/lessons")
    res3 = client.get("/api/admin/lessons")
    print(f"  -> HTTP {res3.status_code}")
    print(f"  -> Lessons count = {len(res3.json())}")
    assert res3.status_code == 200, f"Expected 200, got {res3.status_code}"
    assert isinstance(res3.json(), list), "Expected list of lessons"

    # 4. POST /api/admin/modules
    print("\n[TEST 4] POST /api/admin/modules (Create Admin Test Module)")
    mod_payload = {
        "curriculum_id": 2,  # English Curriculum
        "module_name": "Admin Test Literacy Module",
        "sequence_no": 99,
        "skill_type": "Reading & Pronunciation"
    }
    res4 = client.post("/api/admin/modules", json=mod_payload)
    print(f"  -> HTTP {res4.status_code}")
    print(f"  -> Response: {res4.json()}")
    assert res4.status_code == 200, f"Expected 200, got {res4.status_code}"
    created_mod_id = res4.json()["module_id"]

    # 5. POST /api/admin/lessons
    print(f"\n[TEST 5] POST /api/admin/lessons (Create Lesson in Module {created_mod_id})")
    les_payload = {
        "module_id": created_mod_id,
        "title": "Admin Test Practice Lesson",
        "content_type": "Voice Practice",
        "content_url": "/audio/en/admin_test.mp3",
        "target_text": "This is a custom admin test practice sentence",
        "phonetic_script": "[\"cus-tom\", \"ad-min\"]",
        "difficulty_level": "FOUNDATIONAL"
    }
    res5 = client.post("/api/admin/lessons", json=les_payload)
    print(f"  -> HTTP {res5.status_code}")
    print(f"  -> Response: {res5.json()}")
    assert res5.status_code == 200, f"Expected 200, got {res5.status_code}"
    created_les_id = res5.json()["lesson_id"]

    # 6. DELETE /api/admin/lessons/{lesson_id}
    print(f"\n[TEST 6] DELETE /api/admin/lessons/{created_les_id}")
    res6 = client.delete(f"/api/admin/lessons/{created_les_id}")
    print(f"  -> HTTP {res6.status_code}")
    print(f"  -> Response: {res6.json()}")
    assert res6.status_code == 200, f"Expected 200, got {res6.status_code}"

    # 7. DELETE /api/admin/modules/{module_id}
    print(f"\n[TEST 7] DELETE /api/admin/modules/{created_mod_id}")
    res7 = client.delete(f"/api/admin/modules/{created_mod_id}")
    print(f"  -> HTTP {res7.status_code}")
    print(f"  -> Response: {res7.json()}")
    assert res7.status_code == 200, f"Expected 200, got {res7.status_code}"

    print("\n" + "=" * 80)
    print("        ALL 7 ADMIN REST API ENDPOINT TESTS PASSED SUCCESSFULLY (100%)")
    print("=" * 80)


if __name__ == "__main__":
    run_admin_router_test()
