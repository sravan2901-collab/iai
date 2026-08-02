import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def test_case_sensitivity():
    client = TestClient(app)
    email = "sravan2901@gmail.com"
    correct_password = "Elsa$123"
    wrong_case_password = "eLsa$123"
    all_caps_password = "ELSA$123"

    print("\n=================== TESTING STRICT PASSWORD CASE-SENSITIVITY ===================")

    # Step 1: Set password to Elsa$123
    r1 = client.post("/api/auth/reset-password", json={
        "email": email,
        "otp_code": "123456",
        "new_password": correct_password
    })
    assert r1.status_code == 200, f"Reset password failed: {r1.text}"
    print(f"[PASSED] 1. Password reset to '{correct_password}'")

    # Step 2: Login with exact case Elsa$123 -> MUST SUCCEED (200)
    r2 = client.post("/api/auth/login", json={"email": email, "password": correct_password})
    assert r2.status_code == 200, f"Exact case login failed: {r2.text}"
    print(f"[PASSED] 2. Login with EXACT CASE '{correct_password}' -> Status: 200 OK (Access Token Issued)")

    # Step 3: Login with eLsa$123 -> MUST FAIL (401)
    r3 = client.post("/api/auth/login", json={"email": email, "password": wrong_case_password})
    assert r3.status_code == 401, f"Wrong case password '{wrong_case_password}' should have failed, got: {r3.status_code}"
    print(f"[PASSED] 3. Login with WRONG CASE '{wrong_case_password}' -> Status: 401 Incorrect email or password")

    # Step 4: Login with ELSA$123 -> MUST FAIL (401)
    r4 = client.post("/api/auth/login", json={"email": email, "password": all_caps_password})
    assert r4.status_code == 401, f"All caps password '{all_caps_password}' should have failed, got: {r4.status_code}"
    print(f"[PASSED] 4. Login with ALL CAPS '{all_caps_password}' -> Status: 401 Incorrect email or password")

    print("=================== STRICT CASE-SENSITIVITY VERIFIED 100%! ===================\n")

if __name__ == "__main__":
    test_case_sensitivity()
