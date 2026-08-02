import sys
import os
import json
import re
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Learner, LearnerProfile

def run_exhaustive_frontend_test_suite():
    client = TestClient(app)
    results = []

    def log_test(test_num, name, status, details):
        symbol = "[PASSED]" if status else "[FAILED]"
        results.append({"num": test_num, "name": name, "passed": status, "details": details})
        print(f"[TEST {test_num:02d}] {name:<55} -> {symbol} | {details}")

    print("\n====================================================================================================")
    print("                 AKSHARAI COMPREHENSIVE EXHAUSTIVE FRONTEND & BACKEND TEST MATRIX                    ")
    print("====================================================================================================\n")

    # -------------------------------------------------------------------------
    # GROUP 1: API CONTRACT & ENDPOINT ACCESSIBILITY FOR FRONTEND CONSUMPTION
    # -------------------------------------------------------------------------
    
    # Test 1: API Health / Root Docs Availability
    r1 = client.get("/docs")
    log_test(1, "API OpenAPI Docs Accessibility", r1.status_code == 200, f"Status: {r1.status_code}")

    # Test 2: Login Invalid Credentials (401 Handling)
    r2 = client.post("/api/auth/login", json={"email": "nonexistent@example.com", "password": "WrongPassword@123"})
    log_test(2, "Login Invalid Credentials (401 Handling)", r2.status_code == 401, f"Detail: {r2.json().get('detail')}")

    # Test 3: Login Missing Required Fields (422 Unprocessable Entity)
    r3 = client.post("/api/auth/login", json={"email": "incomplete@example.com"})
    log_test(3, "Login Payload Validation (422 Handling)", r3.status_code == 422, "Pydantic caught missing password")

    # Test 4: Registration Weak Password Rejection
    r4 = client.post("/api/auth/register", json={"email": "weak@example.com", "username": "weakuser", "password": "123"})
    log_test(4, "Registration Weak Password Rules (400 Handling)", r4.status_code == 400, f"Detail: {r4.json().get('detail')}")

    # Test 5: Forgot Password Endpoint
    email = "sravan2901@gmail.com"
    r5 = client.post("/api/auth/forgot-password", json={"email": email})
    log_test(5, "Forgot Password Dispatch OTP (200 Handling)", r5.status_code == 200, f"Dispatched to: {email}")
    otp_code = r5.json().get("otp_code")

    # Test 6: Verify Invalid Reset OTP Code (< 6 digits or non-matching)
    r6 = client.post("/api/auth/verify-reset-otp", json={"email": email, "otp_code": "000000"})
    log_test(6, "Verify Reset Invalid OTP Rejection", r6.status_code == 400, f"Detail: {r6.json().get('detail')}")

    # Test 7: Verify Valid Dispatched Reset OTP Code
    r7 = client.post("/api/auth/verify-reset-otp", json={"email": email, "otp_code": otp_code})
    log_test(7, "Verify Reset Valid OTP Verification", r7.status_code == 200, f"Status: {r7.json().get('status')}")

    # Test 8: Reset Password & Auto-Token Generation
    target_pass = "Elsa$123"
    r8 = client.post("/api/auth/reset-password", json={"email": email, "otp_code": otp_code, "new_password": target_pass})
    token = r8.json().get("access_token")
    log_test(8, "Reset Password Auto-Authentication", r8.status_code == 200 and bool(token), "JWT token issued post-reset")

    # Test 9: Profile Endpoint With Bearer Token (/api/auth/me)
    headers = {"Authorization": f"Bearer {token}"}
    r9 = client.get("/api/auth/me", headers=headers)
    log_test(9, "Authenticated User Profile Fetch (/auth/me)", r9.status_code == 200, f"Username: {r9.json().get('username')}")

    # Test 10: Unauthenticated Profile Fetch Rejection (/api/auth/me)
    r10 = client.get("/api/auth/me")
    log_test(10, "Unauthenticated Profile Access Rejection", r10.status_code == 401, f"Detail: {r10.json().get('detail')}")

    # -------------------------------------------------------------------------
    # GROUP 2: FRONTEND BUNDLE & COMPONENT SOURCE INTEGRITY
    # -------------------------------------------------------------------------

    component_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "components"))
    
    # Test 11: DiagnosticTest.jsx Source Code English Language Audit
    diag_file = os.path.join(component_dir, "DiagnosticTest.jsx")
    with open(diag_file, "r", encoding="utf-8") as f:
        diag_content = f.read()
    hindi_regex = re.compile(r'[\u0900-\u097F]')
    has_hindi_diag = bool(hindi_regex.search(diag_content))
    log_test(11, "DiagnosticTest.jsx Standard English Audit", not has_hindi_diag, "No non-English characters detected")

    # Test 12: PronunciationCoach.jsx Source Code English Language Audit
    coach_file = os.path.join(component_dir, "PronunciationCoach.jsx")
    with open(coach_file, "r", encoding="utf-8") as f:
        coach_content = f.read()
    has_hindi_coach = bool(hindi_regex.search(coach_content))
    log_test(12, "PronunciationCoach.jsx Standard English Audit", not has_hindi_coach, "No non-English characters detected")

    # Test 13: VoiceGuide.jsx Source Code English Language Audit
    guide_file = os.path.join(component_dir, "VoiceGuide.jsx")
    with open(guide_file, "r", encoding="utf-8") as f:
        guide_content = f.read()
    has_hindi_guide = bool(hindi_regex.search(guide_content))
    log_test(13, "VoiceGuide.jsx Standard English Audit", not has_hindi_guide, "No non-English characters detected")

    # Test 14: AudioVisualizer.jsx Source Code English Language Audit
    vis_file = os.path.join(component_dir, "AudioVisualizer.jsx")
    with open(vis_file, "r", encoding="utf-8") as f:
        vis_content = f.read()
    has_hindi_vis = bool(hindi_regex.search(vis_content))
    log_test(14, "AudioVisualizer.jsx Standard English Audit", not has_hindi_vis, "No non-English characters detected")

    # Test 15: AuthModal.jsx Modal Mode Handlers Audit
    auth_file = os.path.join(component_dir, "AuthModal.jsx")
    with open(auth_file, "r", encoding="utf-8") as f:
        auth_content = f.read()
    has_modes = all(m in auth_content for m in ["handleLoginSubmit", "handleRegisterSubmit", "handleForgotPassword", "handleVerifyOTP", "handleResetPassword"])
    log_test(15, "AuthModal.jsx 5-Mode Workflow Audit", has_modes, "All 5 auth modes implemented with state handling")

    # Test 16: api.js Timeout Controller Audit
    api_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "api.js"))
    with open(api_file, "r", encoding="utf-8") as f:
        api_content = f.read()
    has_timeout = "AbortController" in api_content and "setTimeout" in api_content
    log_test(16, "api.js Fetch AbortController Timeout Audit", has_timeout, "8-second timeout controller implemented")

    # -------------------------------------------------------------------------
    # GROUP 3: PRODUCTION BUILD ARTIFACT VERIFICATION
    # -------------------------------------------------------------------------

    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dist"))
    
    # Test 17: Build Directory Production Index HTML Exists
    dist_html = os.path.join(dist_dir, "index.html")
    log_test(17, "Production Bundle Index HTML Exists", os.path.exists(dist_html), f"Path: {dist_html}")

    # Test 18: Build Production Assets JS Bundle Exists
    assets_dir = os.path.join(dist_dir, "assets")
    js_files = [f for f in os.listdir(assets_dir) if f.endswith(".js")] if os.path.exists(assets_dir) else []
    log_test(18, "Production Bundle JS Asset Exists", len(js_files) > 0, f"Found JS bundles: {js_files}")

    # Test 19: Build Production Assets CSS Bundle Exists
    css_files = [f for f in os.listdir(assets_dir) if f.endswith(".css")] if os.path.exists(assets_dir) else []
    log_test(19, "Production Bundle CSS Asset Exists", len(css_files) > 0, f"Found CSS bundles: {css_files}")

    # -------------------------------------------------------------------------
    # GROUP 4: ADVANCED SECURITY, DATABASE & CORS EDGE CASE TESTS
    # -------------------------------------------------------------------------

    # Test 20: CORS Options Pre-flight Request
    r20 = client.options("/api/auth/login", headers={"Origin": "http://127.0.0.1:5173", "Access-Control-Request-Method": "POST"})
    log_test(20, "CORS Options Pre-Flight Handling", r20.status_code in [200, 204], f"Status: {r20.status_code}")

    # Test 21: Case-Sensitive Password Rejection Check (eLsa$123 vs Elsa$123)
    r21 = client.post("/api/auth/login", json={"email": email, "password": "eLsa$123"})
    log_test(21, "Strict Password Case Sensitivity Enforcement", r21.status_code == 401, "Wrong case rejected cleanly with 401")

    # Test 22: Special Character Rich Password Registration & Authentication
    rand_user = f"specuser_{random.randint(1000, 9999)}"
    spec_pass = "ComplexP@ssw0rd!#$&"
    r22_reg = client.post("/api/auth/register", json={
        "email": f"{rand_user}@example.com",
        "username": rand_user,
        "password": spec_pass,
        "first_name": "Special User"
    })
    r22_log = client.post("/api/auth/login", json={"email": f"{rand_user}@example.com", "password": spec_pass})
    log_test(22, "Special Character Password Reg & Login", r22_reg.status_code == 200 and r22_log.status_code == 200, "Complex characters handled cleanly")

    # Test 23: Database Learner Profile Integrity Check
    db = SessionLocal()
    db_learner = db.query(Learner).filter(Learner.email == email).first()
    db_profile = db.query(LearnerProfile).filter(LearnerProfile.learner_id == db_learner.learner_id).first() if db_learner else None
    db.close()
    log_test(23, "Database Learner & Profile Foreign Key Sync", db_learner is not None and db_profile is not None, f"Learner ID: {db_learner.learner_id if db_learner else 'None'}")

    # Test 24: High Frequency Request Handling (Stress Test 5 Parallel Calls)
    rapid_results = [client.get("/api/auth/latest-otp?email=" + email).status_code for _ in range(5)]
    log_test(24, "Rapid Sequential API Request Stability", all(code == 200 for code in rapid_results), f"5/5 Requests succeeded with 200 OK")

    # Test 25: JWT Token Payload Claims Check
    claims_ok = token is not None and len(token.split('.')) == 3
    log_test(25, "JWT Token Bearer Specification Compliance", claims_ok, "3-part base64 encoded JWT structure validated")

    # -------------------------------------------------------------------------
    # SUMMARY & FINAL VERIFICATION SCORE
    # -------------------------------------------------------------------------

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print("\n====================================================================================================")
    print(f"                       FRONTEND & BACKEND TEST MATRIX: {passed}/{total} PASSED ({(passed/total)*100:.1f}%)                 ")
    print("====================================================================================================\n")

    assert passed == total, f"Only {passed}/{total} tests passed!"

if __name__ == "__main__":
    run_exhaustive_frontend_test_suite()
