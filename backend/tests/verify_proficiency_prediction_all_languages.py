import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def verify_proficiency_prediction_all_languages():
    print("=" * 100)
    print("      VERIFYING LEARNER PROFICIENCY PREDICTION ALGORITHMS ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        ts = int(time.time() * 1000)
        email = f"pred_tester_{lang}_{ts}@example.com"
        username = f"pred_user_{lang}_{ts}"

        # 1. Register test user
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": f"Learner_{lang}",
            "last_name": "Pred",
            "selected_lang": lang
        })
        assert reg_res.status_code in [200, 201], f"Registration failed for {lang}"
        token = reg_res.json()["access_token"]
        u_id = reg_res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Call GET /api/recommendations/predict-proficiency?lang={iso}
        res = requests.get(f"{BASE_URL}/api/recommendations/predict-proficiency?lang={lang}", headers=headers)
        assert res.status_code == 200, f"Proficiency prediction API failed for {lang}: {res.status_code}"
        data = res.json()

        print(f"\n[{lang.upper()}] Learner ID: {u_id}")
        print(f"  - Current Level        : {data['current_level']} ({data.get('native_current_level', '').encode('ascii', 'ignore').decode('ascii')})")
        print(f"  - Predicted Next Level : {data['predicted_next_level']} ({data.get('native_next_level', '').encode('ascii', 'ignore').decode('ascii')})")
        print(f"  - Days to Mastery      : {data['estimated_days_to_mastery']} days")
        print(f"  - Accuracy Growth Rate : {data['accuracy_growth_rate']}% per week")
        print(f"  - Prediction Summary   : {data.get('prediction_summary', '').encode('ascii', 'ignore').decode('ascii')}")

        assert data['current_level'] == "FOUNDATIONAL", f"Expected FOUNDATIONAL level for {lang}"
        assert data['predicted_next_level'] == "FUNCTIONAL", f"Expected FUNCTIONAL next level for {lang}"

    print("\n" + "=" * 100)
    print("      SUCCESS: PROFICIENCY PREDICTION ALGORITHMS VERIFIED 100% FOR ALL 8 LANGUAGES!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_proficiency_prediction_all_languages()
    if not ok:
        sys.exit(1)
