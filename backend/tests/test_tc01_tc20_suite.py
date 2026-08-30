"""
Full Implementation & Test Suite for TC01 - TC20 Test Matrix.
Executes all 20 test cases against AksharAI FastAPI backend endpoints using starlette TestClient / httpx.
"""

import sys
import os
import unittest
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)

class TestTC01ToTC20Matrix(unittest.TestCase):
    """
    Test suite implementing TC01 to TC20 for AksharAI platform.
    """
    @classmethod
    def setUpClass(cls):
        cls.valid_token = None
        cls.valid_user_id = None
        cls.otp_code = None
        cls.test_email = "test1@akshar.ai"
        cls.test_username = "testuser1"
        cls.test_password = "Test@1234"

    def test_01_TC01_register_valid_data_succeeds(self):
        """TC01: Register with valid data succeeds (POST /api/auth/register)"""
        # Cleanup existing learner if present
        db = SessionLocal()
        existing = db.query(models.Learner).filter(models.Learner.email == self.test_email).first()
        if existing:
            db.delete(existing)
            db.commit()
        db.close()

        payload = {
            "email": self.test_email,
            "username": self.test_username,
            "password": self.test_password,
            "first_name": "TestUser1",
            "last_name": "Learner"
        }
        res = client.post("/api/auth/register", json=payload)
        self.assertIn(res.status_code, [200, 201], f"TC01 Failed: {res.text}")
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["literacy_level"], "FOUNDATIONAL")
        TestTC01ToTC20Matrix.valid_token = data["access_token"]
        TestTC01ToTC20Matrix.valid_user_id = data["user_id"]
        print("  ✓ [TC01 PASSED] Register with valid data succeeds")

    def test_02_TC02_register_fails_weak_password(self):
        """TC02: Register fails with weak password (POST /api/auth/register)"""
        payload = {
            "email": "test2@akshar.ai",
            "username": "testuser2",
            "password": "abcdefgh"
        }
        res = client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400, f"TC02 Failed: {res.text}")
        data = res.json()
        self.assertIn("Password must be at least 8 characters", data.get("detail", ""))
        print("  ✓ [TC02 PASSED] Register fails with weak password")

    def test_03_TC03_register_fails_duplicate_email(self):
        """TC03: Register fails with duplicate email (POST /api/auth/register)"""
        payload = {
            "email": self.test_email,
            "username": "newuniqueuser3",
            "password": self.test_password
        }
        res = client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400, f"TC03 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data.get("detail"), "Email address is already registered.")
        print("  ✓ [TC03 PASSED] Register fails with duplicate email")

    def test_04_TC04_register_fails_duplicate_username(self):
        """TC04: Register fails with duplicate username (POST /api/auth/register)"""
        payload = {
            "email": "unique4@akshar.ai",
            "username": self.test_username,
            "password": self.test_password
        }
        res = client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400, f"TC04 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data.get("detail"), "Username is already taken.")
        print("  ✓ [TC04 PASSED] Register fails with duplicate username")

    def test_05_TC05_login_succeeds_correct_credentials(self):
        """TC05: Login succeeds with correct credentials (POST /api/auth/login)"""
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        res = client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 200, f"TC05 Failed: {res.text}")
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("literacy_level", data)
        TestTC01ToTC20Matrix.valid_token = data["access_token"]
        print("  ✓ [TC05 PASSED] Login succeeds with correct credentials")

    def test_06_TC06_login_fails_wrong_password(self):
        """TC06: Login fails with wrong password (POST /api/auth/login)"""
        payload = {
            "email": self.test_email,
            "password": "WrongPass1!"
        }
        res = client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 401, f"TC06 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data.get("detail"), "Incorrect email or password")
        print("  ✓ [TC06 PASSED] Login fails with wrong password")

    def test_07_TC07_login_fails_non_existent_email(self):
        """TC07: Login fails for non-existent email (POST /api/auth/login)"""
        payload = {
            "email": "noone@akshar.ai",
            "password": self.test_password
        }
        res = client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 401, f"TC07 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data.get("detail"), "Incorrect email or password")
        print("  ✓ [TC07 PASSED] Login fails for non-existent email")

    def test_08_TC08_forgot_password_creates_new_account_if_not_found(self):
        """TC08: Forgot password creates new account if not found (POST /api/auth/forgot-password)"""
        forgot_email = "newuser@akshar.ai"
        payload = {"email": forgot_email}
        res = client.post("/api/auth/forgot-password", json=payload)
        self.assertEqual(res.status_code, 200, f"TC08 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("otp_code", data)
        TestTC01ToTC20Matrix.otp_code = data["otp_code"]
        print(f"  ✓ [TC08 PASSED] Forgot password creates new account if not found (OTP: {data['otp_code']})")

    def test_09_TC09_verify_reset_otp_fails_short_code(self):
        """TC09: Verify reset OTP fails with short/invalid code (POST /api/auth/verify-reset-otp)"""
        payload = {
            "email": self.test_email,
            "otp_code": "123"
        }
        res = client.post("/api/auth/verify-reset-otp", json=payload)
        self.assertEqual(res.status_code, 400, f"TC09 Failed: {res.text}")
        data = res.json()
        self.assertIn("Please enter a valid 6-digit OTP code", data.get("detail", ""))
        print("  ✓ [TC09 PASSED] Verify reset OTP fails with short/invalid code")

    def test_10_TC10_verify_reset_otp_succeeds_correct_code(self):
        """TC10: Verify reset OTP succeeds with correct code (POST /api/auth/verify-reset-otp)"""
        otp = TestTC01ToTC20Matrix.otp_code or "123456"
        payload = {
            "email": "newuser@akshar.ai",
            "otp_code": otp
        }
        res = client.post("/api/auth/verify-reset-otp", json=payload)
        self.assertEqual(res.status_code, 200, f"TC10 Failed: {res.text}")
        data = res.json()
        self.assertIn("OTP verified successfully", data.get("message", ""))
        print("  ✓ [TC10 PASSED] Verify reset OTP succeeds with correct code")

    def test_11_TC11_reset_password_fails_weak_new_password(self):
        """TC11: Reset password fails with weak new password (POST /api/auth/reset-password)"""
        otp = TestTC01ToTC20Matrix.otp_code or "123456"
        payload = {
            "email": "newuser@akshar.ai",
            "otp_code": otp,
            "new_password": "weakpass"
        }
        res = client.post("/api/auth/reset-password", json=payload)
        self.assertEqual(res.status_code, 400, f"TC11 Failed: {res.text}")
        data = res.json()
        self.assertIn("New password must be at least 8 characters long", data.get("detail", ""))
        print("  ✓ [TC11 PASSED] Reset password fails with weak new password")

    def test_12_TC12_email_verification_fails_fake_token(self):
        """TC12: Email verification fails for fake/invalid token (GET /api/auth/verify-email)"""
        res = client.get("/api/auth/verify-email?token=fake_token_123")
        self.assertEqual(res.status_code, 400, f"TC12 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data.get("detail"), "Invalid or expired email verification token.")
        print("  ✓ [TC12 PASSED] Email verification fails for fake/invalid token")

    def test_13_TC13_get_current_learner_profile_valid_token(self):
        """TC13: Get current learner profile with valid token (GET /api/auth/me)"""
        headers = {"Authorization": f"Bearer {TestTC01ToTC20Matrix.valid_token}"}
        res = client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200, f"TC13 Failed: {res.text}")
        data = res.json()
        self.assertEqual(data["email"], self.test_email)
        self.assertEqual(data["username"], self.test_username)
        print("  ✓ [TC13 PASSED] Get current learner profile with valid token")

    def test_14_TC14_get_proficiency_levels_for_learner(self):
        """TC14: Get proficiency levels for a learner (GET /api/learners/{learner_id}/proficiency)"""
        lid = TestTC01ToTC20Matrix.valid_user_id or 1
        res = client.get(f"/api/learners/{lid}/proficiency")
        self.assertEqual(res.status_code, 200, f"TC14 Failed: {res.text}")
        data = res.json()
        self.assertIsInstance(data, dict)
        print(f"  ✓ [TC14 PASSED] Get proficiency levels for learner ID {lid}")

    def test_15_TC15_get_proficiency_fails_non_existent_learner(self):
        """TC15: Get proficiency fails for non-existent learner (GET /api/learners/{learner_id}/proficiency)"""
        res = client.get("/api/learners/999999/proficiency")
        self.assertEqual(res.status_code, 404, f"TC15 Failed: {res.text}")
        data = res.json()
        self.assertIn("Learner with ID 999999 not found", data.get("detail", ""))
        print("  ✓ [TC15 PASSED] Get proficiency fails for non-existent learner")

    def test_16_TC16_get_diagnostic_questions_for_language(self):
        """TC16: Get diagnostic questions for a language (GET /api/assessment/diagnostic-questions)"""
        res = client.get("/api/assessment/diagnostic-questions?lang=en")
        self.assertEqual(res.status_code, 200, f"TC16 Failed: {res.text}")
        data = res.json()
        questions = data.get("questions", data) if isinstance(data, dict) else data
        self.assertIsInstance(questions, list)
        self.assertEqual(len(questions), 9)
        print("  ✓ [TC16 PASSED] Get diagnostic questions for a language")

    def test_17_TC17_submit_initial_assessment_valid_answers(self):
        """TC17: Submit initial assessment with valid answers (POST /api/assessment/submit)"""
        headers = {"Authorization": f"Bearer {TestTC01ToTC20Matrix.valid_token}"}
        payload = {
            "lang": "en",
            "answers": [
                {"stage": 1, "question_id": 1, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
                {"stage": 2, "question_id": 2, "skill_type": "WRITE", "written_text": "library", "is_correct": True},
                {"stage": 3, "question_id": 3, "skill_type": "SPEAK", "spoken_text": "Language unlocks knowledge", "is_correct": True},
                {"stage": 4, "question_id": 4, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
                {"stage": 5, "question_id": 5, "skill_type": "WRITE", "written_text": "written", "is_correct": True},
                {"stage": 6, "question_id": 6, "skill_type": "SPEAK", "spoken_text": "continuous practice brought clarity", "is_correct": True},
                {"stage": 7, "question_id": 7, "skill_type": "READ", "selected_option_id": "a", "is_correct": True},
                {"stage": 8, "question_id": 8, "skill_type": "WRITE", "written_text": "eloquence", "is_correct": True},
                {"stage": 9, "question_id": 9, "skill_type": "SPEAK", "spoken_text": "eloquent communication and lifelong empowerment", "is_correct": True}
            ]
        }
        res = client.post("/api/assessment/submit", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200, f"TC17 Failed: {res.text}")
        data = res.json()
        self.assertIn("proficiency_level", data)
        print("  ✓ [TC17 PASSED] Submit initial assessment with valid answers")

    def test_18_TC18_generate_adaptive_learning_path(self):
        """TC18: Generate adaptive learning path for learner (POST /api/learners/{learner_id}/learning-path/generate)"""
        lid = TestTC01ToTC20Matrix.valid_user_id or 1
        headers = {"Authorization": f"Bearer {TestTC01ToTC20Matrix.valid_token}"}
        res = client.post(f"/api/learners/{lid}/learning-path/generate", headers=headers)
        self.assertEqual(res.status_code, 200, f"TC18 Failed: {res.text}")
        data = res.json()
        self.assertIn("path_id", data)
        self.assertIn("learning_path", data)
        print("  ✓ [TC18 PASSED] Generate adaptive learning path for learner")

    def test_19_TC19_get_supported_languages_list(self):
        """TC19: Get supported languages list (GET /api/curriculum/languages)"""
        res = client.get("/api/curriculum/languages")
        self.assertEqual(res.status_code, 200, f"TC19 Failed: {res.text}")
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) >= 8)
        print(f"  ✓ [TC19 PASSED] Get supported languages list ({len(data)} languages supported)")

    def test_20_TC20_complete_lesson_update_progress(self):
        """TC20: Complete a lesson and update progress (POST /api/progress/complete-lesson)"""
        lid = TestTC01ToTC20Matrix.valid_user_id or 1
        headers = {"Authorization": f"Bearer {TestTC01ToTC20Matrix.valid_token}"}
        
        # Ensure learner has generated an active learning path first
        client.post(f"/api/learners/{lid}/learning-path/generate", headers=headers)

        db = SessionLocal()
        real_lesson = db.query(models.Lesson).first()
        target_lesson_id = real_lesson.lesson_id if real_lesson else 1
        db.close()

        payload = {
            "learner_id": lid,
            "lesson_id": target_lesson_id,
            "score": 85
        }
        res = client.post("/api/progress/complete-lesson", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200, f"TC20 Failed: {res.text}")
        data = res.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Lesson completed successfully!")
        print("  ✓ [TC20 PASSED] Complete a lesson and update progress")


if __name__ == "__main__":
    unittest.main()
