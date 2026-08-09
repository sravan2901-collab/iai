import requests
import sqlite3
import sys

BASE_URL = "http://127.0.0.1:8000/api/assessment/submit"
DB_PATH = "backend/aksharai_dev.db"

def verify_step1_2_percentages():
    print("=" * 100)
    print("      VERIFYING STEP 1.2 — LEARNER PROFILE SKILL BREAKDOWN PERCENTAGES")
    print("=" * 100)

    # 1. Submit diagnostic assessment (Reading: 33/33 -> 100%, Writing: 22/33 -> 66.7%, Voice: 34/34 -> 100%)
    payload = {
        "lang": "en",
        "answers": [
            {"stage": 1, "skill_type": "READ", "selected_option_id": "a"},  # Read 1 OK
            {"stage": 2, "skill_type": "WRITE", "written_text": "library"}, # Write 1 OK
            {"stage": 3, "skill_type": "SPEAK", "spoken_text": "Language unlocks knowledge, wisdom, and human expression"}, # Speak 1 OK
            {"stage": 4, "skill_type": "READ", "selected_option_id": "a"},  # Read 2 OK
            {"stage": 5, "skill_type": "WRITE", "written_text": "written"}, # Write 2 OK
            {"stage": 6, "skill_type": "SPEAK", "spoken_text": "Although the journey was challenging, continuous practice brought clarity and confidence"}, # Speak 2 OK
            {"stage": 7, "skill_type": "READ", "selected_option_id": "a"},  # Read 3 OK
            {"stage": 8, "skill_type": "WRITE", "written_text": "WRONG_ANSWER"}, # Write 3 Wrong
            {"stage": 9, "skill_type": "SPEAK", "spoken_text": "Mastery over language transforms thought into eloquent communication and lifelong empowerment"} # Speak 3 OK
        ]
    }

    res = requests.post(BASE_URL, json=payload)
    if res.status_code != 200:
        print(f"[FAILED] Submission API status: {res.status_code}")
        return False

    data = res.json()
    print(f"API Total Score: {data.get('total_score')}% | Level: {data.get('proficiency_level')}")

    # 2. Inspect LearnerProfile directly in SQLite DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cols = [col[1] for col in cursor.execute("PRAGMA table_info(learner_profile)").fetchall()]
    print(f"LearnerProfile Table Columns: {cols}")

    profile_row = cursor.execute("SELECT profile_id, learner_id, literacy_level, reading_pct, comprehension_pct, voice_pct FROM learner_profile ORDER BY profile_id DESC LIMIT 1").fetchone()
    conn.close()

    assert profile_row is not None, "Failed: LearnerProfile row not found!"

    p_id, l_id, level, r_pct, c_pct, v_pct = profile_row
    print("\n[DB PERSISTENCE] LearnerProfile Granular Skill Breakdown Row:")
    print(f"  - Profile ID        : {p_id}")
    print(f"  - Learner ID        : {l_id}")
    print(f"  - Literacy Level    : {level}")
    print(f"  - Reading Pct       : {r_pct}%")
    print(f"  - Comprehension Pct : {c_pct}%")
    print(f"  - Voice Pct         : {v_pct}%")

    assert "reading_pct" in cols, "Failed: reading_pct column missing from learner_profile schema!"
    assert "comprehension_pct" in cols, "Failed: comprehension_pct column missing from learner_profile schema!"
    assert "voice_pct" in cols, "Failed: voice_pct column missing from learner_profile schema!"

    assert r_pct == 100.0, f"Expected reading_pct 100.0, got {r_pct}"
    assert c_pct == 66.7, f"Expected comprehension_pct 66.7, got {c_pct}"
    assert v_pct == 100.0, f"Expected voice_pct 100.0, got {v_pct}"

    print("\n" + "=" * 100)
    print("      SUCCESS: STEP 1.2 LEARNER PROFILE SKILL PERCENTAGES VERIFIED 100% IN DB")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_step1_2_percentages()
    if not ok:
        sys.exit(1)
