import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"

def verify_step1_3_language_preference():
    print("=" * 100)
    print("      VERIFYING STEP 1.3 — LEARNER LANGUAGE PREFERENCE TRACKING & CONTENT FILTERING")
    print("=" * 100)

    # 1. Verify 8 languages seeded in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    langs_in_db = cursor.execute("SELECT lang_id, iso_code, lang_name FROM language").fetchall()
    print(f"\n[DB SEEDING] Language Table Rows ({len(langs_in_db)}):")
    for l in langs_in_db:
        clean_name = l[2].encode("ascii", "ignore").decode("ascii")
        print(f"  - Lang ID: {l[0]} | ISO Code: {l[1]} | Name: {clean_name}")

    assert len(langs_in_db) >= 8, f"Expected 8 seeded languages in DB, found {len(langs_in_db)}"
    lang_map = {l[1]: l[0] for l in langs_in_db}

    # 2. Register learner in Telugu ('te')
    ts = int(time.time() * 1000)
    unique_email = f"telugu_learner_{ts}@example.com"
    unique_username = f"telugu_user_{ts}"

    reg_payload = {
        "email": unique_email,
        "username": unique_username,
        "password": "Password123!",
        "first_name": "Telugu",
        "last_name": "Learner",
        "selected_lang": "te"
    }

    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json=reg_payload)
    if reg_res.status_code != 200:
        print(f"[FAILED] Registration failed with status: {reg_res.status_code} | Details: {reg_res.text}")
        conn.close()
        return False

    reg_data = reg_res.json()
    token = reg_data.get("access_token")
    user_id = reg_data.get("user_id")

    # Verify learner current_lang_id in DB matches Telugu lang_id
    learner_lang_id = cursor.execute("SELECT current_lang_id FROM learner WHERE learner_id = ?", (user_id,)).fetchone()[0]
    expected_te_id = lang_map.get("te")
    print(f"\n[REGISTRATION TEST] Learner ID {user_id} current_lang_id: {learner_lang_id} (Expected Telugu: {expected_te_id})")
    assert learner_lang_id == expected_te_id, f"Learner current_lang_id was not set to Telugu lang_id {expected_te_id}!"

    # 3. Assessment Submission in Hindi ('hi') updates current_lang_id
    sub_payload = {
        "lang": "hi",
        "answers": [
            {"stage": 1, "skill_type": "READ", "selected_option_id": "a"},
            {"stage": 2, "skill_type": "WRITE", "written_text": "पुस्तकालय"},
            {"stage": 3, "skill_type": "SPEAK", "spoken_text": "भाषा ज्ञान का द्वार खोलती है"}
        ]
    }
    sub_headers = {"Authorization": f"Bearer {token}"}
    sub_res = requests.post(f"{BASE_URL}/api/assessment/submit", json=sub_payload, headers=sub_headers)
    assert sub_res.status_code == 200, f"Assessment submit failed with {sub_res.status_code}"

    # Verify current_lang_id updated to Hindi lang_id
    updated_lang_id = cursor.execute("SELECT current_lang_id FROM learner WHERE learner_id = ?", (user_id,)).fetchone()[0]
    expected_hi_id = lang_map.get("hi")
    print(f"[ASSESSMENT TEST] Learner ID {user_id} updated current_lang_id: {updated_lang_id} (Expected Hindi: {expected_hi_id})")
    assert updated_lang_id == expected_hi_id, f"Learner current_lang_id was not updated to Hindi lang_id {expected_hi_id}!"

    # 4. Learning Path Generator automatically returns Hindi path based on stored current_lang_id
    path_res = requests.get(f"{BASE_URL}/api/learning-path/active", headers=sub_headers)
    assert path_res.status_code == 200, f"Learning path API failed: {path_res.status_code}"
    path_data = path_res.json()
    print(f"\n[LEARNING PATH GENERATOR TEST] Target Language returned: {path_data.get('target_lang')}")
    assert path_data.get("target_lang") == "hi", f"Expected target_lang 'hi', got '{path_data.get('target_lang')}'!"

    conn.close()

    print("\n" + "=" * 100)
    print("      SUCCESS: STEP 1.3 LEARNER LANGUAGE PREFERENCE TRACKING VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_step1_3_language_preference()
    if not ok:
        sys.exit(1)
