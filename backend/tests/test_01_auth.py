# -*- coding: utf-8 -*-
"""
Test Suite 1: Authentication — Registration, Login, Profile, Token Validation
"""
import uuid


class TestRegistration:
    """Test user registration flow."""

    def test_register_success(self, client):
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/api/auth/register", json={
            "email": f"reg_{uid}@test.com",
            "username": f"reg_{uid}",
            "password": "ValidPass1!",
            "first_name": "Reg Tester",
            "native_lang_id": 2
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "learner_id" in data or "access_token" in data or "message" in data

    def test_register_duplicate_email(self, client, test_user_credentials, registered_user):
        resp = client.post("/api/auth/register", json=test_user_credentials)
        assert resp.status_code == 400
        assert "already" in resp.json().get("detail", "").lower() or resp.status_code == 400

    def test_register_missing_email(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "noEmail",
            "password": "Pass123!",
            "first_name": "No Email"
        })
        assert resp.status_code in [400, 422]

    def test_register_weak_password(self, client):
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/api/auth/register", json={
            "email": f"weak_{uid}@test.com",
            "username": f"weak_{uid}",
            "password": "123",
            "first_name": "Weak Pass"
        })
        # Should reject weak passwords
        assert resp.status_code in [400, 422]


class TestLogin:
    """Test login flow."""

    def test_login_success(self, client, test_user_credentials, registered_user):
        resp = client.post("/api/auth/login", json={
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user_credentials, registered_user):
        resp = client.post("/api/auth/login", json={
            "email": test_user_credentials["email"],
            "password": "WrongPassword999!"
        })
        assert resp.status_code in [400, 401]

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "nonexistent@nobody.com",
            "password": "AnyPass123!"
        })
        assert resp.status_code in [400, 401, 404]


class TestTokenAuth:
    """Test protected endpoints require valid auth."""

    def test_protected_without_token(self, client):
        resp = client.get("/api/recommendations")
        assert resp.status_code == 401

    def test_protected_with_invalid_token(self, client):
        resp = client.get("/api/recommendations", headers={
            "Authorization": "Bearer invalid_garbage_token"
        })
        assert resp.status_code == 401

    def test_protected_with_valid_token(self, client, auth_headers):
        resp = client.get("/api/recommendations", headers=auth_headers)
        assert resp.status_code == 200


class TestProfile:
    """Test profile retrieval."""

    def test_get_profile(self, client, auth_headers):
        resp = client.get("/api/learners/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "email" in data or "learner_id" in data or "first_name" in data
