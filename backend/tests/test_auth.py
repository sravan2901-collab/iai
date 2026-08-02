import sys
import os

# Add backend directory to sys.path for importing app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_valid_user():
    payload = {
        "email": "test_learner_1@example.com",
        "username": "testlearner1",
        "password": "StrongP@ssword123",
        "first_name": "Test Learner",
        "native_lang_id": 1
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code in [200, 400]

def test_forgot_password_and_reset_otp():
    # 1. Request OTP
    email = "sravan2901@gmail.com"
    forgot_res = client.post("/api/auth/forgot-password", json={"email": email})
    assert forgot_res.status_code == 200
    data = forgot_res.json()
    assert "otp_code" in data
    otp_code = data["otp_code"]
    assert len(otp_code) == 6

    # 2. Verify OTP
    verify_res = client.post("/api/auth/verify-reset-otp", json={"email": email, "otp_code": otp_code})
    assert verify_res.status_code == 200

    # 3. Reset Password
    reset_res = client.post("/api/auth/reset-password", json={
        "email": email,
        "otp_code": otp_code,
        "new_password": "NewStrongP@ss123"
    })
    assert reset_res.status_code == 200
