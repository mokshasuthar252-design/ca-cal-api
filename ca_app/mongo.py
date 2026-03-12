from pymongo import MongoClient

client = MongoClient("mongodb+srv://moksha:moksha252@cluster0.ahzyhcp.mongodb.net/?appName=Cluster0")

db = client["calculator_db"]

user_collection = db["users"]
history_collection = db["calculator_history"]

