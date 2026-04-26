from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities_response = client.get("/activities").json()
    assert email in activities_response[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    first_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    activity_name = "Programming Class"
    email = "removeme@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    delete_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": f"Removed {email} from {activity_name}"}

    activities_response = client.get("/activities").json()
    assert email not in activities_response[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    activity_name = "Chess Club"
    email = "notfound@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
