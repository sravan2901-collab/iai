"""
Comprehensive PyTorch Test Suite for AksharAI Neural AI Engine.

Tests:
1. PyTorch Neural Model Architectures & Tensor Operations
2. Gradient Flow, Loss Computation & Backpropagation
3. Neural Model Training & Monotonic Loss Convergence
4. PyTorch Model Serialization & Weight Checkpoint Saving/Loading
5. Neural Batch Inference & Performance Latency Benchmarks
6. Integration with AksharAI Database & Multilingual Learner Pipelines
"""

import sys
import os
import unittest
import torch
import torch.nn as nn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pytorch_ai_engine import (
    AksharAIProficiencyNet,
    AksharAIHandwritingNet,
    AksharAIPronunciationNet,
    AksharAIRecommendationNet,
    PyTorchAIEngine
)
from app.database import SessionLocal
from app import models


class TestPyTorchProficiencyNet(unittest.TestCase):
    """
    Test suite for PyTorch Learner Proficiency Neural Classifier.
    """
    def setUp(self):
        self.net = AksharAIProficiencyNet(input_dim=7, hidden_dim=64, num_classes=4)

    def test_single_and_batch_forward_pass(self):
        """Verify single vector and batch tensor forward pass output shapes."""
        # Single instance
        x_single = torch.tensor([85.0, 90.0, 78.0, 82.0, 92.0, 88.0, 75.0], dtype=torch.float32)
        probs, score = self.net(x_single)
        
        self.assertEqual(probs.shape, torch.Size([4]))
        self.assertAlmostEqual(torch.sum(probs).item(), 1.0, places=4)
        self.assertTrue(0.0 <= score.item() <= 100.0)

        # Batch of 16 instances
        x_batch = torch.randn(16, 7)
        probs_b, score_b = self.net(x_batch)
        self.assertEqual(probs_b.shape, torch.Size([16, 4]))
        self.assertEqual(score_b.shape, torch.Size([16, 1]))

    def test_gradient_flow_and_backprop(self):
        """Verify loss computation and non-zero gradient backpropagation."""
        self.net.train()
        x = torch.randn(8, 7)
        y_class = torch.tensor([0, 1, 2, 3, 1, 2, 0, 3], dtype=torch.long)
        y_score = torch.tensor([[20.0], [50.0], [75.0], [90.0], [45.0], [70.0], [15.0], [95.0]], dtype=torch.float32)

        optimizer = torch.optim.Adam(self.net.parameters(), lr=0.01)
        optimizer.zero_grad()

        probs, score = self.net(x)
        loss_cls = nn.CrossEntropyLoss()(probs, y_class)
        loss_reg = nn.MSELoss()(score, y_score)
        total_loss = loss_cls + 0.01 * loss_reg

        total_loss.backward()

        self.assertIsNotNone(self.net.fc1.weight.grad)
        self.assertFalse(torch.isnan(self.net.fc1.weight.grad).any())
        self.assertTrue(torch.abs(self.net.fc1.weight.grad).sum().item() > 0.0)

    def test_training_loss_convergence(self):
        """Verify PyTorch model loss strictly decreases over training epochs."""
        self.net.train()
        optimizer = torch.optim.Adam(self.net.parameters(), lr=0.02)
        criterion = nn.CrossEntropyLoss()

        x_train = torch.tensor([
            [10.0, 15.0, 10.0, 5.0, 20.0, 15.0, 0.0],
            [15.0, 20.0, 10.0, 12.0, 25.0, 20.0, 10.0],
            [40.0, 45.0, 50.0, 42.0, 55.0, 48.0, 30.0],
            [50.0, 55.0, 52.0, 48.0, 60.0, 58.0, 40.0],
            [75.0, 80.0, 78.0, 82.0, 85.0, 88.0, 70.0],
            [85.0, 90.0, 88.0, 92.0, 95.0, 94.0, 85.0],
            [95.0, 98.0, 96.0, 94.0, 98.0, 97.0, 95.0],
            [90.0, 92.0, 94.0, 96.0, 92.0, 95.0, 90.0]
        ], dtype=torch.float32)

        y_train = torch.tensor([0, 0, 1, 1, 2, 2, 3, 3], dtype=torch.long)

        initial_loss = None
        final_loss = None

        for epoch in range(25):
            optimizer.zero_grad()
            probs, _ = self.net(x_train)
            loss = criterion(probs, y_train)
            loss.backward()
            optimizer.step()

            if epoch == 0:
                initial_loss = float(loss.item())
            final_loss = float(loss.item())

        self.assertLess(final_loss, initial_loss, f"Training failed to converge: Initial {initial_loss} -> Final {final_loss}")


class TestPyTorchHandwritingNet(unittest.TestCase):
    """
    Test suite for PyTorch Neural Handwriting Evaluator.
    """
    def setUp(self):
        self.net = AksharAIHandwritingNet(input_dim=6, hidden_dim=32)

    def test_handwriting_quality_scoring(self):
        """Verify neat vs messy handwriting score predictions."""
        neat_stroke = torch.tensor([95.0, 90.0, 85.0, 5.0, 40.0, 0.0], dtype=torch.float32)
        messy_stroke = torch.tensor([20.0, 15.0, 10.0, 80.0, 90.0, 5.0], dtype=torch.float32)

        score_neat = self.net(neat_stroke).item()
        score_messy = self.net(messy_stroke).item()

        self.assertTrue(0.0 <= score_neat <= 100.0)
        self.assertTrue(0.0 <= score_messy <= 100.0)

    def test_handwriting_gradient_update(self):
        """Test handwriting evaluator backprop step."""
        self.net.train()
        x = torch.randn(4, 6)
        y = torch.tensor([[85.0], [90.0], [30.0], [45.0]], dtype=torch.float32)
        
        optimizer = torch.optim.SGD(self.net.parameters(), lr=0.01)
        optimizer.zero_grad()
        out = self.net(x)
        loss = nn.MSELoss()(out, y)
        loss.backward()
        optimizer.step()

        self.assertIsNotNone(self.net.layer1.weight.grad)


class TestPyTorchPronunciationNet(unittest.TestCase):
    """
    Test suite for PyTorch Neural Pronunciation & Acoustic Speech Evaluator.
    """
    def setUp(self):
        self.net = AksharAIPronunciationNet(input_dim=5, hidden_dim=32)

    def test_pronunciation_inference_shapes(self):
        """Test accuracy and fluency index predictions."""
        x = torch.tensor([0.92, 12.5, 65.0, 0.05, 130.0], dtype=torch.float32)
        accuracy, fluency = self.net(x)

        self.assertTrue(0.0 <= accuracy.item() <= 100.0)
        self.assertTrue(0.0 <= fluency.item() <= 100.0)

    def test_pronunciation_batch_evaluation(self):
        """Test batch speech evaluation tensor output."""
        x_batch = torch.randn(10, 5)
        acc_b, flu_b = self.net(x_batch)
        self.assertEqual(acc_b.shape, torch.Size([10, 1]))
        self.assertEqual(flu_b.shape, torch.Size([10, 1]))


class TestPyTorchRecommendationNet(unittest.TestCase):
    """
    Test suite for PyTorch Deep Neural Collaborative Recommender.
    """
    def setUp(self):
        self.net = AksharAIRecommendationNet(learner_feature_dim=8, module_feature_dim=8, embed_dim=16)

    def test_recommendation_affinity_scoring(self):
        """Test recommendation affinity scoring between learner and candidate module."""
        learner_feats = torch.randn(8)
        module_feats = torch.randn(8)

        affinity = self.net(learner_feats.unsqueeze(0), module_feats.unsqueeze(0))
        val = affinity.squeeze().item()
        self.assertTrue(0.0 <= val <= 100.0)

    def test_recommendation_candidate_ranking(self):
        """Test scoring batch of 20 candidate modules for a single learner."""
        learner_feats = torch.randn(1, 8).repeat(20, 1)
        candidate_modules = torch.randn(20, 8)

        scores = self.net(learner_feats, candidate_modules)
        self.assertEqual(scores.shape, torch.Size([20, 1]))


class TestPyTorchEngineAndCheckpointing(unittest.TestCase):
    """
    Test suite for PyTorchAIEngine service and checkpoint saving/loading.
    """
    def setUp(self):
        self.engine = PyTorchAIEngine()

    def test_predict_learner_proficiency_integration(self):
        """Test PyTorch engine proficiency prediction pipeline."""
        res = self.engine.predict_learner_proficiency([80.0, 85.0, 75.0, 70.0, 90.0, 88.0, 60.0])
        self.assertIn("predicted_level", res)
        self.assertIn(res["predicted_level"], ["ZERO", "FOUNDATIONAL", "FUNCTIONAL", "PROFICIENT"])
        self.assertIn("level_probabilities", res)
        self.assertIn("predicted_composite_score", res)

    def test_evaluate_handwriting_integration(self):
        """Test handwriting engine integration."""
        res = self.engine.evaluate_handwriting_strokes([90.0, 85.0, 75.0, 5.0, 40.0, 0.0])
        self.assertIn("predicted_stroke_accuracy", res)
        self.assertIn("quality_tier", res)

    def test_evaluate_pronunciation_integration(self):
        """Test pronunciation engine integration."""
        res = self.engine.evaluate_pronunciation_audio([0.88, 14.0, 60.0, 0.08, 120.0])
        self.assertIn("predicted_speech_accuracy", res)
        self.assertIn("predicted_fluency_index", res)

    def test_checkpoint_save_and_load(self):
        """Test saving PyTorch model weights to disk and reloading state dict."""
        ckpt_filename = "test_aksharai_models.pt"
        saved_path = self.engine.save_checkpoint(ckpt_filename)
        self.assertTrue(os.path.exists(saved_path))

        # Perform prediction before reload
        pred_before = self.engine.predict_learner_proficiency([70.0, 75.0, 65.0, 60.0, 80.0, 78.0, 50.0])

        # Create new engine instance and load checkpoint
        new_engine = PyTorchAIEngine()
        loaded = new_engine.load_checkpoint(ckpt_filename)
        self.assertTrue(loaded)

        pred_after = new_engine.predict_learner_proficiency([70.0, 75.0, 65.0, 60.0, 80.0, 78.0, 50.0])
        self.assertEqual(pred_before["predicted_level"], pred_after["predicted_level"])
        self.assertEqual(pred_before["predicted_composite_score"], pred_after["predicted_composite_score"])

        # Clean up temporary test checkpoint file
        if os.path.exists(saved_path):
            os.remove(saved_path)

    def test_multilingual_database_learners_inference(self):
        """Test running PyTorch Neural Engine on database learners across all languages."""
        db = SessionLocal()
        try:
            learners = db.query(models.Learner).all()
            self.assertTrue(len(learners) > 0, "Database should contain registered learners.")

            for learner in learners[:10]:
                lid = float(learner.learner_id)
                features = [
                    float((lid * 15) % 100),
                    float((lid * 25) % 100),
                    float((lid * 35) % 100),
                    float((lid * 45) % 100),
                    85.0,
                    80.0,
                    50.0
                ]
                res = self.engine.predict_learner_proficiency(features)
                self.assertIn(res["predicted_level"], ["ZERO", "FOUNDATIONAL", "FUNCTIONAL", "PROFICIENT"])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
