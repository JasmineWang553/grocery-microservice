import pytest
from fastapi.testclient import TestClient
from app.main import app, clear_test_data  # Ensure you have a function to reset DB
from bson import ObjectId
from unittest.mock import MagicMock, patch
import datetime 

# Clear pytest cache before running tests
pytest.main(["--cache-clear"])

# Create a TestClient using the FastAPI app defined in your application
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_database():
    """Ensures test database is reset before each test."""
    clear_test_data()  # This should be an endpoint or function in FastAPI that clears test data


@pytest.fixture
def mock_grocery_collection():
    """Mock the MongoDB grocery collection."""
    mock = MagicMock()
    with patch('app.routes.grocery_collection', mock):
        yield mock

def test_is_alive():
    response = client.get("/isAlive")
    assert response.status_code == 200
    assert response.json() == {"message": "Grocery Microservice Running"}

def test_add_item(mock_grocery_collection):
    item_data = {"item_name": "Apple", "quantity": 10}

    # Mock database behavior
    mock_grocery_collection.find_one.return_value = None
    mock_grocery_collection.insert_one.return_value.inserted_id = ObjectId()

    response = client.post("/add_item", json=item_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item added successfully"
    assert "id" in response_data

def test_add_existing_item(mock_grocery_collection):
    """Test that adding an existing item returns 400 Bad Request."""
    item_data = {"item_name": "Banana", "quantity": 5}
    print(f"Mocked Collection: {mock_grocery_collection}")
    # Mocking existing item found
    mock_grocery_collection.find_one.return_value = {
        "_id": ObjectId(),
        "item_name": "Banana"
    }

    response = client.post("/add_item", json=item_data)

    # Debugging: Print response if test fails
    print(f"Response: {response.json()}")

    assert response.status_code == 400, f"Unexpected status code: {response.status_code}"
    assert response.json()["detail"] == "Item already exists in the grocery list"

def test_get_items(mock_grocery_collection):
    """Test retrieving the grocery list with a mocked database."""
    
    # Fix UTC handling
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Mocked grocery item (wrapped in a list)
    item_data = [{
        "_id": ObjectId(),
        "item_name": "Orange",
        "quantity": 20,
        "date": current_time
    }]

    # Fix: Simulate MongoDB cursor behavior with iter()
    mock_grocery_collection.find.return_value = iter(item_data)  

    # Send GET request
    response = client.get("/get_items")

    # Assertions
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    # Fix: Get JSON response correctly
    items = response.json()  

    # Ensure we got exactly 1 item
    assert isinstance(items, list)  # 
    assert len(items) == 1  
    assert items[0]["item_name"] == "Orange"

def test_delete_item(mock_grocery_collection):
    item_name = "Grapes"
    mock_grocery_collection.delete_many.return_value.deleted_count = 1
    
    response = client.delete(f"/delete_item/{item_name}")
    assert response.status_code == 200
    assert response.json() == {"message": "Item deleted successfully"}

def test_delete_nonexistent_item(mock_grocery_collection):
    item_name = "NonExistent"
    mock_grocery_collection.delete_many.return_value.deleted_count = 0
    
    response = client.delete(f"/delete_item/{item_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_update_item_no_fields_to_update():
    """Test that updating with no fields returns 400."""
    item_data = {"item_name": "", "quantity": 0}

    response = client.put("/update_item", json=item_data)

    # Debugging: Print response for troubleshooting
    print(f"Response: {response.status_code}, {response.json()}")

    assert response.status_code == 400, f"Unexpected status code: {response.status_code}"
    assert response.json()["detail"] == "No fields to update"


def test_update_existing_item(mock_grocery_collection):
    item_data = {"item_name": "Lemon", "quantity": 15}
    
    # Simulate that the item exists and can be updated
    mock_grocery_collection.update_one.return_value.matched_count = 1
    
    response = client.put("/update_item", json=item_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Item updated successfully"

def test_insert_instead_of_update(mock_grocery_collection):
    item_data = {"item_name": "New Item", "quantity": 5}
    # Simulate no item was updated, hence inserting instead
    mock_grocery_collection.update_one.return_value.matched_count = 0
    mock_grocery_collection.insert_one.return_value.inserted_id = ObjectId()
    
    response = client.put("/update_item", json=item_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Item not found, inserted instead."

