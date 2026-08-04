import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/assessment"
LANGUAGES = ["en", "te", "hi", "ta", "bn", "mr", "kn", "es"]

def run_wrong_answers_test():
    print("=" * 100)
    print("      LIVE TEST: SUBMITTING WRONG ANSWERS ACROSS ALL 8 LANGUAGES")
    print("=" * 100)

    for lang in LANGUAGES:
        print(f"\n>>> TESTING LANGUAGE: [{lang.upper()}] <<<")
        
        # 1. Fetch questions for language
        res_q = requests.get(f"{BASE_URL}/diagnostic-questions?lang={lang}")
        questions = res_q.json()
        print(f"Loaded {len(questions)} diagnostic questions for {lang.upper()}.")

        # 2. Build 100% WRONG submission payload
        wrong_payload = {
            "lang": lang,
            "answers": []
        }

        for q in questions:
            skill = q["skill_type"]
            q_id = q["stage"]
            if skill == "READ":
                # Pick an option that is WRONG (is_correct == False)
                wrong_opt = next((opt["id"] for opt in q.get("options", []) if not opt.get("is_correct")), "b")
                wrong_payload["answers"].append({
                    "stage": q_id,
                    "skill_type": skill,
                    "selected_option_id": wrong_opt
                })
            elif skill == "WRITE":
                # Submit wrong text that is NOT in accepted_answers
                wrong_payload["answers"].append({
                    "stage": q_id,
                    "skill_type": skill,
                    "written_text": "WRONG_INCORRECT_TEXT_xyz"
                })
            elif skill == "SPEAK":
                # Submit completely wrong or empty speech
                wrong_payload["answers"].append({
                    "stage": q_id,
                    "skill_type": skill,
                    "spoken_text": "gibberish wrong speech input"
                })

        # 3. Submit wrong answers to API
        res_sub = requests.post(f"{BASE_URL}/submit", json=wrong_payload)
        data = res_sub.json()

        print(f"  Result Status      : {data.get('status')}")
        print(f"  Total Score        : {data.get('total_score')}%")
        print(f"  Correct Count      : {data.get('correct_answers')} / {data.get('total_questions')}")
        print(f"  Proficiency Level  : {data.get('proficiency_level')}")
        print("  Question-by-Question Validation Details:")
        for v in data.get("validated_details", []):
            status_str = "PASSED (CORRECT)" if v["is_correct"] else "REJECTED (WRONG)"
            print(f"    - Question {v['question_id']} [{v['skill_type']}]: {status_str}")

        assert data.get("total_score") == 0, f"Expected 0% score for wrong answers in {lang}, got {data.get('total_score')}"
        assert data.get("correct_answers") == 0, f"Expected 0 correct answers in {lang}, got {data.get('correct_answers')}"
        assert data.get("proficiency_level") == "FOUNDATIONAL", f"Expected FOUNDATIONAL tier for {lang}, got {data.get('proficiency_level')}"
        print(f"  => SUCCESS: All wrong answers strictly REJECTED for {lang.upper()}!")

    print("\n" + "=" * 100)
    print("      ALL WRONG ANSWERS WERE STRICTLY REJECTED ACROSS ALL 8 LANGUAGES (100% SUCCESS)")
    print("=" * 100)

if __name__ == "__main__":
    run_wrong_answers_test()
