import sys
import os
import requests

BASE_URL = "http://127.0.0.1:8000/api/assessment"

LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def test_strict_answer_validation():
    print("=" * 100)
    print("      TESTING STRICT DIAGNOSTIC ANSWER VALIDATION ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    all_passed = True
    total_subtests = 0
    passed_subtests = 0

    for lang in LANGUAGES:
        print(f"\n--- Language: [{lang.upper()}] ---")
        
        # 1. Fetch questions for language
        res = requests.get(f"{BASE_URL}/diagnostic-questions?lang={lang}")
        if res.status_code != 200:
            print(f"[FAILED] Fetch questions HTTP {res.status_code} for {lang}")
            all_passed = False
            continue
        
        data = res.json()
        questions = data if isinstance(data, list) else data.get("questions", [])
        if len(questions) != 9:
            print(f"[FAILED] Expected 9 questions for {lang}, got {len(questions)}")
            all_passed = False
            continue
            
        print(f"  [+] Loaded {len(questions)} diagnostic questions.")

        # Test Case A: All Correct Answers -> Must score 100% (9/9 correct)
        correct_submission = {
            "lang": lang,
            "answers": []
        }
        
        for q in questions:
            skill = q["skill_type"]
            q_id = q["stage"]
            if skill == "READ":
                # Find correct option id
                corr_opt = next((opt["id"] for opt in q.get("options", []) if opt.get("is_correct")), "a")
                correct_submission["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": corr_opt, "is_correct": True})
            elif skill == "WRITE":
                # Use first accepted answer
                acc_ans = q.get("accepted_answers", ["correct"])[0]
                correct_submission["answers"].append({"stage": q_id, "skill_type": skill, "written_text": acc_ans, "is_correct": True})
            elif skill == "SPEAK":
                target = q.get("target_text", "speech")
                correct_submission["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": target, "is_correct": True})

        res_a = requests.post(f"{BASE_URL}/submit", json=correct_submission)
        total_subtests += 1
        if res_a.status_code == 200 and res_a.json().get("correct_answers") == 9 and res_a.json().get("total_score") == 100:
            print(f"  [PASSED] All Correct Submission Test [{lang.upper()}] -> Score: 100%, Level: {res_a.json().get('proficiency_level')}")
            passed_subtests += 1
        else:
            print(f"  [FAILED] All Correct Submission Test [{lang.upper()}] -> Status: {res_a.status_code}")
            all_passed = False

        # Test Case B: All Wrong Answers -> Must score 0% (0/9 correct)
        wrong_submission = {
            "lang": lang,
            "answers": []
        }
        
        for q in questions:
            skill = q["skill_type"]
            q_id = q["stage"]
            if skill == "READ":
                # Find wrong option id
                wrong_opt = next((opt["id"] for opt in q.get("options", []) if not opt.get("is_correct")), "b")
                wrong_submission["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": wrong_opt, "is_correct": True}) # client sending fake is_correct=True
            elif skill == "WRITE":
                wrong_submission["answers"].append({"stage": q_id, "skill_type": skill, "written_text": "WRONG_GARBAGE_TEXT_123", "is_correct": True})
            elif skill == "SPEAK":
                wrong_submission["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": "", "is_correct": False})

        res_b = requests.post(f"{BASE_URL}/submit", json=wrong_submission)
        total_subtests += 1
        data_b = res_b.json()
        if res_b.status_code == 200 and data_b.get("correct_answers") == 0 and data_b.get("total_score") == 0:
            print(f"  [PASSED] All Wrong Submission Rejection [{lang.upper()}] -> Score: 0%, Level: {data_b.get('proficiency_level')}")
            passed_subtests += 1
        else:
            print(f"  [FAILED] All Wrong Submission Rejection [{lang.upper()}] -> Resp: {data_b}")
            print(f"  [DEBUG] Validated Details: {data_b.get('validated_details')}")
            all_passed = False

    print("\n" + "=" * 100)
    print(f"       STRICT DIAGNOSTIC VALIDATION MATRIX: {passed_subtests}/{total_subtests} PASSED")
    print("=" * 100)
    return all_passed

if __name__ == "__main__":
    success = test_strict_answer_validation()
    if not success:
        sys.exit(1)
