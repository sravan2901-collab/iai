import sys
import os
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def generate_random_password():
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*")
    rest = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"P@{upper}{lower}{digit}{special}{rest}"

def run_stress_test():
    client = TestClient(app)
    print("\n=================== STARTING STRESS TEST FOR PASSWORD RESET & LOGIN ===================")
    
    test_email = "sravan2901@gmail.com"

    for iteration in range(1, 6):
        new_pass = generate_random_password()
        print(f"\n--- [ITERATION {iteration}/5] Testing Reset with New Password: '{new_pass}' ---")

        # 1. Forgot Password Request
        req_res = client.post("/api/auth/forgot-password", json={"email": test_email})
        assert req_res.status_code == 200, f"Forgot password failed: {req_res.text}"
        otp_code = req_res.json()["otp_code"]
        print(f"  [OK] 1. Forgot Password Requested -> Dispatched OTP: {otp_code}")

        # 2. Verify OTP
        ver_res = client.post("/api/auth/verify-reset-otp", json={"email": test_email, "otp_code": otp_code})
        assert ver_res.status_code == 200, f"Verify OTP failed: {ver_res.text}"
        print(f"  [OK] 2. OTP Code Verified -> Status: 200")

        # 3. Reset Password
        reset_res = client.post("/api/auth/reset-password", json={
            "email": test_email,
            "otp_code": otp_code,
            "new_password": new_pass
        })
        assert reset_res.status_code == 200, f"Reset password failed: {reset_res.text}"
        print(f"  [OK] 3. Password Reset Completed in DB -> Status: 200")

        # 4. Attempt Login with Old Password (MUST FAIL)
        old_login = client.post("/api/auth/login", json={"email": test_email, "password": "WrongOldPassword123!"})
        assert old_login.status_code == 401, f"Old password should have been rejected, got: {old_login.status_code}"
        print(f"  [OK] 4. Old Password Login Correctly Rejected -> Status 401 Unauthorized")

        # 5. Attempt Login with NEW Password (MUST SUCCEED)
        new_login = client.post("/api/auth/login", json={"email": test_email, "password": new_pass})
        assert new_login.status_code == 200, f"New password login failed: {new_login.text}"
        token = new_login.json()["access_token"]
        assert token, "Access token missing from login response"
        print(f"  [OK] 5. New Password Login SUCCESSFUL -> JWT Token: {token[:25]}...")

    print("\n=================== STRESS TEST COMPLETED: 5/5 ITERATIONS PASSED PERFECTLY! ===================\n")

if __name__ == "__main__":
    run_stress_test()
