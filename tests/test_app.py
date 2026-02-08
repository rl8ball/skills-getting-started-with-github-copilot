import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_contains_activity_details(self, client):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to activity"""
        email = "newstudent@mergington.edu"
        client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Gym Class"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Test signup fails when student already registered"""
        # michael is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test multiple different students can signup"""
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Gym Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Gym Class"]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        email = "michael@mergington.edu"
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_student(self, client):
        """Test unregister fails when student not signed up"""
        response = client.delete(
            "/activities/Gym Class/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
