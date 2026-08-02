import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def run_all_tests():
    client = TestClient(app)
    print("\n=================== STARTING AUTOMATED AUTH & OTP TESTS ===================")

    # Test 1: Register
    reg_payload = {
        "email": "autotest_user@example.com",
        "username": "autotestuser",
        "password": "StrongP@ss123",
        "first_name": "Auto Test",
        "native_lang_id": 1
    }
    res1 = client.post("/api/auth/register", json=reg_payload)
    print(f"[TEST 1] Register User -> Status: {res1.status_code}")
    assert res1.status_code in [200, 400], f"Registration failed: {res1.text}"

    # Test 2: Request Forgot Password OTP
    email = "sravan2901@gmail.com"
    res2 = client.post("/api/auth/forgot-password", json={"email": email})
    print(f"[TEST 2] Request Reset OTP -> Status: {res2.status_code}, Response: {res2.json()}")
    assert res2.status_code == 200, f"Forgot password failed: {res2.text}"
    otp_code = res2.json()["otp_code"]
    assert len(otp_code) == 6, "OTP code length must be 6 digits"

    # Test 3: Fetch Latest OTP
    res3 = client.get(f"/api/auth/latest-otp?email={email}")
    print(f"[TEST 3] Fetch Latest Dispatched OTP -> Status: {res3.status_code}, OTP: {res3.json().get('otp_code')}")
    assert res3.status_code == 200, f"Latest OTP lookup failed: {res3.text}"
    assert res3.json()["otp_code"] == otp_code

    # Test 4: Verify OTP
    res4 = client.post("/api/auth/verify-reset-otp", json={"email": email, "otp_code": otp_code})
    print(f"[TEST 4] Verify 6-Digit Reset OTP -> Status: {res4.status_code}, Response: {res4.json()}")
    assert res4.status_code == 200, f"OTP verification failed: {res4.text}"

    # Test 5: Reset Password with New Strong Password
    res5 = client.post("/api/auth/reset-password", json={
        "email": email,
        "otp_code": otp_code,
        "new_password": "NewStrongP@ssword123"
    })
    print(f"[TEST 5] Update Password -> Status: {res5.status_code}, Response: {res5.json()}")
    assert res5.status_code == 200, f"Password reset failed: {res5.text}"

    # Test 6: Verify Login with New Password
    res6 = client.post("/api/auth/login", json={"email": email, "password": "NewStrongP@ssword123"})
    print(f"[TEST 6] Login with New Password -> Status: {res6.status_code}")
    assert res6.status_code == 200, f"Login with new password failed: {res6.text}"

    print("=================== ALL 6 TESTS PASSED SUCCESSFULLY! ===================\n")

if __name__ == "__main__":
    run_all_tests()
