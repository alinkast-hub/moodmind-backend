"""Smoke tests for the MoodMind backend API.

Requires the server running locally (`python app.py`) with JWT_SECRET_KEY set.
"""
import random
import string

import requests

BASE_URL = "http://localhost:5000"


def random_username():
    return "testuser_" + "".join(random.choices(string.ascii_lowercase, k=8))


def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    print("health check passed")


def test_register_and_login():
    username = random_username()
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "securepassword123",
    }
    resp = requests.post(f"{BASE_URL}/register", json=payload)
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    print("registration passed")

    resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": "securepassword123"},
    )
    assert resp.status_code == 200, resp.text
    print("login passed")
    return token


def test_journal_flow(token):
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post(
        f"{BASE_URL}/journal",
        headers=headers,
        json={"text": "Today was a great day! I feel happy.", "mood_score": 8},
    )
    assert resp.status_code == 201, resp.text
    print("journal entry creation passed")

    resp = requests.get(f"{BASE_URL}/journal/history", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["pagination"]["total"] >= 1
    print("journal history passed")


def test_analyze(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{BASE_URL}/analyze",
        headers=headers,
        json={"text": "I feel anxious about tomorrow.", "mood_score": 3},
    )
    assert resp.status_code == 200, resp.text
    print("analyze passed")


def test_mood_stats(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/mood/stats", headers=headers)
    assert resp.status_code == 200, resp.text
    print("mood stats passed")


def test_subscription_check(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/subscription/check", headers=headers)
    assert resp.status_code == 200, resp.text
    print("subscription check passed")


def test_user_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    assert resp.status_code == 200, resp.text
    print("user profile passed")


if __name__ == "__main__":
    test_health()
    token = test_register_and_login()
    test_journal_flow(token)
    test_analyze(token)
    test_mood_stats(token)
    test_subscription_check(token)
    test_user_profile(token)
    print("\nAll tests passed.")
