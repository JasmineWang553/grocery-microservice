from fastapi import APIRouter, HTTPException
from app.database import grocery_collection
from app.models import GroceryItem
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

@router.get("/isAlive")
async def isAlive():
    # 
    return {"message": "Grocery Microservice Running"}

@router.post("/add_item", summary="Add a grocery item", response_model=dict)
async def add_item(item: GroceryItem):
    # Validate input
    if not item.item_name or item.item_name.strip() == "":
        raise HTTPException(status_code=400, detail="Item name cannot be empty or null")
    if item.quantity is None:
        raise HTTPException(status_code=400, detail="Quantity cannot be empty or null")

    # Check if item already exists (case-insensitive match)
    existing_item = grocery_collection.find_one({"item_name": {"$regex": f"^{item.item_name}$", "$options": "i"}})

    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists in the grocery list")

    item_dict = item.model_dump()
    item_dict["date"] = datetime.utcnow().replace(tzinfo=timezone.utc)
    inserted_item = grocery_collection.insert_one(item_dict)
    return {"message": "Item added successfully", "id": str(inserted_item.inserted_id)}

@router.get("/get_items", summary="Get all grocery items", response_model=list)
async def get_items():
    items = list(grocery_collection.find({}, {"_id": 1, "item_name": 1, "quantity": 1, "date": 1}))
    for item in items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
    return items

@router.delete("/delete_item/{item_name}", summary="Delete a grocery item", response_model=dict)
async def delete_item(item_name: str):
    if item_name is None:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = grocery_collection.delete_many({"item_name": item_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted successfully"}

@router.put("/update_item", summary="Update an existing grocery item", response_model=dict)
async def update_item(item: GroceryItem):
    """Update an item in the grocery list."""
    # Ensure there are fields to update
    if item.item_name is None or item.quantity is None or len(item.item_name) == 0:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Perform update operation
    result = grocery_collection.update_one(
        {"item_name": item.item_name},
        {"$set": {"quantity": item.quantity}}
    )

    if result.matched_count == 0:
        return {"message": "Item not found, inserted instead."}

    return {"message": "Item updated successfully"}