from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]
    assert email in participants


def test_duplicate_signup_returns_400():
    activity_name = "Chess Club"
    email = "duplicate_student@mergington.edu"

    first_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    activity_name = "Programming Class"
    email = "remove_student@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    delete_response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"

    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]
    assert email not in participants


def test_remove_missing_participant_returns_404():
    activity_name = "Gym Class"
    email = "not_signed_up@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
