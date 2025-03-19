from fastapi import APIRouter, HTTPException
from app.database import grocery_collection
from app.models import GroceryItem
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/isAlive")
async def isAlive():
    return {"message":"Grocery Microservice Running"}

@router.post("/add_item", summary="Add a grocery item", response_model=dict)
async def add_item(item: GroceryItem):
    # Check if item already exists (case-insensitive match)
    existing_item = grocery_collection.find_one({"item_name": {"$regex": f"^{item.item_name}$", "$options": "i"}})

    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists in the grocery list")

    item_dict = item.dict()
    item_dict["date"] = datetime.utcnow()
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
    if item_name == None:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = grocery_collection.delete_many({"item_name": item_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted successfully"}

@router.put("/update_item", summary="Update a grocery item", response_model=dict)
async def update_item(item: GroceryItem):
    item_dict = item.dict()
    update_data = {}
    if item_dict["item_name"]:
        update_data["item_name"] = item_dict["item_name"]
    if item_dict["quantity"] is not None:
        update_data["quantity"] = item_dict["quantity"]
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = grocery_collection.update_one(
        {"item_name": item_dict["item_name"]}, {"$set": update_data}
    )

    if result.matched_count == 0:
        inserted_item = grocery_collection.insert_one(item_dict)
        return {"message": "Item not found, inserted instead."}

    return {"message": "Item updated successfully"}