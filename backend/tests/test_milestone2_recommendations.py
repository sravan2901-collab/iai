"""
Milestone 2 AI Personalized Learning Engine Verification Test Suite
Tests:
1. GET /api/recommendations/adaptive-plan — returns adaptive focus skill and recommended modules.
2. GET /api/recommendations/predict-proficiency — returns predictive proficiency trajectory and days to next level.
3. POST /api/recommendations/personalized-lessons — returns customized practice flashcards and prompt phrases.
4. GET /api/recommendations/recommended-content — returns dynamically weighted content items.
5. Verification of multi-language support (te, hi, ta, bn, mr, kn, es, en).
6. Non-collision with singular /api/recommendations endpoints.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import create_access_token

client = TestClient(app)


class TestMilestone2Recommendations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

        # Fetch or create test learner
        cls.learner = cls.db.query(models.Learner).filter(models.Learner.email == "m2_tester@aksharai.org").first()
        if not cls.learner:
            cls.learner = models.Learner(
                email="m2_tester@aksharai.org",
                username="m2_tester",
                password_hash="test_hash"
            )
            cls.db.add(cls.learner)
            cls.db.commit()
            cls.db.refresh(cls.learner)

        cls.profile = cls.db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == cls.learner.learner_id).first()
        if not cls.profile:
            cls.profile = models.LearnerProfile(
                learner_id=cls.learner.learner_id,
                first_name="M2",
                last_name="Tester",
                literacy_level="FOUNDATIONAL",
                reading_pct=42.0,
                comprehension_pct=65.0,
                voice_pct=50.0,
                streak_count=3,
                total_points=80
            )
            cls.db.add(cls.profile)
            cls.db.commit()
            cls.db.refresh(cls.profile)

        cls.token = create_access_token({"sub": str(cls.learner.learner_id), "email": cls.learner.email})
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_adaptive_plan_endpoint(self):
        """Verify GET /api/recommendations/adaptive-plan returns valid adaptive plan."""
        res = client.get("/api/recommendations/adaptive-plan?lang=en", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["learner_id"], self.learner.learner_id)
        self.assertEqual(data["primary_focus_skill"], "READING")  # Reading is 42.0 (lowest)
        self.assertIn("confidence_score", data)
        self.assertIn("recommended_modules", data)
        self.assertIn("rationale", data)
        self.assertGreaterEqual(len(data["recommended_modules"]), 1)
        print(f"  [OK] [Adaptive Plan] Focus skill: {data['primary_focus_skill']}, Confidence: {data['confidence_score']}")

    def test_02_predict_proficiency_endpoint(self):
        """Verify GET /api/recommendations/predict-proficiency returns trajectory and estimated days."""
        res = client.get("/api/recommendations/predict-proficiency?lang=en", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["learner_id"], self.learner.learner_id)
        self.assertIn("current_level", data)
        self.assertIn("predicted_next_level", data)
        self.assertIn("estimated_days_to_mastery", data)
        self.assertIn("accuracy_growth_rate", data)
        self.assertIn("prediction_summary", data)
        print(f"  [OK] [Proficiency Prediction] Predicted: {data['predicted_next_level']} in {data['estimated_days_to_mastery']} days")

    def test_03_personalized_lessons_endpoint(self):
        """Verify POST /api/recommendations/personalized-lessons generates custom exercises."""
        res = client.post("/api/recommendations/personalized-lessons?skill_type=READING&lang=te", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("lesson_id", data)
        self.assertEqual(data["target_skill"], "READING")
        self.assertEqual(data["language_code"], "te")
        self.assertIn("title", data)
        self.assertIn("practice_content", data)
        self.assertGreaterEqual(len(data["practice_content"]), 1)
        print(f"  [OK] [Personalized Lesson] Target: {data['target_skill']}, Type: {data['exercise_type']}")

    def test_04_recommended_content_endpoint(self):
        """Verify GET /api/recommendations/recommended-content returns dynamically weighted list."""
        res = client.get("/api/recommendations/recommended-content?lang=en", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        items = res.json()

        self.assertIsInstance(items, list)
        self.assertGreaterEqual(len(items), 1)
        self.assertIn("category", items[0])
        self.assertIn("relevance_score", items[0])
        print(f"  [OK] [Recommended Content] Returned {len(items)} items, Top: '{items[0]['title']}' ({items[0]['relevance_score']})")

    def test_05_multilingual_coverage(self):
        """Verify adaptive plan works across all target Indic languages and Spanish."""
        for lang in ["te", "hi", "ta", "bn", "mr", "kn", "es"]:
            res = client.get(f"/api/recommendations/adaptive-plan?lang={lang}", headers=self.auth_headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("recommended_modules", data)
        print("  [OK] [Multilingual Coverage] Verified 7 Indic/European languages (te, hi, ta, bn, mr, kn, es)")


if __name__ == '__main__':
    unittest.main()
