import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"

def verify_step3_2_milestone_logic():
    print("=" * 100)
    print("      VERIFYING STEP 3.2 — MILESTONE COMPLETION & UNLOCK LOGIC")
    print("=" * 100)

    # 1. Register test user
    ts = int(time.time() * 1000)
    email = f"milestone_tester_{ts}@example.com"
    username = f"ms_user_{ts}"
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password123!",
        "first_name": "Milestone",
        "last_name": "Tester",
        "selected_lang": "en"
    })
    data = reg_res.json()
    token = data.get("access_token")
    u_id = data.get("user_id")
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\n[REGISTER TEST USER] Learner ID: {u_id}")

    # 2. Fetch initial active path
    path_res = requests.get(f"{BASE_URL}/api/learning-path/active", headers=headers)
    assert path_res.status_code == 200, f"Path API failed {path_res.status_code}"
    initial_path = path_res.json()
    path_id = initial_path.get("path_id")

    m1_lessons = initial_path["milestones"][0]["lessons"]
    m2_lessons = initial_path["milestones"][1]["lessons"]

    print(f"\nInitial Path ID: {path_id} | Current Level: {initial_path.get('current_level')}")
    print(f"Milestone 1 lessons count: {len(m1_lessons)}")
    print(f"Milestone 2 first lesson initial status: {m2_lessons[0]['status']}")

    # 3. Complete ALL lessons in Milestone 1
    for idx, les in enumerate(m1_lessons):
        patch_res = requests.patch(
            f"{BASE_URL}/api/learning-path/lesson/{les['path_lesson_id']}/status",
            json={"status": "COMPLETED"},
            headers=headers
        )
        assert patch_res.status_code == 200, f"Failed completing lesson {idx+1}"
        p_data = patch_res.json()
        print(f"  - Completed Lesson {idx+1} (PathLesson {les['path_lesson_id']}) | Milestone Completed: {p_data.get('details', {}).get('milestone_completed')}")

    # 4. Verify DB changes in SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # a. Verify ProgressTracking for Module 1 is 100% completed
    m1_module_id = m1_lessons[0]['lesson_id']
    m1_prog = cursor.execute("SELECT completion_percent FROM progress_tracking WHERE learner_id=? AND module_id=1", (u_id,)).fetchone()
    print(f"\n[DB MILESTONE 1 PROGRESS TRACKING] Completion Percent: {m1_prog[0]}%")
    assert m1_prog[0] == 100.0, f"Expected 100.0% completion for Milestone 1, got {m1_prog[0]}"

    # b. Verify next milestone's lessons (Milestone 2) are automatically UNLOCKED
    m2_pl_status = cursor.execute("SELECT status FROM path_lesson WHERE path_lesson_id=?", (m2_lessons[0]['path_lesson_id'],)).fetchone()[0]
    print(f"[DB NEXT MILESTONE UNLOCK] Milestone 2 First Lesson Status: {m2_pl_status}")
    assert m2_pl_status == "UNLOCKED", f"Expected UNLOCKED for Milestone 2 first lesson, got {m2_pl_status}"

    # 5. Complete remaining lessons in Milestone 2 & 3 to test proficiency level promotion
    path_res2 = requests.get(f"{BASE_URL}/api/learning-path/active", headers=headers)
    updated_path = path_res2.json()

    all_remaining_pl_ids = []
    for m in updated_path["milestones"][1:]:
        for l in m["lessons"]:
            all_remaining_pl_ids.append(l["path_lesson_id"])

    for pl_id in all_remaining_pl_ids:
        requests.patch(
            f"{BASE_URL}/api/learning-path/lesson/{pl_id}/status",
            json={"status": "COMPLETED"},
            headers=headers
        )

    # Verify level promotion in DB (FOUNDATIONAL -> FUNCTIONAL)
    promoted_level = cursor.execute("SELECT current_level FROM learning_path WHERE path_id=?", (path_id,)).fetchone()[0]
    profile_level = cursor.execute("SELECT literacy_level FROM learner_profile WHERE learner_id=?", (u_id,)).fetchone()[0]

    print(f"\n[LEVEL PROMOTION TEST] LearningPath Level: {promoted_level} | LearnerProfile Level: {profile_level}")
    assert promoted_level in ["FUNCTIONAL", "PROFICIENT"], f"Expected level promotion, got {promoted_level}"
    assert profile_level in ["FUNCTIONAL", "PROFICIENT"], f"Expected profile level promotion, got {profile_level}"

    conn.close()

    print("\n" + "=" * 100)
    print("      SUCCESS: STEP 3.2 MILESTONE COMPLETION & UNLOCK LOGIC VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_step3_2_milestone_logic()
    if not ok:
        sys.exit(1)
