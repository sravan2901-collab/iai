import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/assessment"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def test_mixed_right_and_wrong():
    print("=" * 100)
    print("      LIVE TEST: MIXED CORRECT & WRONG ANSWERS ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    scenarios = [
        {"name": "1 Correct, 8 Wrong", "correct_target": 1, "expected_score": 11, "expected_level": "FOUNDATIONAL"},
        {"name": "3 Correct, 6 Wrong", "correct_target": 3, "expected_score": 33, "expected_level": "FOUNDATIONAL"},
        {"name": "5 Correct, 4 Wrong", "correct_target": 5, "expected_score": 56, "expected_level": "FUNCTIONAL"},
        {"name": "7 Correct, 2 Wrong", "correct_target": 7, "expected_score": 78, "expected_level": "PROFICIENT"},
    ]

    all_passed = True
    total_tests = 0
    passed_tests = 0

    for lang in LANGUAGES:
        print(f"\n==================== LANGUAGE: [{lang.upper()}] ====================")
        res_q = requests.get(f"{BASE_URL}/diagnostic-questions?lang={lang}")
        questions = res_q.json()

        for sc in scenarios:
            total_tests += 1
            target_correct = sc["correct_target"]
            
            payload = {
                "lang": lang,
                "answers": []
            }

            for idx, q in enumerate(questions):
                skill = q["skill_type"]
                q_id = q["stage"]
                
                if idx < target_correct:
                    # Provide RIGHT answer
                    if skill == "READ":
                        corr_opt = next((opt["id"] for opt in q.get("options", []) if opt.get("is_correct")), "a")
                        payload["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": corr_opt})
                    elif skill == "WRITE":
                        acc_ans = q.get("accepted_answers", ["correct"])[0]
                        payload["answers"].append({"stage": q_id, "skill_type": skill, "written_text": acc_ans})
                    elif skill == "SPEAK":
                        target = q.get("target_text", "speech")
                        payload["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": target})
                else:
                    # Provide WRONG answer
                    if skill == "READ":
                        wrong_opt = next((opt["id"] for opt in q.get("options", []) if not opt.get("is_correct")), "b")
                        payload["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": wrong_opt})
                    elif skill == "WRITE":
                        payload["answers"].append({"stage": q_id, "skill_type": skill, "written_text": "WRONG_INCORRECT_TEXT_123"})
                    elif skill == "SPEAK":
                        payload["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": "gibberish wrong phrase"})

            res = requests.post(f"{BASE_URL}/submit", json=payload)
            data = res.json()

            actual_score = data.get("total_score")
            actual_correct = data.get("correct_answers")
            actual_level = data.get("proficiency_level")

            is_ok = (
                res.status_code == 200 and
                actual_correct == target_correct and
                actual_score == sc["expected_score"] and
                actual_level == sc["expected_level"]
            )

            if is_ok:
                passed_tests += 1
                print(f"  [PASSED] {sc['name']} [{lang.upper()}] -> Score: {actual_score}% ({actual_correct}/9), Tier: {actual_level}")
            else:
                all_passed = False
                print(f"  [FAILED] {sc['name']} [{lang.upper()}] -> Expected {sc['expected_score']}%, got {actual_score}% ({actual_correct}/9), Level: {actual_level}")

    print("\n" + "=" * 100)
    print(f"       MIXED RIGHT & WRONG ACCURACY MATRIX: {passed_tests}/{total_tests} PASSED")
    print("=" * 100)
    return all_passed

if __name__ == "__main__":
    success = test_mixed_right_and_wrong()
    if not success:
        sys.exit(1)
