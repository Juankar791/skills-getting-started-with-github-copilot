import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, test_activities):
        # Arrange
        expected_count = len(test_activities)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_count
        assert "Test Club" in response.json()
        assert "Empty Club" in response.json()
    
    def test_get_activities_returns_correct_structure(self, client, test_activities):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields
    
    def test_get_activities_participants_is_list(self, client, test_activities):
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_data in activities.values():
            assert isinstance(activity_data["participants"], list)


class TestPostSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client, test_activities):
        # Arrange
        activity_name = "Empty Club"
        email = "newstudent@example.com"
        initial_count = len(test_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in test_activities[activity_name]["participants"]
        assert len(test_activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_duplicate_participant_rejected(self, client, test_activities):
        # Arrange
        activity_name = "Test Club"
        email = "test1@example.com"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_with_empty_email_validation(self, client, test_activities):
        # Arrange
        activity_name = "Test Club"
        initial_count = len(test_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email=",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert - App currently accepts empty emails (no validation)
        # Future enhancement: Add email validation to reject empty/invalid emails
        assert response.status_code == 200
        assert len(test_activities[activity_name]["participants"]) == initial_count + 1
        assert "" in test_activities[activity_name]["participants"]


class TestDeleteUnregister:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant_success(self, client, test_activities):
        # Arrange
        activity_name = "Test Club"
        email = "test1@example.com"
        initial_count = len(test_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in test_activities[activity_name]["participants"]
        assert len(test_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_nonexistent_participant_returns_400(self, client, test_activities):
        # Arrange
        activity_name = "Test Club"
        email = "notregistered@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_invalid_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_all_participants_from_activity(self, client, test_activities):
        # Arrange
        activity_name = "Test Club"
        emails = test_activities[activity_name]["participants"].copy()
        
        # Act & Assert for each removal
        for email in emails:
            response = client.delete(
                f"/activities/{activity_name}/unregister?email={email}"
            )
            assert response.status_code == 200
            assert email not in test_activities[activity_name]["participants"]
        
        # Assert all removed
        assert len(test_activities[activity_name]["participants"]) == 0
