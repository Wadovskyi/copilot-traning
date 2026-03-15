import copy
import pytest
from fastapi.testclient import TestClient
from app import app, activities as activities_store

_ORIGINAL_ACTIVITIES = copy.deepcopy(activities_store)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity data before each test."""
    activities_store.clear()
    activities_store.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == len(_ORIGINAL_ACTIVITIES)


def test_get_activities_shape():
    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities_store[activity_name]["participants"]


def test_signup_unknown_activity():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown Activity/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_signup_already_registered():
    # Arrange
    activity_name = "Chess Club"
    email = activities_store[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    email = activities_store[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities_store[activity_name]["participants"]


def test_unregister_unknown_activity():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/Unknown Activity/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_unregister_not_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "not_enrolled@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]
