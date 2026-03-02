"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    yield
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_has_correct_structure(self, client):
        """Test that activity structure is correct"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """Test that participants are included in response"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_adds_participant(self, client):
        """Test that a new participant is added"""
        email = "alice@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]

    def test_signup_actually_adds_to_list(self, client):
        """Test that participant is actually added to the activity"""
        email = "alice@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert len(activities_data["Chess Club"]["participants"]) == 3

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_participants(self, client):
        """Test adding multiple different participants"""
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        for email in emails:
            client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        for email in emails:
            assert email in activities_data["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes a participant"""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_actually_removes_from_list(self, client):
        """Test that participant is actually removed"""
        email = "michael@mergington.edu"
        client.post(f"/activities/Chess%20Club/unregister?email={email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        assert email not in activities_data["Chess Club"]["participants"]
        assert len(activities_data["Chess Club"]["participants"]) == 1

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_participant(self, client):
        """Test unregister for participant not in activity returns 404"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_twice_fails(self, client):
        """Test that unregistering twice fails the second time"""
        email = "michael@mergington.edu"
        
        # First unregister succeeds
        response1 = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response2.status_code == 404


class TestIntegration:
    """Integration tests for signup and unregister flows"""

    def test_signup_then_unregister_flow(self, client):
        """Test complete signup and unregister flow"""
        email = "newstudent@mergington.edu"
        activity = "Programming%20Class"
        
        # Initial check - not registered
        response = client.get("/activities")
        assert email not in response.json()["Programming Class"]["participants"]
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Check registered
        response = client.get("/activities")
        assert email in response.json()["Programming Class"]["participants"]
        
        # Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Check unregistered
        response = client.get("/activities")
        assert email not in response.json()["Programming Class"]["participants"]

    def test_multiple_activities_independence(self, client):
        """Test that activities are independent"""
        email = "test@mergington.edu"
        
        # Sign up for Chess Club
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Verify only in Chess Club
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email not in data["Programming Class"]["participants"]
        assert email not in data["Gym Class"]["participants"]
