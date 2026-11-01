import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
INITIAL = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory data before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL))


def test_root_redirects_to_index():
    # Arrange / Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities_returns_all():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_twice_is_rejected():
    # Arrange
    email = "twice@mergington.edu"
    client.post("/activities/Chess Club/signup", params={"email": email})

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_unknown_activity_returns_404():
    # Act
    response = client.post(
        "/activities/Unknown/signup", params={"email": "a@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant():
    # Arrange
    email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_signed_up_returns_400():
    # Act
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "nobody@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400


def test_unregister_unknown_activity_returns_404():
    # Act
    response = client.delete(
        "/activities/Unknown/unregister", params={"email": "a@x.edu"}
    )

    # Assert
    assert response.status_code == 404
