"""
AI Learning Path Generation Verification Test Suite
Tests:
1. Verify learning_path_engine.generate_learning_path() when Ollama / AI is available.
2. Ensure json.dumps() serialization of phonetic_script executes without NameError.
3. Ensure AI generated lessons are committed and populated in the database.
"""
import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base, engine, SessionLocal
from app import models
from app.services.learning_path_engine import generate_learning_path


class TestAILearningPathGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

        # Create or fetch test learner
        cls.learner = cls.db.query(models.Learner).filter(models.Learner.email == "ai_lp_tester@aksharai.org").first()
        if not cls.learner:
            cls.learner = models.Learner(
                email="ai_lp_tester@aksharai.org",
                username="ai_lp_tester",
                password_hash="test_hash"
            )
            cls.db.add(cls.learner)
            cls.db.commit()
            cls.db.refresh(cls.learner)

        cls.profile = cls.db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == cls.learner.learner_id).first()
        if not cls.profile:
            cls.profile = models.LearnerProfile(
                learner_id=cls.learner.learner_id,
                first_name="AILP",
                last_name="Tester",
                literacy_level="FOUNDATIONAL",
                reading_pct=30.0,
                comprehension_pct=60.0,
                voice_pct=70.0
            )
            cls.db.add(cls.profile)
            cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @patch("app.services.learning_path_engine.is_ai_available")
    @patch("app.services.learning_path_engine.generate_path_plan")
    @patch("app.services.learning_path_engine.generate_lesson_content")
    def test_ai_learning_path_generation_with_ollama(
        self, mock_gen_content, mock_gen_plan, mock_ai_avail
    ):
        """Simulate Ollama AI availability and ensure no NameError on json.dumps or AI lesson generation."""
        mock_ai_avail.return_value = True
        mock_gen_plan.return_value = [
            {"title": "AI Phonics Vowel Identification", "difficulty_level": "FOUNDATIONAL"},
            {"title": "AI Two-Letter Word Blends", "difficulty_level": "FOUNDATIONAL"}
        ]
        mock_gen_content.return_value = {
            "title": "AI Phonics Vowel Identification",
            "content_url": "/audio/en/ai_vowels.mp3",
            "target_text": "A, E, I, O, U are vowel sounds.",
            "phonetic_script": ["A", "E", "I", "O", "U"],
            "difficulty_level": "FOUNDATIONAL"
        }

        path_id = generate_learning_path(
            learner_id=self.learner.learner_id,
            target_lang="en",
            db=self.db
        )

        self.assertIsInstance(path_id, int)
        path = self.db.query(models.LearningPath).filter(models.LearningPath.path_id == path_id).first()
        self.assertIsNotNone(path)

        path_lessons = self.db.query(models.PathLesson).filter(models.PathLesson.path_id == path_id).all()
        self.assertGreaterEqual(len(path_lessons), 1)

        # Check that lesson phonetic_script was cleanly serialized as valid JSON
        first_lesson = self.db.query(models.Lesson).filter(models.Lesson.lesson_id == path_lessons[0].lesson_id).first()
        self.assertIsNotNone(first_lesson)
        self.assertIn("AI Phonics", first_lesson.title)
        self.assertIn("[", first_lesson.phonetic_script)
        self.assertIn("]", first_lesson.phonetic_script)

        print(f"  [OK] [AI Learning Path Engine] Generated path #{path_id} with AI lesson: '{first_lesson.title}' (phonetic_script: {first_lesson.phonetic_script})")


if __name__ == '__main__':
    unittest.main()
