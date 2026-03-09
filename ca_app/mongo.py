from pymongo import MongoClient

client = MongoClient("mongodb+srv://mokshasuthar252_db_user:7CTQSOZZPEv7zaus@cluster0.ahzyhcp.mongodb.net/?appName=Cluster0")
db = client["calculator_db"]

user_collection = db["users"]
history_collection = db["calculator_history"]