from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GroceryItem(BaseModel):
    item_name: str
    quantity: int
    date: str | None=None


