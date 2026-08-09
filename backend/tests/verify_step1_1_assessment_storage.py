import requests
import sqlite3
import sys

BASE_URL = "http://127.0.0.1:8000/api/assessment/submit"
DB_PATH = "backend/aksharai_dev.db"

def verify_step1_1_enrichment():
    print("=" * 100)
    print("      VERIFYING STEP 1.1 — ENRICH ASSESSMENT RESULT STORAGE IN DATABASE")
    print("=" * 100)

    # 1. Post a sample diagnostic test submission
    payload = {
        "lang": "en",
        "answers": [
            {"stage": 1, "skill_type": "READ", "selected_option_id": "a"},
            {"stage": 2, "skill_type": "WRITE", "written_text": "library"},
            {"stage": 3, "skill_type": "SPEAK", "spoken_text": "Language unlocks knowledge, wisdom, and human expression"},
            {"stage": 4, "skill_type": "READ", "selected_option_id": "a"},
            {"stage": 5, "skill_type": "WRITE", "written_text": "written"},
            {"stage": 6, "skill_type": "SPEAK", "spoken_text": "Although the journey was challenging"},
            {"stage": 7, "skill_type": "READ", "selected_option_id": "a"},
            {"stage": 8, "skill_type": "WRITE", "written_text": "eloquence"},
            {"stage": 9, "skill_type": "SPEAK", "spoken_text": "Mastery over language transforms thought"}
        ]
    }

    res = requests.post(BASE_URL, json=payload)
    if res.status_code != 200:
        print(f"[FAILED] Submission API status: {res.status_code}")
        return False

    data = res.json()
    validated_details = data.get("validated_details", [])
    print(f"API Submission Status: {res.status_code} | Total Score: {data.get('total_score')}%")
    print(f"Validated Details returned: {len(validated_details)} question items")

    # 2. Inspect SQLite Database directly
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query Assessment table
    assessments = cursor.execute("SELECT assessment_id, assessment_type, title, total_marks FROM assessment").fetchall()
    print(f"\n[DB PERSISTENCE] Assessment Table Rows ({len(assessments)}):")
    for a in assessments:
        print(f"  - Assessment ID: {a[0]} | Type: {a[1]} | Title: {a[2]} | Total Marks: {a[3]}")

    # Query AssessmentQuestion table
    questions = cursor.execute("SELECT question_id, assessment_id, question_type, question_text, correct_answer FROM assessment_question").fetchall()
    print(f"\n[DB PERSISTENCE] AssessmentQuestion Table Rows ({len(questions)}):")
    for q in questions:
        print(f"  - Question ID: {q[0]} | Assessment ID: {q[1]} | Type: {q[2]}")

    # Query AssessmentResult table
    results = cursor.execute("SELECT result_id, learner_id, assessment_id, question_id, score, is_correct, user_answer, submitted_at FROM assessment_result ORDER BY result_id DESC LIMIT 9").fetchall()
    print(f"\n[DB PERSISTENCE] AssessmentResult Table Rows (Recent 9):")
    for r in results:
        status_str = "[CORRECT]" if r[5] else "[INCORRECT]"
        clean_user_ans = (r[6] or "").encode("ascii", "ignore").decode("ascii")
        print(f"  - Result ID: {r[0]} | Learner ID: {r[1]} | Assessment ID: {r[2]} | Question ID: {r[3]} | Score: {r[4]} | {status_str} | User Ans: {clean_user_ans}")

    conn.close()

    assert len(assessments) >= 1, "Failed: No Assessment record found in DB!"
    assert len(questions) >= 9, "Failed: AssessmentQuestion rows were not written!"
    assert len(results) >= 9, "Failed: AssessmentResult rows were not written!"

    # Verify every result has a valid question_id from AssessmentQuestion
    valid_q_ids = set([q[0] for q in questions])
    for r in results:
        assert r[3] in valid_q_ids, f"Failed: AssessmentResult question_id {r[3]} not mapped to AssessmentQuestion!"

    print("\n" + "=" * 100)
    print("      SUCCESS: STEP 1.1 ENRICHED ASSESSMENT STORAGE VERIFIED 100% IN DATABASE")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_step1_1_enrichment()
    if not ok:
        sys.exit(1)
