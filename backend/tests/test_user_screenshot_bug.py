import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/assessment/submit"

def test_screenshot_bug():
    print("=" * 100)
    print("      TESTING EXACT USER SCREENSHOT CASES (jjjj for Q2, wrote for Q5)")
    print("=" * 100)

    payload = {
        "lang": "en",
        "answers": [
            {"stage": 1, "skill_type": "READ", "selected_option_id": "a"}, # Q1 READ -> Correct
            {"stage": 2, "skill_type": "WRITE", "written_text": "jjjj"},   # Q2 WRITE -> MUST BE INCORRECT (User screenshot 1)
            {"stage": 3, "skill_type": "SPEAK", "spoken_text": "Language unlocks knowledge"}, # Q3
            {"stage": 4, "skill_type": "READ", "selected_option_id": "a"}, # Q4 READ -> Correct
            {"stage": 5, "skill_type": "WRITE", "written_text": "wrote"}   # Q5 WRITE -> MUST BE INCORRECT (User screenshot 2)
        ]
    }

    res = requests.post(BASE_URL, json=payload)
    data = res.json()
    details = data.get("validated_details", [])

    q2_item = next((d for d in details if d["question_id"] == 2), None)
    q5_item = next((d for d in details if d["question_id"] == 5), None)

    print(f"Q2 ('jjjj') is_correct: {q2_item.get('is_correct')} (Expected: False)")
    print(f"Q5 ('wrote') is_correct: {q5_item.get('is_correct')} (Expected: False)")

    assert q2_item.get('is_correct') == False, "ERROR: Q2 'jjjj' was incorrectly marked True!"
    assert q5_item.get('is_correct') == False, "ERROR: Q5 'wrote' was incorrectly marked True!"

    print("=" * 100)
    print("      SUCCESS: SCREENSHOT BUGS FULLY RESOLVED! 'jjjj' and 'wrote' are 100% REJECTED!")
    print("=" * 100)
    return True

if __name__ == "__main__":
    ok = test_screenshot_bug()
    if not ok:
        sys.exit(1)
