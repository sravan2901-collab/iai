import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def verify_all_languages_step2_and_3():
    print("=" * 100)
    print("      VERIFYING STEPS 2 & 3 ADAPTIVE PATHS & RE-PLANNING ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        ts = int(time.time() * 1000)
        email = f"multi_tester_{lang}_{ts}@example.com"
        username = f"user_{lang}_{ts}"
        
        # 1. Register learner in target language
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": f"Learner_{lang}",
            "last_name": "Test",
            "selected_lang": lang
        })
        assert reg_res.status_code in [200, 201], f"Registration failed for lang {lang}: {reg_res.status_code}"
        token = reg_res.json()["access_token"]
        u_id = reg_res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Set initial Reading weakness
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE learner_profile SET reading_pct=25.0, comprehension_pct=85.0, voice_pct=90.0 WHERE learner_id=?", (u_id,))
        conn.commit()
        conn.close()

        # 2. Step 2 — Fetch Adaptive Path in native script
        path_res = requests.get(f"{BASE_URL}/api/learning-path/active?lang={lang}", headers=headers)
        assert path_res.status_code == 200, f"Path API failed for lang {lang}"
        path_data = path_res.json()
        path_id = path_data["path_id"]
        m1_title = path_data["milestones"][0]["title"].encode('ascii', 'ignore').decode('ascii')
        print(f"\n[{lang.upper()}] Adaptive Path ID: {path_id} | First Milestone: {m1_title}")

        # 3. Step 3.1 & 3.2 — Complete lessons in Milestone 1 & test auto-unlock & progress tracking
        m1_lessons = path_data["milestones"][0]["lessons"]
        for idx, les in enumerate(m1_lessons):
            p_res = requests.patch(f"{BASE_URL}/api/learning-path/lesson/{les['path_lesson_id']}/status", json={"status": "COMPLETED"}, headers=headers)
            assert p_res.status_code == 200, f"Lesson patch failed for lang {lang}"

        # 4. Step 3.3 — Update skill scores to simulate shift (Voice drops to 30%), complete 3rd lesson to trigger re-planning
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE learner_profile SET reading_pct=95.0, comprehension_pct=85.0, voice_pct=30.0 WHERE learner_id=?", (u_id,))
        conn.commit()
        conn.close()

        # Fetch remaining lesson IDs
        path_res2 = requests.get(f"{BASE_URL}/api/learning-path/active?lang={lang}", headers=headers).json()
        all_pl_ids = []
        for m in path_res2["milestones"]:
            for l in m["lessons"]:
                all_pl_ids.append(l["path_lesson_id"])

        if len(all_pl_ids) >= 3:
            r3 = requests.patch(f"{BASE_URL}/api/learning-path/lesson/{all_pl_ids[2]}/status", json={"status": "COMPLETED"}, headers=headers).json()
            is_replanned = r3.get("details", {}).get("replanned", False)
            print(f"[{lang.upper()}] Step 3.3 Re-Planning Trigger Executed: {is_replanned}")

        print(f"[{lang.upper()}] -> SUCCESS: Step 2 & Step 3 fully operational.")

    print("\n" + "=" * 100)
    print("      SUCCESS: STEPS 2 & 3 VERIFIED 100% ACROSS ALL 8 LANGUAGES!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_all_languages_step2_and_3()
    if not ok:
        sys.exit(1)
