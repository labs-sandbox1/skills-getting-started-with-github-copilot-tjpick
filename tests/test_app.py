"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save initial state
    initial_state = {
        "Basketball Team": {
            "description": "Join our competitive basketball team and represent Mergington High",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "alex@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Develop swimming techniques and participate in swim meets",
            "schedule": "Tuesdays and Thursdays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu", "ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Explore theater arts, acting, and stage production",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["emily@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Express creativity through painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges at regional competitions",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "william@mergington.edu"]
        },
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
    }
    
    # Reset activities
    activities.clear()
    activities.update(initial_state)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Basketball Team" in data
        assert "Swimming Club" in data
        assert len(data) == 9
    
    def test_activities_have_correct_structure(self, client):
        """Test that activities have the correct data structure"""
        response = client.get("/activities")
        data = response.json()
        
        basketball = data["Basketball Team"]
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_success(self, client):
        """Test successful signup"""
        response = client.post(
            "/activities/Basketball Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Basketball Team"]["participants"]
    
    def test_signup_duplicate(self, client):
        """Test that duplicate signup is rejected"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup (duplicate)
        response2 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_existing_participant(self, client):
        """Test that existing participant cannot sign up again"""
        response = client.post(
            "/activities/Basketball Team/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_success(self, client):
        """Test successful unregister"""
        # First, verify participant exists
        activities_before = client.get("/activities").json()
        assert "james@mergington.edu" in activities_before["Basketball Team"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Basketball Team/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "james@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert "james@mergington.edu" not in activities_after["Basketball Team"]["participants"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister when not signed up"""
        response = client.delete(
            "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_after_unregister(self, client):
        """Test that a participant can sign up again after unregistering"""
        email = "james@mergington.edu"
        activity = "Basketball Team"
        
        # Unregister
        response1 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify participant is in the list
        activities_data = client.get("/activities").json()
        assert email in activities_data[activity]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity limits"""
    
    def test_multiple_signups(self, client):
        """Test multiple participants can sign up"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Chess Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_data = client.get("/activities").json()
        chess_participants = activities_data["Chess Club"]["participants"]
        for email in emails:
            assert email in chess_participants
