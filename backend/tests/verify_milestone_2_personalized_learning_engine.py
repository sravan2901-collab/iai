import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"

def verify_milestone_2():
    print("=" * 100)
    print("      VERIFYING MILESTONE 2 — AI-BASED PERSONALIZED LEARNING ENGINE")
    print("=" * 100)

    # 1. Register test user
    ts = int(time.time() * 1000)
    email = f"m2_tester_{ts}@example.com"
    username = f"m2_user_{ts}"
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "username": username,
        "password": "Password123!",
        "first_name": "Milestone2",
        "last_name": "Tester",
        "selected_lang": "te"
    })
    assert reg_res.status_code in [200, 201], f"Registration failed {reg_res.status_code}"
    data = reg_res.json()
    token = data["access_token"]
    u_id = data["user_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n[TEST USER REGISTERED] ID: {u_id} | Language: Telugu (te)")

    # Set skill percentages with Reading weakness
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE learner_profile SET reading_pct=30.0, comprehension_pct=75.0, voice_pct=80.0 WHERE learner_id=?", (u_id,))
    conn.commit()
    conn.close()

    # 2. Test Step 2.1 — Adaptive Learning Recommendation Model
    rec_res = requests.get(f"{BASE_URL}/api/recommendations/adaptive-plan", headers=headers)
    assert rec_res.status_code == 200, f"Adaptive recommendation failed: {rec_res.status_code}"
    rec = rec_res.json()
    print(f"\n[STEP 2.1 — ADAPTIVE RECOMMENDATION MODEL]")
    print(f"  - Primary Focus Skill : {rec['primary_focus_skill']}")
    print(f"  - Confidence Score    : {rec['confidence_score']}")
    print(f"  - Recommended Modules : {len(rec['recommended_modules'])} modules prioritized")
    print(f"  - Engine Rationale    : {rec['rationale']}")
    assert rec['primary_focus_skill'] == "READING", f"Expected READING focus, got {rec['primary_focus_skill']}"

    # 3. Test Step 2.2 — Learner Proficiency Prediction Algorithm
    pred_res = requests.get(f"{BASE_URL}/api/recommendations/predict-proficiency", headers=headers)
    assert pred_res.status_code == 200, f"Proficiency prediction failed: {pred_res.status_code}"
    pred = pred_res.json()
    print(f"\n[STEP 2.2 — PROFICIENCY PREDICTION ALGORITHM]")
    print(f"  - Current Level       : {pred['current_level']}")
    print(f"  - Predicted Next Level: {pred['predicted_next_level']}")
    print(f"  - Estimated Days      : {pred['estimated_days_to_mastery']} days")
    print(f"  - Growth Rate         : {pred['accuracy_growth_rate']}% per week")

    # 4. Test Step 2.3 — Personalized Lesson Generation Workflow
    gen_res = requests.post(f"{BASE_URL}/api/recommendations/personalized-lessons", json={}, headers=headers)
    assert gen_res.status_code == 200, f"Personalized lesson generation failed: {gen_res.status_code}"
    gen = gen_res.json()
    print(f"\n[STEP 2.3 — PERSONALIZED LESSON GENERATION WORKFLOW]")
    print(f"  - Generated Lesson ID : {gen['lesson_id']}")
    print(f"  - Target Skill        : {gen['target_skill']}")
    print(f"  - Exercise Type       : {gen['exercise_type']}")
    print(f"  - Exercise Title      : {gen['title']}")

    # 5. Test Step 2.4 — Content Recommendation Engine
    cnt_res = requests.get(f"{BASE_URL}/api/recommendations/recommended-content", headers=headers)
    assert cnt_res.status_code == 200, f"Content recommendation failed: {cnt_res.status_code}"
    cnt = cnt_res.json()
    print(f"\n[STEP 2.4 — CONTENT RECOMMENDATION ENGINE]")
    print(f"  - Ranked Items Returned: {len(cnt)}")
    for item in cnt:
        print(f"    * Category: {item['category']} | Skill: {item['skill_type']} | Relevance: {item['relevance_score']}")

    # 6. Test Step 2.5 — Learning Path Management APIs
    lp_res = requests.get(f"{BASE_URL}/api/learning-path/active?lang=te", headers=headers)
    assert lp_res.status_code == 200, f"Learning path API failed: {lp_res.status_code}"
    lp = lp_res.json()
    print(f"\n[STEP 2.5 — LEARNING PATH MANAGEMENT APIs]")
    print(f"  - Active Path ID       : {lp['path_id']}")
    print(f"  - Path Title           : {lp['path_title'].encode('ascii', 'ignore').decode('ascii')}")
    print(f"  - Total Milestones     : {len(lp['milestones'])}")

    print("\n" + "=" * 100)
    print("      SUCCESS: MILESTONE 2 — PERSONALIZED LEARNING ENGINE VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_milestone_2()
    if not ok:
        sys.exit(1)
