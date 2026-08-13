import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def verify_content_recommendations_all_languages():
    print("=" * 100)
    print("      VERIFYING CONTENT RECOMMENDATION ENGINES ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        ts = int(time.time() * 1000)
        email = f"cnt_tester_{lang}_{ts}@example.com"
        username = f"cnt_user_{lang}_{ts}"

        # 1. Register test user
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": f"Learner_{lang}",
            "last_name": "Cnt",
            "selected_lang": lang
        })
        assert reg_res.status_code in [200, 201], f"Registration failed for {lang}"
        token = reg_res.json()["access_token"]
        u_id = reg_res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Call GET /api/recommendations/recommended-content?lang={iso}
        res = requests.get(f"{BASE_URL}/api/recommendations/recommended-content?lang={lang}", headers=headers)
        assert res.status_code == 200, f"Content recommendation API failed for {lang}: {res.status_code}"
        data = res.json()

        print(f"\n[{lang.upper()}] Learner ID: {u_id} | Recommended Items: {len(data)}")
        for idx, item in enumerate(data, 1):
            print(f"  {idx}. Category: {item['category'].encode('ascii', 'ignore').decode('ascii')} | Title: {item['title'].encode('ascii', 'ignore').decode('ascii')} | Relevance: {item['relevance_score']}")

        assert len(data) == 3, f"Expected 3 recommended content items for {lang}"

    print("\n" + "=" * 100)
    print("      SUCCESS: CONTENT RECOMMENDATION ENGINES VERIFIED 100% FOR ALL 8 LANGUAGES!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_content_recommendations_all_languages()
    if not ok:
        sys.exit(1)
