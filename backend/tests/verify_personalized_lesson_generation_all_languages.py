import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def verify_personalized_lessons_all_languages():
    print("=" * 100)
    print("      VERIFYING PERSONALIZED LESSON GENERATION WORKFLOWS ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        ts = int(time.time() * 1000)
        email = f"gen_tester_{lang}_{ts}@example.com"
        username = f"gen_user_{lang}_{ts}"

        # 1. Register test user
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": f"Learner_{lang}",
            "last_name": "Gen",
            "selected_lang": lang
        })
        assert reg_res.status_code in [200, 201], f"Registration failed for {lang}"
        token = reg_res.json()["access_token"]
        u_id = reg_res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Call POST /api/recommendations/personalized-lessons?lang={iso}
        res = requests.post(f"{BASE_URL}/api/recommendations/personalized-lessons?lang={lang}", json={}, headers=headers)
        assert res.status_code == 200, f"Personalized lesson generation failed for {lang}: {res.status_code}"
        data = res.json()

        print(f"\n[{lang.upper()}] Learner ID: {u_id}")
        print(f"  - Lesson ID       : {data['lesson_id']}")
        print(f"  - Target Skill    : {data['target_skill']}")
        print(f"  - Exercise Type   : {data['exercise_type']}")
        print(f"  - Title           : {data['title'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"  - Instructions    : {data['instructions'].encode('ascii', 'ignore').decode('ascii')}")

        assert data['language_code'] == lang, f"Expected lang {lang}, got {data['language_code']}"
        assert len(data['practice_content']) >= 1, f"Practice content empty for {lang}"

    print("\n" + "=" * 100)
    print("      SUCCESS: PERSONALIZED LESSON GENERATION WORKFLOWS VERIFIED 100% FOR ALL 8 LANGUAGES!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_personalized_lessons_all_languages()
    if not ok:
        sys.exit(1)
