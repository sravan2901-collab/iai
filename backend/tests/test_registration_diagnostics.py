import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def test_registration_diagnostics():
    client = TestClient(app)
    print("\n=================== STARTING REGISTRATION DIAGNOSTIC CHECKS ===================")

    # Diagnostic Test 1: Weak Password Rejection
    weak_pass_payload = {
        "email": f"weak_{random.randint(1000,9999)}@example.com",
        "username": f"weakuser_{random.randint(1000,9999)}",
        "password": "123", # Failing password rules
        "first_name": "Weak Test"
    }
    r1 = client.post("/api/auth/register", json=weak_pass_payload)
    print(f"[DIAGNOSTIC 1] Weak Password Rejection -> Status: {r1.status_code}, Detail: {r1.json().get('detail')}")
    assert r1.status_code == 400
    assert "Password must be at least 8 characters" in r1.json()["detail"]

    # Diagnostic Test 2: Existing Email Rejection
    existing_email_payload = {
        "email": "sravan2901@gmail.com", # Already exists
        "username": f"unique_user_{random.randint(10000,99999)}",
        "password": "StrongPassword@123",
        "first_name": "Duplicate Test"
    }
    r2 = client.post("/api/auth/register", json=existing_email_payload)
    print(f"[DIAGNOSTIC 2] Existing Email Rejection -> Status: {r2.status_code}, Detail: {r2.json().get('detail')}")
    assert r2.status_code == 400
    assert "Email already exists" in r2.json()["detail"]

    # Diagnostic Test 3: Existing Username Rejection
    existing_user_payload = {
        "email": f"new_email_{random.randint(10000,99999)}@example.com",
        "username": "autotestuser", # Existing username
        "password": "StrongPassword@123",
        "first_name": "Duplicate Username Test"
    }
    r3 = client.post("/api/auth/register", json=existing_user_payload)
    print(f"[DIAGNOSTIC 3] Existing Username Rejection -> Status: {r3.status_code}, Detail: {r3.json().get('detail')}")
    assert r3.status_code == 400
    assert "Username already exists" in r3.json()["detail"]

    # Diagnostic Test 4: Valid New Registration
    rand_id = random.randint(100000, 999999)
    valid_payload = {
        "email": f"newlearner_{rand_id}@example.com",
        "username": f"newlearner_{rand_id}",
        "password": "ValidPass@123",
        "first_name": "Valid Learner",
        "native_lang_id": 1
    }
    r4 = client.post("/api/auth/register", json=valid_payload)
    print(f"[DIAGNOSTIC 4] Valid New Registration -> Status: {r4.status_code}, User ID: {r4.json().get('user_id')}")
    assert r4.status_code == 200
    assert "access_token" in r4.json()
    assert r4.json()["username"] == f"newlearner_{rand_id}"

    print("=================== ALL 4 REGISTRATION DIAGNOSTIC CHECKS PASSED 100%! ===================\n")

if __name__ == "__main__":
    test_registration_diagnostics()
