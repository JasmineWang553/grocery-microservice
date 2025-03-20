from fastapi import FastAPI
from app.routes import router
from app.database import grocery_collection  # Make sure this is your DB collection

app = FastAPI(title="Grocery List API", description="FastAPI MongoDB Example", version="1.0.0")

app.include_router(router)

def clear_test_data():
    """Clears all items from the database to ensure a fresh state for tests."""
    grocery_collection.delete_many({})