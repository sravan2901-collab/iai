# -*- coding: utf-8 -*-
"""
conftest.py — Shared fixtures for AksharAI test suite.
Provides TestClient, test user registration/login, and auth headers.
"""

import sys
import os
import pytest
import uuid

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient for the entire test session."""
    return TestClient(app)


@pytest.fixture(scope="session")
def test_user_credentials():
    """Unique test user credentials for this session."""
    uid = uuid.uuid4().hex[:8]
    return {
        "email": f"pytest_{uid}@test.com",
        "username": f"pytest_{uid}",
        "password": "TestPass123!",
        "first_name": "Pytest User",
        "native_lang_id": 2  # English
    }


@pytest.fixture(scope="session")
def registered_user(client, test_user_credentials):
    """Register the test user. Returns the response data."""
    resp = client.post("/api/auth/register", json=test_user_credentials)
    assert resp.status_code == 200, f"Registration failed: {resp.text}"
    return resp.json()


@pytest.fixture(scope="session")
def auth_token(client, test_user_credentials, registered_user):
    """Login and return a valid JWT token."""
    resp = client.post("/api/auth/login", json={
        "email": test_user_credentials["email"],
        "password": test_user_credentials["password"]
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Authorization headers dict for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}
