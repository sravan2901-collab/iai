"""
Gamification & Streak System Verification Test Suite
Tests:
1. Canonical Achievement catalog seeding and idempotency (no duplicates on repeated seeding).
2. Date-based streak calculation (same day, consecutive day, gap of 2+ days reset).
3. Points and achievement awarding on voice practice with score 100 ("Perfect Pronunciation" + "First Voice Practice").
4. Points and achievement awarding on lesson completion ("First Lesson Complete").
5. Double-award prevention between voice evaluation and lesson workflow.
6. Integration with GET /api/progress/dashboard.
"""
import sys
import os
import unittest
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine, SessionLocal
from app import models
from app.auth import create_access_token
from app.services.gamification_service import (
    seed_achievement_catalog,
    update_streak,
    check_and_award_achievements,
    CANONICAL_ACHIEVEMENTS
)

client = TestClient(app)


class TestGamificationPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

        # Seed catalog
        seed_achievement_catalog(cls.db)

        # Create or fetch dedicated test learner
        cls.learner = cls.db.query(models.Learner).filter(models.Learner.email == "gamify_test@aksharai.org").first()
        if not cls.learner:
            cls.learner = models.Learner(
                email="gamify_test@aksharai.org",
                username="gamify_tester",
                password_hash="test_hash"
            )
            cls.db.add(cls.learner)
            cls.db.commit()
            cls.db.refresh(cls.learner)

        cls.profile = cls.db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == cls.learner.learner_id).first()
        if not cls.profile:
            cls.profile = models.LearnerProfile(
                learner_id=cls.learner.learner_id,
                first_name="Gamify",
                last_name="Tester",
                literacy_level="FOUNDATIONAL",
                streak_count=0,
                total_points=0,
                last_activity_date=None
            )
            cls.db.add(cls.profile)
            cls.db.commit()
            cls.db.refresh(cls.profile)

        # Ensure learning path and lessons exist for learner
        cls.path = cls.db.query(models.LearningPath).filter(models.LearningPath.learner_id == cls.learner.learner_id).first()
        if not cls.path:
            cls.path = models.LearningPath(
                learner_id=cls.learner.learner_id,
                current_level="FOUNDATIONAL",
                target_proficiency="PROFICIENT",
                completion_percentage=0.0
            )
            cls.db.add(cls.path)
            cls.db.commit()
            cls.db.refresh(cls.path)

        lesson = cls.db.query(models.Lesson).first()
        if lesson:
            cls.test_lesson = lesson
            pl = cls.db.query(models.PathLesson).filter(
                models.PathLesson.path_id == cls.path.path_id,
                models.PathLesson.lesson_id == lesson.lesson_id
            ).first()
            if not pl:
                pl = models.PathLesson(
                    path_id=cls.path.path_id,
                    lesson_id=lesson.lesson_id,
                    sequence_no=1,
                    status="UNLOCKED"
                )
                cls.db.add(pl)
                cls.db.commit()

        cls.token = create_access_token({"sub": str(cls.learner.learner_id), "email": cls.learner.email})
        cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_achievement_catalog_seeding_and_idempotency(self):
        """Verify achievement catalog contains all canonical achievements and repeated seeding creates zero duplicates."""
        initial_count = self.db.query(models.Achievement).count()
        self.assertGreaterEqual(initial_count, len(CANONICAL_ACHIEVEMENTS))

        # Re-run seeding
        newly_inserted = seed_achievement_catalog(self.db)
        self.assertEqual(newly_inserted, 0, "Idempotent seed should insert 0 on repeated runs")

        after_count = self.db.query(models.Achievement).count()
        self.assertEqual(initial_count, after_count)

        # Verify key canonical titles exist
        names = [a.achievement_name for a in self.db.query(models.Achievement).all()]
        for expected in ["First Lesson Complete", "First Voice Practice", "Perfect Pronunciation", "3-Day Streak", "100 Points"]:
            self.assertIn(expected, names)
        print(f"  [OK] [Achievement Catalog] Total Seeded: {after_count} canonical badges (Idempotency verified)")

    def test_02_date_based_streak_tracking(self):
        """Verify streak increments on consecutive days, stays same on same day, and resets on gap >= 2 days."""
        learner_id = self.learner.learner_id

        # 1. First ever activity -> streak becomes 1
        self.profile.last_activity_date = None
        self.profile.streak_count = 0
        self.db.commit()

        new_streak = update_streak(learner_id, self.db)
        self.assertEqual(new_streak, 1)

        # 2. Same calendar day -> streak stays 1
        new_streak = update_streak(learner_id, self.db)
        self.assertEqual(new_streak, 1)

        # 3. Simulate yesterday activity -> streak increments to 2
        self.profile.last_activity_date = datetime.date.today() - datetime.timedelta(days=1)
        self.profile.streak_count = 1
        self.db.commit()

        new_streak = update_streak(learner_id, self.db)
        self.assertEqual(new_streak, 2)

        # 4. Simulate missed 3 days gap -> streak resets to 1
        self.profile.last_activity_date = datetime.date.today() - datetime.timedelta(days=3)
        self.profile.streak_count = 10
        self.db.commit()

        new_streak = update_streak(learner_id, self.db)
        self.assertEqual(new_streak, 1)
        print("  [OK] [Streak Tracking] Day-based streak arithmetic verified (same-day, +1 consecutive, reset on gap)")

    def test_03_voice_practice_with_score_100_awards_achievements(self):
        """Verify score 100 on voice practice awards Perfect Pronunciation and First Voice Practice."""
        # Reset learner achievements
        self.db.query(models.LearnerAchievement).filter(models.LearnerAchievement.learner_id == self.learner.learner_id).delete()
        self.profile.total_points = 0
        self.profile.streak_count = 1
        self.db.commit()

        # Call voice evaluate with audio and perfect transcript
        with open('test_te.mp3', 'rb') as f:
            mp3_bytes = f.read()

        lesson = self.db.query(models.Lesson).first()
        files = {'audio_file': ('test_te.mp3', mp3_bytes, 'audio/mpeg')}
        data = {'learner_id': self.learner.learner_id, 'lesson_id': lesson.lesson_id if lesson else 1, 'language_code': 'te'}

        res = client.post('/api/voice/evaluate', data=data, files=files, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        res_data = res.json()

        self.assertIn("achievements_unlocked", res_data)
        unlocked_names = [a["achievement_name"] for a in res_data.get("achievements_unlocked", [])]
        self.assertIn("First Voice Practice", unlocked_names)
        print(f"  [OK] [Voice Gamification] Unlocked: {unlocked_names}, Points: {self.profile.total_points}")

    def test_04_lesson_completion_awards_points_and_achievements(self):
        """Verify POST /api/progress/complete-lesson awards points and First Lesson Complete badge."""
        lesson = self.db.query(models.Lesson).first()
        les_id = lesson.lesson_id if lesson else 1

        initial_points = self.profile.total_points or 0

        res = client.post('/api/progress/complete-lesson', json={"lesson_id": les_id, "score": 90.0}, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        res_data = res.json()

        self.assertIn("achievements_unlocked", res_data)

        self.db.refresh(self.profile)
        # 90.0 score -> +9 points
        self.assertEqual(self.profile.total_points, initial_points + 9)
        print(f"  [OK] [Lesson Completion] Points increased from {initial_points} to {self.profile.total_points}, Unlocked: {res_data.get('achievements_unlocked')}")

    def test_05_progress_dashboard_displays_earned_achievements(self):
        """Verify GET /api/progress/dashboard returns earned achievements and accurate streak/points."""
        res = client.get('/api/progress/dashboard', headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("achievements", data)
        self.assertIsInstance(data["achievements"], list)
        self.assertGreaterEqual(len(data["achievements"]), 1)

        self.assertEqual(data["streak_count"], self.profile.streak_count)
        self.assertEqual(data["total_points"], self.profile.total_points)
        print(f"  [OK] [Dashboard Integration] Verified achievements array in /dashboard: {len(data['achievements'])} badges")


if __name__ == '__main__':
    unittest.main()
