import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def test_activities():
    """Fixture with fresh test activities for each test"""
    test_data = {
        "Test Club": {
            "description": "A test activity",
            "schedule": "Monday, 3:00 PM",
            "max_participants": 5,
            "participants": ["test1@example.com", "test2@example.com"]
        },
        "Empty Club": {
            "description": "An empty activity",
            "schedule": "Friday, 4:00 PM",
            "max_participants": 3,
            "participants": []
        }
    }
    
    # Store original state
    original = dict(activities)
    
    # Replace with test data
    activities.clear()
    activities.update(test_data)
    
    yield test_data
    
    # Restore original state
    activities.clear()
    activities.update(original)
