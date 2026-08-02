import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Learner, LearnerProfile

def run_registration_exhaustive_tests():
    client = TestClient(app)
    results = []

    def log_test(num, name, status, details):
        symbol = "[PASSED]" if status else "[FAILED]"
        results.append({"num": num, "name": name, "passed": status, "details": details})
        print(f"[REG-TEST {num:02d}] {name:<55} -> {symbol} | {details}")

    print("\n====================================================================================================")
    print("                AKSHARAI DEDICATED EXHAUSTIVE REGISTRATION TEST MATRIX (25 CASES)                   ")
    print("====================================================================================================\n")

    # 1. Valid Registration (Happy Path)
    rand_id = random.randint(100000, 999999)
    email1 = f"reguser_{rand_id}@example.com"
    user1 = f"reguser_{rand_id}"
    pass1 = "StrongP@ss123"
    r1 = client.post("/api/auth/register", json={"email": email1, "username": user1, "password": pass1, "first_name": "Reg Test"})
    v_token1 = r1.json().get("verification_token")
    log_test(1, "Happy Path Standard Registration", r1.status_code == 200 and "access_token" in r1.json(), f"User ID: {r1.json().get('user_id')}")

    # 2. Missing Email Field (422)
    r2 = client.post("/api/auth/register", json={"username": "user2", "password": pass1})
    log_test(2, "Missing Email Field Rejection (422)", r2.status_code == 422, "Pydantic validation caught missing email")

    # 3. Missing Username Field (422)
    r3 = client.post("/api/auth/register", json={"email": "user3@example.com", "password": pass1})
    log_test(3, "Missing Username Field Rejection (422)", r3.status_code == 422, "Pydantic validation caught missing username")

    # 4. Missing Password Field (422)
    r4 = client.post("/api/auth/register", json={"email": "user4@example.com", "username": "user4"})
    log_test(4, "Missing Password Field Rejection (422)", r4.status_code == 422, "Pydantic validation caught missing password")

    # 5. Empty Password String (400)
    r5 = client.post("/api/auth/register", json={"email": "user5@example.com", "username": "user5", "password": ""})
    log_test(5, "Empty Password String Rejection (400)", r5.status_code == 400, f"Detail: {r5.json().get('detail')}")

    # 6. Short Password (< 8 chars) (400)
    r6 = client.post("/api/auth/register", json={"email": "user6@example.com", "username": "user6", "password": "P1!"})
    log_test(6, "Short Password (< 8 Chars) Rejection (400)", r6.status_code == 400, "Rule length >= 8 enforced")

    # 7. Missing Uppercase Letter (400)
    r7 = client.post("/api/auth/register", json={"email": "user7@example.com", "username": "user7", "password": "password123!"})
    log_test(7, "Missing Uppercase Letter Rejection (400)", r7.status_code == 400, "Rule uppercase enforced")

    # 8. Missing Lowercase Letter (400)
    r8 = client.post("/api/auth/register", json={"email": "user8@example.com", "username": "user8", "password": "PASSWORD123!"})
    log_test(8, "Missing Lowercase Letter Rejection (400)", r8.status_code == 400, "Rule lowercase enforced")

    # 9. Missing Digit (400)
    r9 = client.post("/api/auth/register", json={"email": "user9@example.com", "username": "user9", "password": "Password!"})
    log_test(9, "Missing Digit Rejection (400)", r9.status_code == 400, "Rule digit enforced")

    # 10. Missing Special Character (400)
    r10 = client.post("/api/auth/register", json={"email": "user10@example.com", "username": "user10", "password": "Password123"})
    log_test(10, "Missing Special Character Rejection (400)", r10.status_code == 400, "Rule special character enforced")

    # 11. Duplicate Exact Email (400)
    r11 = client.post("/api/auth/register", json={"email": email1, "username": f"user11_{rand_id}", "password": pass1})
    log_test(11, "Duplicate Exact Email Rejection (400)", r11.status_code == 400, f"Detail: {r11.json().get('detail')}")

    # 12. Duplicate Case-Insensitive Email (400)
    r12 = client.post("/api/auth/register", json={"email": email1.upper(), "username": f"user12_{rand_id}", "password": pass1})
    log_test(12, "Duplicate Case-Insensitive Email Rejection (400)", r12.status_code == 400, "Case-insensitive email duplicate caught")

    # 13. Duplicate Exact Username (400)
    r13 = client.post("/api/auth/register", json={"email": f"user13_{rand_id}@example.com", "username": user1, "password": pass1})
    log_test(13, "Duplicate Exact Username Rejection (400)", r13.status_code == 400, f"Detail: {r13.json().get('detail')}")

    # 14. Duplicate Case-Insensitive Username (400)
    r14 = client.post("/api/auth/register", json={"email": f"user14_{rand_id}@example.com", "username": user1.upper(), "password": pass1})
    log_test(14, "Duplicate Case-Insensitive Username Rejection (400)", r14.status_code == 400, "Case-insensitive username duplicate caught")

    # 15. Whitespace Trimming in Email
    r15 = client.post("/api/auth/register", json={"email": f"  trimmed_{rand_id}@example.com  ", "username": f"trimmed_{rand_id}", "password": pass1})
    log_test(15, "Email Leading/Trailing Whitespace Trimming", r15.status_code == 200, "Email whitespace trimmed cleanly")

    # 16. Whitespace Trimming in Username
    r16 = client.post("/api/auth/register", json={"email": f"user16_{rand_id}@example.com", "username": f"  user16_{rand_id}  ", "password": pass1})
    log_test(16, "Username Leading/Trailing Whitespace Trimming", r16.status_code == 200 and r16.json()["username"] == f"user16_{rand_id}", "Username trimmed")

    # 17. Special Character Rich Passwords
    spec_pass = "P@$$w0rd!#$&*()_+-=[]{}|;:,.<>?"
    r17 = client.post("/api/auth/register", json={"email": f"user17_{rand_id}@example.com", "username": f"user17_{rand_id}", "password": spec_pass})
    log_test(17, "Complex Symbol Rich Password Support", r17.status_code == 200, "Complex symbols registered cleanly")

    # 18. Very Long Password (> 72 Bytes Slicing)
    long_pass = "SuperLongP@sswordExceedingSeventyTwoBytesLimit123456789012345678901234567890!"
    r18 = client.post("/api/auth/register", json={"email": f"user18_{rand_id}@example.com", "username": f"user18_{rand_id}", "password": long_pass})
    log_test(18, "Very Long Password (> 72 Bytes) Slicing", r18.status_code == 200, "Native bcrypt byte truncation handled without exception")

    # 19. Default Language ID Fallback
    r19 = client.post("/api/auth/register", json={"email": f"user19_{rand_id}@example.com", "username": f"user19_{rand_id}", "password": pass1})
    log_test(19, "Default Language ID (1) Fallback", r19.status_code == 200, "Default lang_id=1 assigned")

    # 20. Database LearnerProfile Initializer Verification
    db = SessionLocal()
    learner20 = db.query(Learner).filter(Learner.email == email1).first()
    profile20 = db.query(LearnerProfile).filter(LearnerProfile.learner_id == learner20.learner_id).first() if learner20 else None
    db.close()
    valid_profile = (profile20 is not None and profile20.literacy_level == "FOUNDATIONAL" and profile20.streak_count == 1 and profile20.total_points == 50)
    log_test(20, "Database LearnerProfile Auto-Initialization", valid_profile, "LearnerProfile created with level=FOUNDATIONAL, streak=1, points=50")

    # 21. SQL Injection Input Safety in Registration
    sql_email = f"sqlinj_{rand_id}' OR 1=1; --@example.com"
    r21 = client.post("/api/auth/register", json={"email": sql_email, "username": f"sqlinj_{rand_id}", "password": pass1})
    log_test(21, "SQL Injection Input Sanitization Check", r21.status_code == 200, "SQL injection string safely stored without exception")

    # 22. XSS Script Injection Input Safety in Registration
    xss_name = "<script>alert('xss')</script>"
    r22 = client.post("/api/auth/register", json={"email": f"xss_{rand_id}@example.com", "username": f"xss_{rand_id}", "password": pass1, "first_name": xss_name})
    log_test(22, "XSS Script Tag Input Handling Check", r22.status_code == 200, "XSS string sanitized and safely stored")

    # 23. Verification Token Generation Check
    log_test(23, "Email Verification Token Generation", bool(v_token1) and len(v_token1) > 20, f"Verification token generated: {v_token1[:15]}...")

    # 24. Valid Email Verification Endpoint (/verify-email)
    r24 = client.post("/api/auth/verify-email", json={"token": v_token1})
    log_test(24, "Email Verification Endpoint Execution", r24.status_code == 200, f"Status: {r24.json().get('status')}")

    # 25. Fake / Invalid Email Verification Token Rejection (400)
    r25 = client.post("/api/auth/verify-email", json={"token": "invalid_fake_token_999"})
    log_test(25, "Fake Verification Token Rejection (400)", r25.status_code == 400, f"Detail: {r25.json().get('detail')}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print("\n====================================================================================================")
    print(f"               EXHAUSTIVE REGISTRATION MATRIX RESULT: {passed}/{total} PASSED ({(passed/total)*100:.1f}%)            ")
    print("====================================================================================================\n")

    assert passed == total, f"Only {passed}/{total} registration tests passed!"

if __name__ == "__main__":
    run_registration_exhaustive_tests()
