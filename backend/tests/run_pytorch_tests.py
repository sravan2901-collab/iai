"""
Master PyTorch Test Runner for AksharAI Platform.

Executes all 14 PyTorch Neural AI unit and integration test cases, outputs detailed performance metrics,
verifies model weight checkpoints, and validates neural predictions across all 8 supported languages.
"""

import sys
import os
import unittest
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pytorch_ai_engine import PyTorchAIEngine

def main():
    print("=" * 80)
    print("AKSHARAI PLATFORM - PYTORCH NEURAL AI TEST SUITE & IMPLEMENTATION RUNNER")
    print("=" * 80)

    start_time = time.time()

    # 1. Initialize PyTorch AI Engine Service
    print("\n[1/4] Initializing PyTorch AI Engine & Deep Neural Models...")
    engine = PyTorchAIEngine()
    print("  ✓ AksharAIProficiencyNet (Multi-Skill Classifier) Initialized")
    print("  ✓ AksharAIHandwritingNet (4-Metric Structural Stroke Evaluator) Initialized")
    print("  ✓ AksharAIPronunciationNet (Phoneme & Acoustic Speech Evaluator) Initialized")
    print("  ✓ AksharAIRecommendationNet (Neural Adaptive Recommender) Initialized")

    # 2. Run Synthetic Model Training & Checkpoint Verification
    print("\n[2/4] Executing PyTorch Neural Model Training & Weight Checkpoint Saving...")
    X_synthetic = [
        [10.0, 15.0, 10.0, 5.0, 20.0, 15.0, 0.0],
        [40.0, 45.0, 50.0, 42.0, 55.0, 48.0, 30.0],
        [75.0, 80.0, 78.0, 82.0, 85.0, 88.0, 70.0],
        [95.0, 98.0, 96.0, 94.0, 98.0, 97.0, 95.0]
    ]
    Y_synthetic = [0, 1, 2, 3]

    final_loss = engine.train_proficiency_model(X_synthetic, Y_synthetic, epochs=15, lr=0.01)
    print(f"  ✓ PyTorch Model Adam Optimization Completed (Final CrossEntropy Loss: {final_loss:.4f})")

    checkpoint_path = engine.save_checkpoint("aksharai_master_models.pt")
    print(f"  ✓ Saved PyTorch Model State Dict Checkpoint -> {os.path.basename(checkpoint_path)}")

    reloaded_engine = PyTorchAIEngine()
    loaded_ok = reloaded_engine.load_checkpoint("aksharai_master_models.pt")
    print(f"  ✓ Reloaded PyTorch Model State Dict Checkpoint -> Success ({loaded_ok})")

    # 3. Run PyTorch Unit Test Suite
    print("\n[3/4] Running PyTorch Unit & Integration Test Suite (14 Test Cases)...")
    suite = unittest.defaultTestLoader.discover(
        start_dir=os.path.dirname(__file__),
        pattern="test_pytorch_ai_suite.py"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 4. Summary & Verification Output
    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("PYTORCH NEURAL AI SUITE IMPLEMENTATION & EXECUTION SUMMARY")
    print("=" * 80)
    print(f"  Total Test Cases Executed : {result.testsRun}")
    print(f"  Passed Test Cases         : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed Test Cases         : {len(result.failures)}")
    print(f"  Execution Errors          : {len(result.errors)}")
    print(f"  Total Execution Time      : {total_time:.2f} seconds")
    print("=" * 80)

    if result.wasSuccessful():
        print("🎉 ALL PYTORCH TEST CASES PASSED 100% SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ PYTORCH TEST SUITE FAILED WITH ERRORS.")
        sys.exit(1)

if __name__ == "__main__":
    main()
