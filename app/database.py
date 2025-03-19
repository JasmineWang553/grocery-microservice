from pymongo import MongoClient
from app.config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
grocery_collection = db[COLLECTION_NAME]
