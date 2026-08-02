import sys
import os
import random
from datetime import datetime, timedelta, timezone
from jose import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Learner, LearnerProfile
from app.auth import get_password_hash
from app.config import settings

def run_login_exhaustive_tests():
    client = TestClient(app)
    results = []

    def log_test(num, name, status, details):
        symbol = "[PASSED]" if status else "[FAILED]"
        results.append({"num": num, "name": name, "passed": status, "details": details})
        print(f"[LOGIN-TEST {num:02d}] {name:<55} -> {symbol} | {details}")

    print("\n====================================================================================================")
    print("                    AKSHARAI DEDICATED EXHAUSTIVE LOGIN TEST MATRIX (30 CASES)                      ")
    print("====================================================================================================\n")

    # Setup Test User: testlogin@example.com with password 'Elsa$123'
    db = SessionLocal()
    email_target = "testlogin@example.com"
    pass_target = "Elsa$123"
    
    learner = db.query(Learner).filter(Learner.email == email_target).first()
    if not learner:
        learner = Learner(
            email=email_target,
            username="testlogin_user",
            password_hash=get_password_hash(pass_target),
            current_lang_id=1,
            is_email_verified=True
        )
        db.add(learner)
        db.commit()
        db.refresh(learner)

        profile = LearnerProfile(
            learner_id=learner.learner_id,
            first_name="Test",
            last_name="Login",
            literacy_level="FOUNDATIONAL",
            streak_count=3,
            total_points=150
        )
        db.add(profile)
        db.commit()
    else:
        learner.password_hash = get_password_hash(pass_target)
        db.commit()

    learner_id_val = learner.learner_id
    db.close()

    # 1. Happy Path Standard Login (200)
    r1 = client.post("/api/auth/login", json={"email": email_target, "password": pass_target})
    token1 = r1.json().get("access_token")
    log_test(1, "Happy Path Standard Login", r1.status_code == 200 and bool(token1), f"User ID: {r1.json().get('user_id')}")

    # 2. Missing Email Field (422)
    r2 = client.post("/api/auth/login", json={"password": pass_target})
    log_test(2, "Missing Email Field Rejection (422)", r2.status_code == 422, "Pydantic validation caught missing email")

    # 3. Missing Password Field (422)
    r3 = client.post("/api/auth/login", json={"email": email_target})
    log_test(3, "Missing Password Field Rejection (422)", r3.status_code == 422, "Pydantic validation caught missing password")

    # 4. Empty Email String (401)
    r4 = client.post("/api/auth/login", json={"email": "", "password": pass_target})
    log_test(4, "Empty Email String Rejection (401)", r4.status_code == 401, f"Detail: {r4.json().get('detail')}")

    # 5. Empty Password String (401)
    r5 = client.post("/api/auth/login", json={"email": email_target, "password": ""})
    log_test(5, "Empty Password String Rejection (401)", r5.status_code == 401, f"Detail: {r5.json().get('detail')}")

    # 6. Unregistered Email Address (401)
    r6 = client.post("/api/auth/login", json={"email": "nonexistent999@example.com", "password": pass_target})
    log_test(6, "Unregistered Email Rejection (401)", r6.status_code == 401, "No learner account found")

    # 7. Wrong Password (401)
    r7 = client.post("/api/auth/login", json={"email": email_target, "password": "WrongPassword@123"})
    log_test(7, "Incorrect Password Rejection (401)", r7.status_code == 401, f"Detail: {r7.json().get('detail')}")

    # 8. Strict Case Sensitivity - Wrong Letter Case (eLsa$123) (401)
    r8 = client.post("/api/auth/login", json={"email": email_target, "password": "eLsa$123"})
    log_test(8, "Strict Case Sensitivity (eLsa$123) Rejection", r8.status_code == 401, "Wrong case rejected with 401")

    # 9. Strict Case Sensitivity - All Caps (ELSA$123) (401)
    r9 = client.post("/api/auth/login", json={"email": email_target, "password": "ELSA$123"})
    log_test(9, "Strict Case Sensitivity (ELSA$123) Rejection", r9.status_code == 401, "All caps rejected with 401")

    # 10. Strict Case Sensitivity - All Lowercase (elsa$123) (401)
    r10 = client.post("/api/auth/login", json={"email": email_target, "password": "elsa$123"})
    log_test(10, "Strict Case Sensitivity (elsa$123) Rejection", r10.status_code == 401, "Lowercase rejected with 401")

    # 11. Case-Insensitive Email Matching (200)
    r11 = client.post("/api/auth/login", json={"email": email_target.upper(), "password": pass_target})
    log_test(11, "Case-Insensitive Email Login Matching", r11.status_code == 200, "Uppercase email logged in cleanly")

    # 12. Email Whitespace Trimming (200)
    r12 = client.post("/api/auth/login", json={"email": f"   {email_target}   ", "password": pass_target})
    log_test(12, "Email Whitespace Trimming", r12.status_code == 200, "Email whitespace trimmed")

    # 13. Password Whitespace Tolerance (200)
    r13 = client.post("/api/auth/login", json={"email": email_target, "password": f"  {pass_target}  "})
    log_test(13, "Password Whitespace Tolerance", r13.status_code == 200, "Space-stripped bcrypt fallback logged in")

    # 14. SQL Injection Attack Attempt in Email (401)
    r14 = client.post("/api/auth/login", json={"email": "admin' OR '1'='1", "password": pass_target})
    log_test(14, "SQL Injection Email Attempt Rejection", r14.status_code == 401, "SQLi attack prevented safely")

    # 15. SQL Injection Attack Attempt in Password (401)
    r15 = client.post("/api/auth/login", json={"email": email_target, "password": "' OR '1'='1"})
    log_test(15, "SQL Injection Password Attempt Rejection", r15.status_code == 401, "SQLi attack prevented safely")

    # 16. XSS Script Tag Attempt in Email (401)
    r16 = client.post("/api/auth/login", json={"email": "<script>alert(1)</script>", "password": pass_target})
    log_test(16, "XSS Script Tag Email Attempt Rejection", r16.status_code == 401, "XSS attack prevented safely")

    # 17. XSS Script Tag Attempt in Password (401)
    r17 = client.post("/api/auth/login", json={"email": email_target, "password": "<script>alert(1)</script>"})
    log_test(17, "XSS Script Tag Password Attempt Rejection", r17.status_code == 401, "XSS attack prevented safely")

    # 18. Exceedingly Long Password Attempt (401)
    long_fail_pass = "VeryLongIncorrectPasswordStringExceedingHundredCharactersLimit" * 5
    r18 = client.post("/api/auth/login", json={"email": email_target, "password": long_fail_pass})
    log_test(18, "Exceedingly Long Password Rejection (401)", r18.status_code == 401, "Bcrypt 72-byte limit handled safely")

    # 19. JWT Token Structure & Base64 Specification
    jwt_parts = token1.split('.') if token1 else []
    log_test(19, "JWT Access Token Spec Compliance (3-part)", len(jwt_parts) == 3, "Valid JWT Header.Payload.Signature format")

    # 20. Authenticated Route Profile Fetch (/api/auth/me) (200)
    headers20 = {"Authorization": f"Bearer {token1}"}
    r20 = client.get("/api/auth/me", headers=headers20)
    log_test(20, "Authenticated Route Access (/auth/me)", r20.status_code == 200, f"Email: {r20.json().get('email')}")

    # 21. Tampered / Fake Bearer Token Access (401)
    headers21 = {"Authorization": "Bearer fake_tampered_token_string"}
    r21 = client.get("/api/auth/me", headers=headers21)
    log_test(21, "Tampered Bearer Token Access Rejection (401)", r21.status_code == 401, f"Detail: {r21.json().get('detail')}")

    # 22. Malformed Authorization Header Format (401)
    headers22 = {"Authorization": "Basic invalid_header_format"}
    r22 = client.get("/api/auth/me", headers=headers22)
    log_test(22, "Malformed Auth Header Format Rejection (401)", r22.status_code == 401, "Non-Bearer header rejected")

    # 23. Rapid Sequential Login Stress (5 Calls)
    rapid_status = [client.post("/api/auth/login", json={"email": email_target, "password": pass_target}).status_code for _ in range(5)]
    log_test(23, "Rapid Sequential Login Request Stability", all(s == 200 for s in rapid_status), "5/5 Login requests returned 200 OK")

    # 24. CORS Options Pre-flight Check on /api/auth/login
    r24 = client.options("/api/auth/login", headers={"Origin": "http://127.0.0.1:5173", "Access-Control-Request-Method": "POST"})
    log_test(24, "CORS Options Pre-Flight Handling", r24.status_code in [200, 204], f"Status: {r24.status_code}")

    # 25. Database Learner Profile Sync Verification
    db = SessionLocal()
    db_l = db.query(Learner).filter(Learner.email == email_target).first()
    db_p = db.query(LearnerProfile).filter(LearnerProfile.learner_id == db_l.learner_id).first() if db_l else None
    db.close()
    log_test(25, "Database Learner & Profile State Sync", db_l is not None and db_p is not None, f"Streak: {db_p.streak_count if db_p else 0}, Points: {db_p.total_points if db_p else 0}")

    # 26. Expired Token Rejection Check (401)
    expired_exp = datetime.now(timezone.utc) - timedelta(hours=1)
    expired_token = jwt.encode({"sub": str(learner_id_val), "exp": expired_exp}, settings.SECRET_KEY, algorithm="HS256")
    r26 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    log_test(26, "Expired JWT Token Access Rejection (401)", r26.status_code == 401, f"Detail: {r26.json().get('detail')}")

    # 27. Non-Existent User ID Token Rejection (401)
    non_exist_token = jwt.encode({"sub": "99999999", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}, settings.SECRET_KEY, algorithm="HS256")
    r27 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {non_exist_token}"})
    log_test(27, "Non-Existent User ID Token Rejection (401)", r27.status_code == 401, f"Detail: {r27.json().get('detail')}")

    # 28. Login Response Token Schema Field Verification
    data28 = r1.json()
    valid_schema = all(k in data28 for k in ["access_token", "token_type", "user_id", "username", "literacy_level"])
    log_test(28, "Login Token Response Schema Compliance", valid_schema, f"Fields returned: {list(data28.keys())}")

    # 29. Re-authenticating After Password Update
    new_pass_temp = "NewPassword@123"
    r29_req = client.post("/api/auth/forgot-password", json={"email": email_target})
    otp29 = r29_req.json().get("otp_code")
    r29_reset = client.post("/api/auth/reset-password", json={"email": email_target, "otp_code": otp29, "new_password": new_pass_temp})
    r29_login = client.post("/api/auth/login", json={"email": email_target, "password": new_pass_temp})
    # Reset back to Elsa$123
    r29_req2 = client.post("/api/auth/forgot-password", json={"email": email_target})
    otp29_2 = r29_req2.json().get("otp_code")
    client.post("/api/auth/reset-password", json={"email": email_target, "otp_code": otp29_2, "new_password": pass_target})
    log_test(29, "Re-authentication Post-Password Reset", r29_reset.status_code == 200 and r29_login.status_code == 200, "New password authenticated & restored")

    # 30. Password Case Sensitivity Preservation Post-Reset Check
    r30_fail = client.post("/api/auth/login", json={"email": email_target, "password": "elsa$123"})
    log_test(30, "Case Sensitivity Preserved Post-Reset Check", r30_fail.status_code == 401, "Wrong case rejected after password reset")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print("\n====================================================================================================")
    print(f"                   EXHAUSTIVE LOGIN MATRIX RESULT: {passed}/{total} PASSED ({(passed/total)*100:.1f}%)              ")
    print("====================================================================================================\n")

    assert passed == total, f"Only {passed}/{total} login tests passed!"

if __name__ == "__main__":
    run_login_exhaustive_tests()
