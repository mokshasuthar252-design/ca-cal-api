from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["calculator_db"]

user_collection = db["users"]
history_collection = db["calculator_history"]