import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def verify_adaptive_recommendations_all_languages():
    print("=" * 100)
    print("      VERIFYING ADAPTIVE LEARNING RECOMMENDATION MODELS ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        ts = int(time.time() * 1000)
        email = f"rec_tester_{lang}_{ts}@example.com"
        username = f"rec_user_{lang}_{ts}"

        # 1. Register test user
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": f"Tester_{lang}",
            "last_name": "Rec",
            "selected_lang": lang
        })
        assert reg_res.status_code in [200, 201], f"Registration failed for {lang}"
        token = reg_res.json()["access_token"]
        u_id = reg_res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Update learner profile with Reading weakness
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE learner_profile SET reading_pct=25.0, comprehension_pct=75.0, voice_pct=80.0 WHERE learner_id=?", (u_id,))
        conn.commit()
        conn.close()

        # 3. Call GET /api/recommendations/adaptive-plan?lang={iso}
        res = requests.get(f"{BASE_URL}/api/recommendations/adaptive-plan?lang={lang}", headers=headers)
        assert res.status_code == 200, f"Recommendation API failed for {lang}: {res.status_code}"
        data = res.json()

        print(f"\n[{lang.upper()}] Learner ID: {u_id}")
        print(f"  - Primary Focus Skill : {data['primary_focus_skill']}")
        print(f"  - Confidence Score    : {data['confidence_score']}")
        print(f"  - First Rec Module    : {data['recommended_modules'][0]['title'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"  - Native Rationale    : {data['rationale'].encode('ascii', 'ignore').decode('ascii')}")

        assert data['primary_focus_skill'] == "READING", f"Expected READING focus for {lang}, got {data['primary_focus_skill']}"
        assert len(data['recommended_modules']) == 3, f"Expected 3 recommended modules for {lang}"

    print("\n" + "=" * 100)
    print("      SUCCESS: ADAPTIVE LEARNING RECOMMENDATION MODELS VERIFIED 100% FOR ALL 8 LANGUAGES!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_adaptive_recommendations_all_languages()
    if not ok:
        sys.exit(1)
