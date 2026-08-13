import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

def test_diagnostic_submission():
    client = TestClient(app)
    
    # 1. Login user to get token
    login_res = client.post("/api/auth/login", json={"email": "test@aksharai.dev", "password": "password123"})
    print(f"Login status: {login_res.status_code}")
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Submit diagnostic assessment
    payload = {
        "lang": "en",
        "answers": [
            {"question_id": 1, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
            {"question_id": 2, "skill_type": "WRITE", "written_text": "library", "is_correct": True},
            {"question_id": 3, "skill_type": "SPEAK", "spoken_text": "Language unlocks knowledge", "is_correct": True},
            {"question_id": 4, "skill_type": "READ", "selected_option_id": "a", "is_correct": False},
            {"question_id": 5, "skill_type": "WRITE", "written_text": "wrong", "is_correct": False},
            {"question_id": 6, "skill_type": "SPEAK", "spoken_text": "wrong", "is_correct": False},
            {"question_id": 7, "skill_type": "READ", "selected_option_id": "a", "is_correct": False},
            {"question_id": 8, "skill_type": "WRITE", "written_text": "wrong", "is_correct": False},
            {"question_id": 9, "skill_type": "SPEAK", "spoken_text": "wrong", "is_correct": False}
        ]
    }
    
    res = client.post("/api/assessment/submit", json=payload, headers=headers)
    print(f"Submit status: {res.status_code}")
    print("Submit Response JSON:")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    test_diagnostic_submission()
