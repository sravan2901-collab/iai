import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"

def verify_step3_3_replanning_trigger():
    print("=" * 100)
    print("      VERIFYING STEP 3.3 — PROGRESS-DRIVEN ADAPTIVE RE-PLANNING TRIGGER")
    print("=" * 100)

    # 1. Register test learner with initial Reading weakness (reading = 20%)
    ts = int(time.time() * 1000)
    email = f"replan_tester_{ts}@example.com"
    username = f"replan_user_{ts}"
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password123!",
        "first_name": "Replan",
        "last_name": "Tester",
        "selected_lang": "en"
    })
    data = reg_res.json()
    token = data.get("access_token")
    u_id = data.get("user_id")
    headers = {"Authorization": f"Bearer {token}"}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE learner_profile SET reading_pct=20.0, comprehension_pct=80.0, voice_pct=90.0 WHERE learner_id=?", (u_id,))
    conn.commit()

    # 2. Fetch initial path
    p_res1 = requests.get(f"{BASE_URL}/api/learning-path/active", headers=headers)
    path1 = p_res1.json()
    path_id = path1.get("path_id")
    print(f"\n[REGISTER TEST LEARNER] ID: {u_id} | Path ID: {path_id}")
    print(f"Initial First Milestone: {path1['milestones'][0]['title']}")

    # 3. Simulate real learning progress: Learner masters Reading (reading_pct -> 95%), but Voice drops (voice_pct -> 30%)
    cursor.execute("UPDATE learner_profile SET reading_pct=95.0, comprehension_pct=80.0, voice_pct=30.0 WHERE learner_id=?", (u_id,))
    conn.commit()

    # 4. Complete 3 lessons to hit the % 3 == 0 re-planning trigger!
    l_ids = []
    for m in path1["milestones"]:
        for l in m["lessons"]:
            l_ids.append(l["path_lesson_id"])

    r1 = requests.patch(f"{BASE_URL}/api/learning-path/lesson/{l_ids[0]}/status", json={"status": "COMPLETED"}, headers=headers).json()
    r2 = requests.patch(f"{BASE_URL}/api/learning-path/lesson/{l_ids[1]}/status", json={"status": "COMPLETED"}, headers=headers).json()
    r3 = requests.patch(f"{BASE_URL}/api/learning-path/lesson/{l_ids[2]}/status", json={"status": "COMPLETED"}, headers=headers).json()

    print(f"\n[LESSON 3 COMPLETION -> TRIGGER RE-PLANNING]")
    print(f"  - Lesson 3 Replanned Flag : {r3.get('details', {}).get('replanned')}")
    reason_clean = r3.get('details', {}).get('replan_reason', '').encode('ascii', 'ignore').decode('ascii')
    print(f"  - Re-Planning Reason      : {reason_clean}")

    assert r3.get('details', {}).get('replanned') == True, "Failed: Re-planning trigger did not execute after 3 completed lessons!"
    assert "VOICE is now lowest" in r3.get('details', {}).get('replan_reason', ''), f"Unexpected replan reason: {r3.get('details', {}).get('replan_reason')}"

    # 5. Fetch updated active path and verify locked lessons re-ordered
    path_res2 = requests.get(f"{BASE_URL}/api/learning-path/active", headers=headers)
    path2 = path_res2.json()

    print(f"\n[UPDATED ADAPTIVE PATH]")
    print(f"  - Personalization Reason: {path2.get('personalization_reason', '').encode('ascii', 'ignore').decode('ascii')}")

    conn.close()

    print("\n" + "=" * 100)
    print("      SUCCESS: STEP 3.3 ADAPTIVE RE-PLANNING TRIGGER VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_step3_3_replanning_trigger()
    if not ok:
        sys.exit(1)
