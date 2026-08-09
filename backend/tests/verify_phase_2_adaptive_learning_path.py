import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"

def verify_phase_2_adaptive_path():
    print("=" * 100)
    print("      VERIFYING PHASE 2 — ADAPTIVE LEARNING PATH GENERATION ALGORITHM (STEPS 2.1, 2.2, 2.3)")
    print("=" * 100)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Verify DB Seeding (Step 2.3)
    curr_count = cursor.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
    mod_count = cursor.execute("SELECT COUNT(*) FROM module").fetchone()[0]
    les_count = cursor.execute("SELECT COUNT(*) FROM lesson").fetchone()[0]

    print("\n[STEP 2.3 DB SEEDING VERIFICATION]")
    print(f"  - Curriculum Table Count: {curr_count}")
    print(f"  - Module Table Count    : {mod_count}")
    print(f"  - Lesson Table Count    : {les_count}")

    assert curr_count >= 8, f"Expected at least 8 curricula in DB, got {curr_count}"
    assert mod_count >= 24, f"Expected at least 24 modules in DB, got {mod_count}"
    assert les_count >= 56, f"Expected at least 56 lessons in DB, got {les_count}"

    # Helper function to create registered learner with specific skill breakdown
    def setup_test_learner(prefix, r_pct, c_pct, v_pct, level="FOUNDATIONAL"):
        ts = int(time.time() * 1000)
        email = f"{prefix}_{ts}@example.com"
        username = f"{prefix}_{ts}"
        reg_payload = {
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": "Phase2",
            "last_name": "Tester",
            "selected_lang": "en"
        }
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json=reg_payload)
        data = reg_res.json()
        token = data.get("access_token")
        u_id = data.get("user_id")

        # Update skill percentages & literacy level directly in DB for testing rules
        cursor.execute(
            "UPDATE learner_profile SET reading_pct=?, comprehension_pct=?, voice_pct=?, literacy_level=? WHERE learner_id=?",
            (r_pct, c_pct, v_pct, level, u_id)
        )
        conn.commit()
        return token, u_id

    # 2. Rule 1 Test: Reading < 50% (Reading = 30.0%)
    print("\n[STEP 2.1 RULE 1 TEST — READING < 50%]")
    t1, id1 = setup_test_learner("rule1_reading", 30.0, 80.0, 90.0)
    res1 = requests.get(f"{BASE_URL}/api/learning-path/active", headers={"Authorization": f"Bearer {t1}"})
    assert res1.status_code == 200, f"Failed HTTP {res1.status_code}"
    p1 = res1.json()
    reason1 = p1.get("personalization_reason", "")
    print(f"  - Learner ID: {id1}")
    print(f"  - Reason    : {reason1.encode('ascii', 'ignore').decode('ascii')}")
    print(f"  - First Milestone: {p1['milestones'][0]['title']}")
    assert "Reading score" in reason1 and "phonics" in reason1, f"Unexpected reason: {reason1}"
    assert "Alphabets & Phonics" in p1['milestones'][0]['title'], "First milestone did not prioritize Reading & Phonics!"

    # 3. Rule 2 Test: Comprehension < 50% (Comprehension = 33.3%)
    print("\n[STEP 2.1 RULE 2 TEST — COMPREHENSION < 50%]")
    t2, id2 = setup_test_learner("rule2_comp", 85.0, 33.3, 90.0)
    res2 = requests.get(f"{BASE_URL}/api/learning-path/active", headers={"Authorization": f"Bearer {t2}"})
    assert res2.status_code == 200, f"Failed HTTP {res2.status_code}"
    p2 = res2.json()
    reason2 = p2.get("personalization_reason", "")
    print(f"  - Learner ID: {id2}")
    print(f"  - Reason    : {reason2.encode('ascii', 'ignore').decode('ascii')}")
    print(f"  - First Milestone: {p2['milestones'][0]['title']}")
    assert "Comprehension score" in reason2 and "ATM & Banking" in reason2, f"Unexpected reason: {reason2}"
    assert "ATM & Banking" in p2['milestones'][0]['title'], "First milestone did not prioritize ATM & Banking!"

    # 4. Rule 3 Test: Voice < 50% (Voice = 40.0%)
    print("\n[STEP 2.1 RULE 3 TEST — VOICE < 50%]")
    t3, id3 = setup_test_learner("rule3_voice", 85.0, 80.0, 40.0)
    res3 = requests.get(f"{BASE_URL}/api/learning-path/active", headers={"Authorization": f"Bearer {t3}"})
    assert res3.status_code == 200, f"Failed HTTP {res3.status_code}"
    p3 = res3.json()
    reason3 = p3.get("personalization_reason", "")
    print(f"  - Learner ID: {id3}")
    print(f"  - Reason    : {reason3.encode('ascii', 'ignore').decode('ascii')}")
    print(f"  - First Milestone: {p3['milestones'][0]['title']}")
    assert "Voice score" in reason3 and "Workplace Communication" in reason3, f"Unexpected reason: {reason3}"
    assert "Workplace Communication" in p3['milestones'][0]['title'], "First milestone did not prioritize Workplace Communication!"

    # 5. Rule 4 Test: All Skills >= 70% (Skipping foundational -> jumping to FUNCTIONAL)
    print("\n[STEP 2.1 RULE 4 TEST — ALL SKILLS >= 70%]")
    t4, id4 = setup_test_learner("rule4_strong", 100.0, 100.0, 100.0)
    res4 = requests.get(f"{BASE_URL}/api/learning-path/active", headers={"Authorization": f"Bearer {t4}"})
    assert res4.status_code == 200, f"Failed HTTP {res4.status_code}"
    p4 = res4.json()
    reason4 = p4.get("personalization_reason", "")
    print(f"  - Learner ID   : {id4}")
    print(f"  - Reason       : {reason4.encode('ascii', 'ignore').decode('ascii')}")
    print(f"  - Current Level: {p4.get('current_level')}")
    assert "All skill scores are" in reason4 and "skipped" in reason4, f"Unexpected reason: {reason4}"
    assert p4.get('current_level') == 'FUNCTIONAL', f"Expected FUNCTIONAL level, got {p4.get('current_level')}"

    # 6. Verify Unlock Logic (Rule 7: First 2 lessons UNLOCKED, rest LOCKED)
    all_lessons = []
    for m in p1['milestones']:
        all_lessons.extend(m['lessons'])

    unlocked_count = sum(1 for l in all_lessons if l['status'] == 'UNLOCKED')
    locked_count = sum(1 for l in all_lessons if l['status'] == 'LOCKED')
    print(f"\n[LESSON UNLOCK LOGIC TEST] Total Lessons: {len(all_lessons)} | Unlocked: {unlocked_count} | Locked: {locked_count}")
    assert unlocked_count == 2, f"Expected exactly 2 unlocked initial lessons, found {unlocked_count}"

    # 7. DB Persistence Integrity
    path_db_row = cursor.execute("SELECT path_id, learner_id, current_level FROM learning_path WHERE learner_id=?", (id1,)).fetchone()
    path_lessons_db_count = cursor.execute("SELECT COUNT(*) FROM path_lesson WHERE path_id=?", (path_db_row[0],)).fetchone()[0]
    print(f"\n[DB PERSISTENCE INTEGRITY] LearningPath ID: {path_db_row[0]} | Linked PathLesson rows in DB: {path_lessons_db_count}")
    assert path_lessons_db_count >= 7, f"Expected at least 7 PathLesson records in DB, found {path_lessons_db_count}"

    conn.close()

    print("\n" + "=" * 100)
    print("      SUCCESS: PHASE 2 ADAPTIVE LEARNING PATH ALGORITHM VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_phase_2_adaptive_path()
    if not ok:
        sys.exit(1)
