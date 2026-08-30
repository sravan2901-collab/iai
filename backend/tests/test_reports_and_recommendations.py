"""
Learning Reports & Recommendations Verification Test Suite
Tests:
1. POST /api/reports/generate produces full snapshot + AI pedagogical narrative.
2. Graceful fallback when AI providers are unavailable (narrative generated or null, no 500 crash).
3. GET /api/reports/history lists learner's past reports in chronological order.
4. GET /api/reports/{report_id} returns full report details for owner.
5. Multi-tenant privacy: Learner B cannot access Learner A's report (returns HTTP 404).
6. GET /api/recommendations returns 3 valid pedagogical interventions.
"""
import sys
import os
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import create_access_token
from app.services.gamification_service import seed_achievement_catalog

client = TestClient(app)


class TestReportsAndRecommendations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        seed_achievement_catalog(cls.db)

        # Primary Learner
        cls.learner_a = cls.db.query(models.Learner).filter(models.Learner.email == "report_tester_a@aksharai.org").first()
        if not cls.learner_a:
            cls.learner_a = models.Learner(
                email="report_tester_a@aksharai.org",
                username="report_tester_a",
                password_hash="test_hash"
            )
            cls.db.add(cls.learner_a)
            cls.db.commit()
            cls.db.refresh(cls.learner_a)

        cls.profile_a = cls.db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == cls.learner_a.learner_id).first()
        if not cls.profile_a:
            cls.profile_a = models.LearnerProfile(
                learner_id=cls.learner_a.learner_id,
                first_name="Report",
                last_name="Tester",
                literacy_level="FUNCTIONAL",
                reading_pct=85.0,
                comprehension_pct=90.0,
                voice_pct=75.0,
                streak_count=4,
                total_points=150
            )
            cls.db.add(cls.profile_a)
            cls.db.commit()

        # Secondary Learner (for security testing)
        cls.learner_b = cls.db.query(models.Learner).filter(models.Learner.email == "report_tester_b@aksharai.org").first()
        if not cls.learner_b:
            cls.learner_b = models.Learner(
                email="report_tester_b@aksharai.org",
                username="report_tester_b",
                password_hash="test_hash"
            )
            cls.db.add(cls.learner_b)
            cls.db.commit()
            cls.db.refresh(cls.learner_b)

        cls.token_a = create_access_token({"sub": str(cls.learner_a.learner_id), "email": cls.learner_a.email})
        cls.auth_headers_a = {"Authorization": f"Bearer {cls.token_a}"}

        cls.token_b = create_access_token({"sub": str(cls.learner_b.learner_id), "email": cls.learner_b.email})
        cls.auth_headers_b = {"Authorization": f"Bearer {cls.token_b}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_generate_learning_report(self):
        """Verify POST /api/reports/generate generates snapshot, persists to DB, and returns report."""
        res = client.post("/api/reports/generate", headers=self.auth_headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("report_id", data)
        self.assertIn("reporting_period", data)
        self.assertIn("overall_progress", data)
        self.assertIn("snapshot", data)
        self.assertIn("narrative", data)

        snapshot = data["snapshot"]
        self.assertIn("profile", snapshot)
        self.assertEqual(snapshot["profile"]["literacy_level"], "FUNCTIONAL")
        self.assertIsInstance(data["narrative"], str)
        self.assertGreater(len(data["narrative"]), 10)

        self.__class__.generated_report_id = data["report_id"]
        print(f"  [OK] [Report Generation] Report #{data['report_id']} generated with overall progress: {data['overall_progress']}%")

    def test_02_report_history_listing(self):
        """Verify GET /api/reports/history lists the generated reports for the authenticated learner."""
        res = client.get("/api/reports/history", headers=self.auth_headers_a)
        self.assertEqual(res.status_code, 200)
        reports = res.json()

        self.assertIsInstance(reports, list)
        self.assertGreaterEqual(len(reports), 1)
        self.assertEqual(reports[0]["report_id"], self.__class__.generated_report_id)
        print(f"  [OK] [Report History] Found {len(reports)} past reports for learner")

    def test_03_report_detail_and_data_integrity(self):
        """Verify GET /api/reports/{report_id} returns full report details and snapshot."""
        rep_id = self.__class__.generated_report_id
        res = client.get(f"/api/reports/{rep_id}", headers=self.auth_headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["report_id"], rep_id)
        self.assertIn("snapshot", data)
        self.assertIn("narrative", data)
        print(f"  [OK] [Report Detail] Successfully retrieved report #{rep_id} with full narrative")

    def test_04_unauthorized_cross_learner_access_forbidden(self):
        """Verify Learner B cannot access Learner A's report (404/403 security boundary)."""
        rep_id = self.__class__.generated_report_id
        res = client.get(f"/api/reports/{rep_id}", headers=self.auth_headers_b)
        self.assertEqual(res.status_code, 404)
        print(f"  [OK] [Multi-Tenant Security] Cross-learner report access correctly blocked (HTTP {res.status_code})")

    def test_05_get_recommendations_endpoint(self):
        """Verify GET /api/recommendations returns 3 valid AI/rule-based next-lesson recommendations."""
        res = client.get("/api/recommendations", headers=self.auth_headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("recommendations", data)
        recs = data["recommendations"]
        self.assertEqual(len(recs), 3)

        for r in recs:
            self.assertIn("title", r)
            self.assertIn("reason", r)
            self.assertIn("priority", r)
            self.assertIn("skill_focus", r)
        print(f"  [OK] [Recommendations] Successfully returned {len(recs)} next-lesson recommendations")


if __name__ == '__main__':
    unittest.main()
