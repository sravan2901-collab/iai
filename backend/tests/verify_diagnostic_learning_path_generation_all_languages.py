import requests
import sqlite3
import sys
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/aksharai_dev.db"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def verify_diagnostic_learning_path_generation_all_languages():
    print("=" * 100)
    print("      VERIFYING DIAGNOSTIC TEST LEARNING PATH GENERATION ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        ts = int(time.time() * 1000)
        email = f"diag_path_user_{lang}_{ts}@example.com"
        username = f"diag_user_{lang}_{ts}"

        # 1. Register test user
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "username": username,
            "password": "Password123!",
            "first_name": f"DiagnosticLearner_{lang}",
            "last_name": "PathTest",
            "selected_lang": lang
        })
        assert reg_res.status_code in [200, 201], f"Registration failed for {lang}"
        token = reg_res.json()["access_token"]
        u_id = reg_res.json()["user_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get diagnostic questions for language
        q_res = requests.get(f"{BASE_URL}/api/assessment/diagnostic-questions?lang={lang}", headers=headers)
        assert q_res.status_code == 200, f"Failed to get questions for {lang}"
        questions = q_res.json()
        if isinstance(questions, dict) and "questions" in questions:
            questions = questions["questions"]

        # 3. Submit diagnostic test answers
        answers = []
        for q in questions:
            st = q.get("stage", q.get("id", 1))
            sk = q.get("skill_type", "READ")
            if sk == "READ":
                opt_id = q["options"][0]["id"] if q.get("options") else "a"
                answers.append({"stage": st, "skill_type": sk, "selected_option_id": opt_id, "is_correct": True})
            elif sk == "WRITE":
                ans_str = q["accepted_answers"][0] if q.get("accepted_answers") else "test"
                answers.append({"stage": st, "skill_type": sk, "written_text": ans_str, "is_correct": True})
            else: # SPEAK
                target = q.get("target_text", "speech sample")
                answers.append({"stage": st, "skill_type": sk, "spoken_text": target, "is_correct": True})

        sub_res = requests.post(f"{BASE_URL}/api/assessment/submit", json={
            "lang": lang,
            "answers": answers
        }, headers=headers)

        assert sub_res.status_code == 200, f"Submission failed for {lang}: {sub_res.status_code} - {sub_res.text}"
        sub_data = sub_res.json()

        print(f"\n[{lang.upper()}] Learner ID: {u_id}")
        print(f"  - Total Score           : {sub_data['total_score']} / 100")
        print(f"  - Proficiency Level     : {sub_data['proficiency_level']}")
        print(f"  - Generated Path Title  : {sub_data['learning_path']['path_title'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"  - Personalization Reason: {sub_data['learning_path']['personalization_reason'].encode('ascii', 'ignore').decode('ascii')}")
        print(f"  - Generated Milestones  : {len(sub_data['learning_path']['milestones'])}")

        assert sub_data["learning_path"] is not None, f"Learning path missing for {lang}"
        assert len(sub_data["learning_path"]["milestones"]) >= 1, f"No milestones generated for {lang}"

        # 4. Verify DB-persisted active learning path
        act_res = requests.get(f"{BASE_URL}/api/learning-path/active?lang={lang}", headers=headers)
        assert act_res.status_code == 200, f"Failed to get active learning path for {lang}"
        act_data = act_res.json()
        assert act_data["path_id"] is not None, f"DB active path missing for {lang}"

    print("\n" + "=" * 100)
    print("      SUCCESS: DIAGNOSTIC TEST LEARNING PATH GENERATION VERIFIED 100% FOR ALL 8 LANGUAGES!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_diagnostic_learning_path_generation_all_languages()
    if not ok:
        sys.exit(1)
