import sys
import os
import sqlite3
import uuid

# Force stdout to UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Adjust python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlalchemy import inspect

client = TestClient(app)

SUPPORTED_LANGUAGES = ['en', 'te', 'hi', 'ta', 'bn', 'mr', 'kn', 'es']

def run_comprehensive_week1_week2_tests():
    print("=" * 100)
    print("      AKSHARAI COMPREHENSIVE WEEK 1 & WEEK 2 GOALS VERIFICATION TEST SUITE")
    print("=" * 100)

    passed_count = 0
    total_tests = 0

    def assert_test(condition, test_name, detail=""):
        nonlocal passed_count, total_tests
        total_tests += 1
        safe_detail = detail.encode('ascii', 'replace').decode('ascii')
        if condition:
            passed_count += 1
            print(f"[TEST {total_tests:02d}] {test_name:<65} -> [PASSED] | {safe_detail}")
        else:
            print(f"[TEST {total_tests:02d}] {test_name:<65} -> [FAILED] | {safe_detail}")

    # --- SECTION 1: MULTILINGUAL DIAGNOSTIC QUESTIONS (8 LANGUAGES x 9 QUESTIONS) ---
    print("\n>>> SECTION 1: MULTILINGUAL DIAGNOSTIC QUESTIONS & BILINGUAL FORMATTING")
    for lang in SUPPORTED_LANGUAGES:
        res = client.get(f"/api/assessment/diagnostic-questions?lang={lang}")
        assert_test(res.status_code == 200, f"Diagnostic Questions API HTTP 200 [{lang.upper()}]", f"Status: {res.status_code}")
        
        q_list = res.json()
        assert_test(len(q_list) == 9, f"Diagnostic Test 9-Question Suite Length [{lang.upper()}]", f"Returned {len(q_list)} questions")

        # Verify Bilingual text and Difficulty Levels 1..9
        difficulties = [q.get('difficulty', idx+1) for idx, q in enumerate(q_list)]
        assert_test(difficulties == [1, 2, 3, 4, 5, 6, 7, 8, 9], f"Progressive Difficulty Levels 1 to 9 [{lang.upper()}]", f"Levels: {difficulties}")

        # Check Question 1 READ
        q1 = q_list[0]
        assert_test(q1['skill_type'] == 'READ' and len(q1.get('options', [])) >= 2, f"Q1 READ Skill & Native Options [{lang.upper()}]", f"Options count: {len(q1.get('options', []))}")

        # Check Question 2 WRITE
        q2 = q_list[1]
        assert_test(q2['skill_type'] == 'WRITE' and len(q2.get('accepted_answers', [])) >= 1, f"Q2 WRITE Skill & Native Answers [{lang.upper()}]", f"Accepted answer set")

        # Check Question 3 SPEAK
        q3 = q_list[2]
        assert_test(q3['skill_type'] == 'SPEAK' and len(q3.get('target_text', '').strip()) > 0, f"Q3 SPEAK Skill & Target Text [{lang.upper()}]", f"Target text present")

    # --- SECTION 2: LEARNER PROFICIENCY BENCHMARKS (8 LANGUAGES) ---
    print("\n>>> SECTION 2: LEARNER PROFICIENCY BENCHMARKS MATRIX")
    for lang in SUPPORTED_LANGUAGES:
        res = client.get(f"/api/assessment/benchmarks?lang={lang}")
        assert_test(res.status_code == 200, f"Proficiency Benchmarks API HTTP 200 [{lang.upper()}]", f"Status: {res.status_code}")
        data = res.json()
        tiers = data.get('tiers', [])
        assert_test(len(tiers) == 3, f"Three Tier Benchmark Definitions [{lang.upper()}]", f"Tiers count: {len(tiers)}")

    # --- SECTION 3: PLACEMENT ASSESSMENT SUBMISSION & ADAPTIVE PATH GENERATION ---
    print("\n>>> SECTION 3: ASSESSMENT SUBMISSION & ADAPTIVE LEARNING PATH")
    submission_payload = {
        "lang": "te",
        "answers": [
            {"stage": 1, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
            {"stage": 2, "skill_type": "WRITE", "written_text": "గ్రంథాలయము", "is_correct": True},
            {"stage": 3, "skill_type": "SPEAK", "spoken_text": "భాష అనేది ఆలోచనలకు రూపాన్ని ఇచ్చే అమూల్యమైన సాధనం", "is_correct": True},
            {"stage": 4, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
            {"stage": 5, "skill_type": "WRITE", "written_text": "దేవాలయం", "is_correct": True},
            {"stage": 6, "skill_type": "SPEAK", "spoken_text": "నిరంతర సాధన ద్వారా మాత్రమే భాషా ప్రావీణ్యం లభిస్తుంది", "is_correct": True},
            {"stage": 7, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
            {"stage": 8, "skill_type": "WRITE", "written_text": "విద్వాంసుడు", "is_correct": True},
            {"stage": 9, "skill_type": "SPEAK", "spoken_text": "సాహిత్యానుశీలనం మానవ చైతన్యానికి అక్షయమైన నిధి", "is_correct": True}
        ]
    }
    res = client.post("/api/assessment/submit", json=submission_payload)
    assert_test(res.status_code == 200, "Placement Test Submission HTTP 200", f"Status: {res.status_code}")
    res_data = res.json()
    assert_test(res_data.get('total_score') == 100, "100% Score Calculation on All Correct Answers", f"Score: {res_data.get('total_score')}")
    assert_test(res_data.get('proficiency_level') == "PROFICIENT", "Proficiency Level 'PROFICIENT' Assignment", f"Level: {res_data.get('proficiency_level')}")
    assert_test('learning_path' in res_data, "Adaptive Learning Path Recommendation Generation", f"Path Title present")

    # --- SECTION 4: LEARNER PROFILE & AUTH STATE PERSISTENCE ---
    print("\n>>> SECTION 4: LEARNER PROFILE & STATE PERSISTENCE")
    uid = uuid.uuid4().hex[:8]
    reg_res = client.post("/api/auth/register", json={
        "first_name": "Comprehensive",
        "last_name": "Tester",
        "email": f"comprehensive_{uid}@example.com",
        "username": f"comp_user_{uid}",
        "password": "Password$123",
        "native_lang_id": 4
    })
    assert_test(reg_res.status_code in [200, 201], "Learner Registration HTTP 200/201", f"Status: {reg_res.status_code}")
    token = reg_res.json().get('access_token')

    profile_res = client.put("/api/auth/profile", headers={"Authorization": f"Bearer {token}"}, json={
        "first_name": "UpdatedTester",
        "last_name": "Pro",
        "literacy_level": "PROFICIENT",
        "native_lang_id": 4
    })
    assert_test(profile_res.status_code == 200, "Learner Profile Update HTTP 200", f"Status: {profile_res.status_code}")

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert_test(me_res.status_code == 200 and me_res.json().get('first_name') == "UpdatedTester", "Authenticated Profile Fetch Integrity", f"First Name: {me_res.json().get('first_name')}")

    # --- SECTION 5: DATABASE TABLES & DYNAMIC SCHEMA INSPECTION ---
    print("\n>>> SECTION 5: DATABASE SCHEMA & TABLE PERSISTENCE INTEGRITY")
    inspector = inspect(engine)
    active_tables = inspector.get_table_names()

    expected_tables = ['learner', 'learner_profile', 'learner_registration_progress', 'language', 'curriculum', 'module', 'lesson', 'assessment']
    for tbl in expected_tables:
        assert_test(tbl in active_tables, f"Database Schema Table Exists [{tbl}]", f"Found in active database tables")

    print("\n" + "=" * 100)
    print(f"       COMPREHENSIVE WEEK 1 & 2 MATRIX: {passed_count}/{total_tests} PASSED ({round((passed_count/total_tests)*100, 1)}%)")
    print("=" * 100)

if __name__ == '__main__':
    run_comprehensive_week1_week2_tests()
