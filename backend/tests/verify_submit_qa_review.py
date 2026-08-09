import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/assessment/submit"

def verify_submit_qa_review():
    print("=" * 100)
    print("      VERIFYING DIAGNOSTIC QUESTION & CORRECT ANSWER REVIEW DATA IN SUBMIT RESPONSE")
    print("=" * 100)

    payload = {
        "lang": "en",
        "answers": [
            {"stage": 1, "skill_type": "READ", "selected_option_id": "a"}, # Correct
            {"stage": 2, "skill_type": "WRITE", "written_text": "WRONG_ANSWER_123"}, # Wrong
            {"stage": 3, "skill_type": "SPEAK", "spoken_text": "Language unlocks knowledge, wisdom, and human expression"}, # Correct
            {"stage": 4, "skill_type": "READ", "selected_option_id": "b"}, # Wrong
            {"stage": 5, "skill_type": "WRITE", "written_text": "written"}, # Correct
            {"stage": 6, "skill_type": "SPEAK", "spoken_text": ""}, # Wrong
            {"stage": 7, "skill_type": "READ", "selected_option_id": "a"}, # Correct
            {"stage": 8, "skill_type": "WRITE", "written_text": "eloquence"}, # Correct
            {"stage": 9, "skill_type": "SPEAK", "spoken_text": "Mastery over language transforms thought into eloquent communication and lifelong empowerment"} # Correct
        ]
    }

    res = requests.post(BASE_URL, json=payload)
    if res.status_code != 200:
        print(f"[FAILED] HTTP Status: {res.status_code}")
        return False

    data = res.json()
    print(f"Total Score         : {data.get('total_score')}%")
    print(f"Correct Answers     : {data.get('correct_answers')} / {data.get('total_questions')}")
    print(f"Proficiency Level   : {data.get('proficiency_level')}")
    print(f"Validated Details   : {len(data.get('validated_details', []))} questions\n")

    details = data.get("validated_details", [])
    if len(details) != 9:
        print(f"[FAILED] Expected 9 validated question details, got {len(details)}")
        return False

    for item in details:
        status_str = "PASSED (CORRECT)" if item.get("is_correct") else "REJECTED (INCORRECT)"
        print(f"  Question {item.get('question_id')} [{item.get('skill_type')}]: {status_str}")
        print(f"    - Title   : {item.get('question_title')}")
        print(f"    - User Ans: {item.get('user_answer')}")
        print(f"    - Corr Ans: {item.get('correct_answer')}\n")

        assert "user_answer" in item, "Missing user_answer in validated_details item"
        assert "correct_answer" in item, "Missing correct_answer in validated_details item"
        assert "question_title" in item, "Missing question_title in validated_details item"

    print("=" * 100)
    print("      SUCCESS: QUESTION & CORRECT ANSWER REVIEW METADATA VERIFIED 100%")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = verify_submit_qa_review()
    if not ok:
        sys.exit(1)
