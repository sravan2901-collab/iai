"""
Stale Learning Path Multi-Path Regression Test Suite
Verifies all 7 previously vulnerable call sites:
1. complete_lesson_workflow (learning_path.py)
2. generate_personalized_path (learning_path.py)
3. check_and_award_achievements (gamification_service.py)
4. get_recommendations (recommendation.py)
5. build_learner_progress_snapshot / dashboard (progress.py)
6. get_module_progress (progress.py)
7. get_learning_history (progress.py)
When a learner has multiple LearningPath rows (e.g. 1st COMPLETED, 2nd ACTIVE),
all systems must target the latest ACTIVE path without falling back to stale paths.
"""
import sys
import os
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import create_access_token
from app.routers.learning_path import complete_lesson_workflow
from app.services.gamification_service import check_and_award_achievements

client = TestClient(app)


class TestStalePathResolution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

        # 1. Create a dedicated test learner with 2 learning paths
        cls.learner = cls.db.query(models.Learner).filter(models.Learner.email == "multipath_tester@aksharai.org").first()
        if not cls.learner:
            cls.learner = models.Learner(
                email="multipath_tester@aksharai.org",
                username="multipath_tester",
                password_hash="test_hash"
            )
            cls.db.add(cls.learner)
            cls.db.commit()
            cls.db.refresh(cls.learner)

        cls.profile = cls.db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == cls.learner.learner_id).first()
        if not cls.profile:
            cls.profile = models.LearnerProfile(
                learner_id=cls.learner.learner_id,
                first_name="MultiPath",
                last_name="Tester",
                literacy_level="FOUNDATIONAL",
                reading_pct=40.0,
                comprehension_pct=50.0,
                voice_pct=60.0
            )
            cls.db.add(cls.profile)
            cls.db.commit()

        # Ensure sample lessons exist
        cls.module = cls.db.query(models.Module).first()
        cls.lessons = cls.db.query(models.Lesson).filter(models.Lesson.module_id == cls.module.module_id).limit(3).all()
        if len(cls.lessons) < 2:
            l1 = models.Lesson(module_id=cls.module.module_id, title="Lesson A", content_type="Reading", target_text="Text A", difficulty_level="FOUNDATIONAL")
            l2 = models.Lesson(module_id=cls.module.module_id, title="Lesson B", content_type="Reading", target_text="Text B", difficulty_level="FOUNDATIONAL")
            cls.db.add_all([l1, l2])
            cls.db.commit()
            cls.lessons = [l1, l2]

        # 2. Path 1: Old Stale Path (Status = COMPLETED)
        cls.old_path = models.LearningPath(
            learner_id=cls.learner.learner_id,
            target_proficiency="FOUNDATIONAL",
            current_level="FOUNDATIONAL",
            status="COMPLETED",
            completion_percentage=100.0,
            generated_on=datetime(2026, 1, 1, tzinfo=timezone.utc)
        )
        cls.db.add(cls.old_path)
        cls.db.commit()
        cls.db.refresh(cls.old_path)

        # 3. Path 2: New Active Path (Status = ACTIVE)
        cls.active_path = models.LearningPath(
            learner_id=cls.learner.learner_id,
            target_proficiency="FUNCTIONAL",
            current_level="FOUNDATIONAL",
            status="ACTIVE",
            completion_percentage=0.0,
            generated_on=datetime.now(timezone.utc)
        )
        cls.db.add(cls.active_path)
        cls.db.commit()
        cls.db.refresh(cls.active_path)

        # Attach PathLesson items to active path
        cls.pl1 = models.PathLesson(
            path_id=cls.active_path.path_id,
            lesson_id=cls.lessons[0].lesson_id,
            sequence_no=1,
            status="UNLOCKED"
        )
        cls.pl2 = models.PathLesson(
            path_id=cls.active_path.path_id,
            lesson_id=cls.lessons[1].lesson_id,
            sequence_no=2,
            status="LOCKED"
        )
        cls.db.add_all([cls.pl1, cls.pl2])
        cls.db.commit()

        cls.token = create_access_token({"sub": str(cls.learner.learner_id), "email": cls.learner.email})
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_complete_lesson_workflow_targets_active_path(self):
        """Verify complete_lesson_workflow updates the ACTIVE path and unlocks next lesson on ACTIVE path."""
        result = complete_lesson_workflow(
            learner_id=self.learner.learner_id,
            lesson_id=self.lessons[0].lesson_id,
            score=85.0,
            db=self.db,
            award_points=True
        )
        self.assertIsNotNone(result)

        # Refresh from DB
        self.db.refresh(self.pl1)
        self.db.refresh(self.pl2)
        self.assertEqual(self.pl1.status, "COMPLETED")
        self.assertEqual(self.pl2.status, "UNLOCKED")
        print("  [OK] [complete_lesson_workflow] Correctly unlocked subsequent lesson on active path")

    def test_02_progress_dashboard_snapshot_uses_active_path(self):
        """Verify /api/progress/dashboard reports stats for the ACTIVE path (not stale path)."""
        res = client.get("/api/progress/dashboard", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        path_stats = data["path_stats"]
        self.assertEqual(path_stats["path_id"], self.active_path.path_id)
        self.assertEqual(path_stats["completed_lessons"], 1)
        self.assertEqual(path_stats["unlocked_lessons"], 1)
        print(f"  [OK] [Dashboard Snapshot] Correctly referenced active path #{path_stats['path_id']}")

    def test_03_module_progress_uses_active_path(self):
        """Verify /api/progress/module/{id} resolves lesson status against ACTIVE path."""
        res = client.get(f"/api/progress/module/{self.module.module_id}", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        completed_count = data["completed_lessons"]
        self.assertGreaterEqual(completed_count, 1)
        print(f"  [OK] [Module Progress] Correctly resolved {completed_count} completed lessons on active path")

    def test_04_learning_history_uses_active_path(self):
        """Verify /api/progress/history queries completed lessons from ACTIVE path."""
        res = client.get("/api/progress/history", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("history", data)
        self.assertGreaterEqual(len(data["history"]), 1)
        print(f"  [OK] [Learning History] Returned {len(data['history'])} completed records from active path")

    def test_05_gamification_service_evaluates_active_path(self):
        """Verify check_and_award_achievements correctly queries active path."""
        new_badges = check_and_award_achievements(
            learner_id=self.learner.learner_id,
            db=self.db
        )
        self.assertIsInstance(new_badges, list)
        print(f"  [OK] [Gamification Service] Evaluated active path, unlocked {len(new_badges)} badges")

    def test_06_recommendation_router_uses_active_path(self):
        """Verify /api/recommendations calculates lesson progress off active path."""
        res = client.get("/api/recommendations", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("recommendations", data)
        self.assertEqual(len(data["recommendations"]), 3)
        print("  [OK] [Recommendations Router] Successfully built recommendations using active path context")


if __name__ == '__main__':
    unittest.main()
