import sys
import os
import requests

BASE_URL = "http://127.0.0.1:8000/api/assessment"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def test_mixed_answer_scoring():
    print("=" * 100)
    print("      TESTING MIXED ACCURACY SCORING & TIER ASSIGNMENT ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    all_passed = True
    total_subtests = 0
    passed_subtests = 0

    for lang in LANGUAGES:
        res = requests.get(f"{BASE_URL}/diagnostic-questions?lang={lang}")
        if res.status_code != 200:
            print(f"[FAILED] Fetch questions for {lang}")
            all_passed = False
            continue

        questions = res.json()

        # Mixed Test Case 1: 4 Correct out of 9 -> Score 44%, Level FOUNDATIONAL
        mixed_sub_1 = {"lang": lang, "answers": []}
        for idx, q in enumerate(questions):
            skill = q["skill_type"]
            q_id = q["stage"]
            if idx < 4:
                # Correct answers for first 4 questions
                if skill == "READ":
                    corr_opt = next((opt["id"] for opt in q.get("options", []) if opt.get("is_correct")), "a")
                    mixed_sub_1["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": corr_opt, "is_correct": True})
                elif skill == "WRITE":
                    acc_ans = q.get("accepted_answers", ["correct"])[0]
                    mixed_sub_1["answers"].append({"stage": q_id, "skill_type": skill, "written_text": acc_ans, "is_correct": True})
                elif skill == "SPEAK":
                    target = q.get("target_text", "speech")
                    mixed_sub_1["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": target, "is_correct": True})
            else:
                # Wrong answers for remaining 5 questions
                if skill == "READ":
                    wrong_opt = next((opt["id"] for opt in q.get("options", []) if not opt.get("is_correct")), "b")
                    mixed_sub_1["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": wrong_opt, "is_correct": False})
                elif skill == "WRITE":
                    mixed_sub_1["answers"].append({"stage": q_id, "skill_type": skill, "written_text": "WRONG_ANSWER_123", "is_correct": False})
                elif skill == "SPEAK":
                    mixed_sub_1["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": "", "is_correct": False})

        res1 = requests.post(f"{BASE_URL}/submit", json=mixed_sub_1)
        total_subtests += 1
        d1 = res1.json()
        if res1.status_code == 200 and d1.get("correct_answers") == 4 and d1.get("total_score") == 44 and d1.get("proficiency_level") == "FOUNDATIONAL":
            print(f"  [PASSED] 4/9 Mixed Scoring Test [{lang.upper()}] -> Score: 44%, Level: FOUNDATIONAL")
            passed_subtests += 1
        else:
            print(f"  [FAILED] 4/9 Mixed Scoring Test [{lang.upper()}] -> Resp: {d1}")
            all_passed = False

        # Mixed Test Case 2: 6 Correct out of 9 -> Score 67%, Level FUNCTIONAL
        mixed_sub_2 = {"lang": lang, "answers": []}
        for idx, q in enumerate(questions):
            skill = q["skill_type"]
            q_id = q["stage"]
            if idx < 6:
                # Correct answers for first 6 questions
                if skill == "READ":
                    corr_opt = next((opt["id"] for opt in q.get("options", []) if opt.get("is_correct")), "a")
                    mixed_sub_2["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": corr_opt, "is_correct": True})
                elif skill == "WRITE":
                    acc_ans = q.get("accepted_answers", ["correct"])[0]
                    mixed_sub_2["answers"].append({"stage": q_id, "skill_type": skill, "written_text": acc_ans, "is_correct": True})
                elif skill == "SPEAK":
                    target = q.get("target_text", "speech")
                    mixed_sub_2["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": target, "is_correct": True})
            else:
                # Wrong answers for remaining 3 questions
                if skill == "READ":
                    wrong_opt = next((opt["id"] for opt in q.get("options", []) if not opt.get("is_correct")), "b")
                    mixed_sub_2["answers"].append({"stage": q_id, "skill_type": skill, "selected_option_id": wrong_opt, "is_correct": False})
                elif skill == "WRITE":
                    mixed_sub_2["answers"].append({"stage": q_id, "skill_type": skill, "written_text": "WRONG_ANSWER_123", "is_correct": False})
                elif skill == "SPEAK":
                    mixed_sub_2["answers"].append({"stage": q_id, "skill_type": skill, "spoken_text": "", "is_correct": False})

        res2 = requests.post(f"{BASE_URL}/submit", json=mixed_sub_2)
        total_subtests += 1
        d2 = res2.json()
        if res2.status_code == 200 and d2.get("correct_answers") == 6 and d2.get("total_score") == 67 and d2.get("proficiency_level") == "FUNCTIONAL":
            print(f"  [PASSED] 6/9 Mixed Scoring Test [{lang.upper()}] -> Score: 67%, Level: FUNCTIONAL")
            passed_subtests += 1
        else:
            print(f"  [FAILED] 6/9 Mixed Scoring Test [{lang.upper()}] -> Resp: {d2}")
            all_passed = False

    print("\n" + "=" * 100)
    print(f"       MIXED SCORING MATRIX: {passed_subtests}/{total_subtests} PASSED")
    print("=" * 100)
    return all_passed

if __name__ == "__main__":
    success = test_mixed_answer_scoring()
    if not success:
        sys.exit(1)
