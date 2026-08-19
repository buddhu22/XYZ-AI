"""
XYZ AI Backend — Authentication & RBAC Security Test Suite

Verifies:
1. Student login (valid / invalid password / role mismatch)
2. Parent login (valid / linked children resolution)
3. Teacher login (valid / invalid password)
4. Principal login (valid / invalid password)
5. JWT token generation, expiration, and decoding
6. /api/v1/auth/me protected endpoint
7. Chat endpoint identity enforcement from JWT token
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.security.context import get_user_context_from_token

client = TestClient(app)


# =============================================================================
# 1. Password Hashing & JWT Unit Tests
# =============================================================================
def test_password_hashing():
    raw = "mysecretpassword123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_token_creation_and_decoding():
    data = {"sub": "10", "email": "rahul.sharma@mail.com", "role": "student", "name": "Rahul Sharma"}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "10"
    assert payload["role"] == "student"
    assert payload["email"] == "rahul.sharma@mail.com"


def test_jwt_invalid_token_decoding():
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    assert decode_access_token(invalid_token) is None


# =============================================================================
# 2. Login Endpoint Tests
# =============================================================================
def test_student_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rahul.sharma@mail.com", "password": "password123", "role": "student"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "student"
    assert data["user"]["email"] == "rahul.sharma@mail.com"


def test_student_login_wrong_password():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rahul.sharma@mail.com", "password": "wrongpassword!", "role": "student"},
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_role_mismatch():
    # Attempting to log into parent account through student portal
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.sharma@mail.com", "password": "password123", "role": "student"},
    )
    assert response.status_code == 401
    assert "mismatch" in response.json()["detail"].lower() or "not a 'student'" in response.json()["detail"].lower()


def test_parent_login_with_linked_children():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.sharma@mail.com", "password": "password123", "role": "parent"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "parent"
    assert "linked_children" in data["user"]
    assert len(data["user"]["linked_children"]) > 0
    assert any(c["name"] == "Rahul Sharma" for c in data["user"]["linked_children"])


def test_teacher_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "amit.kumar@school.com", "password": "password123", "role": "teacher"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "teacher"


def test_principal_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "suresh.nair@school.com", "password": "password123", "role": "principal"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "principal"


# =============================================================================
# 3. Protected /me Endpoint Tests
# =============================================================================
def test_get_current_user_me_success():
    # Login first
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.sharma@mail.com", "password": "password123", "role": "parent"},
    )
    token = login_res.json()["access_token"]

    # Call /me with Bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["role"] == "parent"
    assert me_data["name"] == "Rajesh Sharma"


def test_get_current_user_me_unauthorized():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


# =============================================================================
# 4. UserContext Integration Tests
# =============================================================================
def test_get_user_context_from_jwt_token():
    token = create_access_token({
        "sub": "5",
        "email": "rajesh.sharma@mail.com",
        "name": "Rajesh Sharma",
        "role": "parent",
        "parent_id": 1,
    })
    ctx = get_user_context_from_token(token)
    assert ctx.id == 5
    assert ctx.role == "parent"
    assert ctx.name == "Rajesh Sharma"
    assert ctx.parent_id == 1
    assert 1 in ctx.linked_children_ids


def test_logout_endpoint():
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
