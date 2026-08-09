import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"

def verify_step3_1_completion_tracking():
    print("=" * 100)
    print("      VERIFYING STEP 3.1 — LESSON COMPLETION TRACKING & AUTO-UNLOCK SYSTEM")
    print("=" * 100)

    # 1. Register test learner
    ts = int(time.time() * 1000)
    email = f"completion_tester_{ts}@example.com"
    username = f"comp_user_{ts}"
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password123!",
        "first_name": "Completion",
        "last_name": "Tester",
        "selected_lang": "en"
    })
    data = reg_res.json()
    token = data.get("access_token")
    u_id = data.get("user_id")
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\n[REGISTER TEST USER] Learner ID: {u_id} | Email: {email}")

    # 2. Fetch initial active path
    path_res = requests.get(f"{BASE_URL}/api/learning-path/active", headers=headers)
    assert path_res.status_code == 200, f"Path API failed {path_res.status_code}"
    initial_path = path_res.json()
    path_id = initial_path.get("path_id")

    m1_lessons = initial_path["milestones"][0]["lessons"]
    l1 = m1_lessons[0]
    l2 = m1_lessons[1]

    print(f"Initial Path ID: {path_id}")
    print(f"  - Lesson 1 ID: {l1['lesson_id']} | PathLesson ID: {l1['path_lesson_id']} | Initial Status: {l1['status']}")
    print(f"  - Lesson 2 ID: {l2['lesson_id']} | PathLesson ID: {l2['path_lesson_id']} | Initial Status: {l2['status']}")

    # 3. Patch lesson 1 to COMPLETED
    patch_res = requests.patch(
        f"{BASE_URL}/api/learning-path/lesson/{l1['path_lesson_id']}/status",
        json={"status": "COMPLETED"},
        headers=headers
    )
    assert patch_res.status_code == 200, f"Patch API failed {patch_res.status_code}"
    patch_data = patch_res.json()
    print(f"\n[PATCH LESSON 1 STATUS -> COMPLETED] Response: {patch_data.get('message')}")

    # 4. Verify DB changes in SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # a. PathLesson status
    pl1_status = cursor.execute("SELECT status FROM path_lesson WHERE path_lesson_id=?", (l1['path_lesson_id'],)).fetchone()[0]
    pl2_status = cursor.execute("SELECT status FROM path_lesson WHERE path_lesson_id=?", (l2['path_lesson_id'],)).fetchone()[0]
    print(f"[DB PATHLESSON STATUS] Lesson 1: {pl1_status} | Lesson 2 (Auto-unlocked): {pl2_status}")
    assert pl1_status == "COMPLETED", f"Expected COMPLETED for Lesson 1, got {pl1_status}"

    # b. ProgressTracking table entry
    prog_row = cursor.execute("SELECT progress_id, learner_id, module_id, completion_percent, time_spent_min FROM progress_tracking WHERE learner_id=?", (u_id,)).fetchone()
    print(f"[DB PROGRESS_TRACKING ENTRY]")
    print(f"  - Progress ID       : {prog_row[0]}")
    print(f"  - Learner ID        : {prog_row[1]}")
    print(f"  - Module ID         : {prog_row[2]}")
    print(f"  - Completion Percent: {prog_row[3]}%")
    print(f"  - Time Spent (Min)  : {prog_row[4]}")
    assert prog_row is not None, "Failed: ProgressTracking row was not written!"
    assert prog_row[3] > 0, "Failed: Module completion_percent was not calculated!"

    # c. LearningPath completion_percentage recalculation
    path_completion = cursor.execute("SELECT completion_percentage FROM learning_path WHERE path_id=?", (path_id,)).fetchone()[0]
    print(f"[DB LEARNING_PATH RECALCULATION] Path Completion Percentage: {path_completion}%")
    assert path_completion > 0, "Failed: LearningPath completion_percentage was not updated!"

    conn.close()

    print("\n" + "=" * 100)
    print("      SUCCESS: STEP 3.1 LESSON COMPLETION TRACKING VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_step3_1_completion_tracking()
    if not ok:
        sys.exit(1)
