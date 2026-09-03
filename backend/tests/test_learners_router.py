"""
AksharAI Learners Router Integration & Security Test Suite
Tests:
1. GET  /api/learners/{learner_id}/proficiency
2. POST /api/learners/{learner_id}/learning-path/generate
3. GET  /api/learners/{learner_id}/learning-path
4. GET  /api/learners/{learner_id}/recommendations

Asserts across all 4 endpoints:
- Authorized 200 OK
- Unauthenticated 401 Unauthorized
- Unauthenticated Non-Existent ID 401 Unauthorized (Anti-Enumeration Guard)
- Cross-Tenant IDOR 403 Forbidden
- Invalid Learner ID 404 Not Found
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import SessionLocal
from app import models
from app.auth import create_access_token
from app.services.learning_path_engine import generate_learning_path, get_active_path


class TestLearnersRouter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Ensure test learner 100 exists
        learner100 = cls.db.query(models.Learner).filter(models.Learner.learner_id == 100).first()
        if not learner100:
            learner100 = models.Learner(learner_id=100, email="test100@akshar.ai", username="test100", password_hash="hash")
            cls.db.add(learner100)
            cls.db.commit()

        # Ensure test learner 200 exists for cross-tenant testing
        learner200 = cls.db.query(models.Learner).filter(models.Learner.learner_id == 200).first()
        if not learner200:
            learner200 = models.Learner(learner_id=200, email="test200@akshar.ai", username="test200", password_hash="hash")
            cls.db.add(learner200)
            cls.db.commit()

        # Ensure an active learning path exists for learner 100
        active_p = get_active_path(100, db=cls.db)
        if not active_p:
            generate_learning_path(100, db=cls.db)

        cls.token100 = create_access_token({"sub": "100", "email": "test100@akshar.ai"})
        cls.auth_headers = {"Authorization": f"Bearer {cls.token100}"}

        cls.token200 = create_access_token({"sub": "200", "email": "test200@akshar.ai"})
        cls.other_headers = {"Authorization": f"Bearer {cls.token200}"}

        cls.valid_learner_id = 100
        cls.invalid_learner_id = 999999

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_get_proficiency(self):
        """Test GET /api/learners/{learner_id}/proficiency across 200, 401, 403, and 404."""
        # 1. Authorized 200
        res = self.client.get(f"/api/learners/{self.valid_learner_id}/proficiency", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # 2. Unauthenticated 401
        res_unauth = self.client.get(f"/api/learners/{self.valid_learner_id}/proficiency")
        self.assertEqual(res_unauth.status_code, 401)

        # 3. Anti-enumeration 401 on non-existent learner ID
        res_unauth_inv = self.client.get(f"/api/learners/{self.invalid_learner_id}/proficiency")
        self.assertEqual(res_unauth_inv.status_code, 401)

        # 4. Cross-tenant IDOR 403
        res_cross = self.client.get(f"/api/learners/{self.valid_learner_id}/proficiency", headers=self.other_headers)
        self.assertEqual(res_cross.status_code, 403)

        # 5. Invalid learner 404
        res_inv = self.client.get(f"/api/learners/{self.invalid_learner_id}/proficiency", headers=self.auth_headers)
        self.assertEqual(res_inv.status_code, 404)

    def test_post_learning_path_generate(self):
        """Test POST /api/learners/{learner_id}/learning-path/generate across 200, 401, 403, and 404."""
        # 1. Authorized 200
        res = self.client.post(f"/api/learners/{self.valid_learner_id}/learning-path/generate", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # 2. Unauthenticated 401
        res_unauth = self.client.post(f"/api/learners/{self.valid_learner_id}/learning-path/generate")
        self.assertEqual(res_unauth.status_code, 401)

        # 3. Anti-enumeration 401 on non-existent learner ID
        res_unauth_inv = self.client.post(f"/api/learners/{self.invalid_learner_id}/learning-path/generate")
        self.assertEqual(res_unauth_inv.status_code, 401)

        # 4. Cross-tenant IDOR 403
        res_cross = self.client.post(f"/api/learners/{self.valid_learner_id}/learning-path/generate", headers=self.other_headers)
        self.assertEqual(res_cross.status_code, 403)

        # 5. Invalid learner 404
        res_inv = self.client.post(f"/api/learners/{self.invalid_learner_id}/learning-path/generate", headers=self.auth_headers)
        self.assertEqual(res_inv.status_code, 404)

    def test_get_learning_path(self):
        """Test GET /api/learners/{learner_id}/learning-path across 200, 401, 403, and 404."""
        # 1. Authorized 200
        res = self.client.get(f"/api/learners/{self.valid_learner_id}/learning-path", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # 2. Unauthenticated 401
        res_unauth = self.client.get(f"/api/learners/{self.valid_learner_id}/learning-path")
        self.assertEqual(res_unauth.status_code, 401)

        # 3. Anti-enumeration 401 on non-existent learner ID
        res_unauth_inv = self.client.get(f"/api/learners/{self.invalid_learner_id}/learning-path")
        self.assertEqual(res_unauth_inv.status_code, 401)

        # 4. Cross-tenant IDOR 403
        res_cross = self.client.get(f"/api/learners/{self.valid_learner_id}/learning-path", headers=self.other_headers)
        self.assertEqual(res_cross.status_code, 403)

        # 5. Invalid learner 404
        res_inv = self.client.get(f"/api/learners/{self.invalid_learner_id}/learning-path", headers=self.auth_headers)
        self.assertEqual(res_inv.status_code, 404)

    def test_get_recommendations(self):
        """Test GET /api/learners/{learner_id}/recommendations across 200, 401, 403, and 404."""
        # 1. Authorized 200
        res = self.client.get(f"/api/learners/{self.valid_learner_id}/recommendations", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # 2. Unauthenticated 401
        res_unauth = self.client.get(f"/api/learners/{self.valid_learner_id}/recommendations")
        self.assertEqual(res_unauth.status_code, 401)

        # 3. Anti-enumeration 401 on non-existent learner ID
        res_unauth_inv = self.client.get(f"/api/learners/{self.invalid_learner_id}/recommendations")
        self.assertEqual(res_unauth_inv.status_code, 401)

        # 4. Cross-tenant IDOR 403
        res_cross = self.client.get(f"/api/learners/{self.valid_learner_id}/recommendations", headers=self.other_headers)
        self.assertEqual(res_cross.status_code, 403)

        # 5. Invalid learner 404
        res_inv = self.client.get(f"/api/learners/{self.invalid_learner_id}/recommendations", headers=self.auth_headers)
        self.assertEqual(res_inv.status_code, 404)


def run_learners_router_test():
    print("=" * 80)
    print("        AKSHARAI LEARNERS REST API ROUTER INTEGRATION & SECURITY TEST")
    print("=" * 80)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestLearnersRouter)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    assert result.wasSuccessful(), "Learners router integration tests failed!"


if __name__ == "__main__":
    run_learners_router_test()
