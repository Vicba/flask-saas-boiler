from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId  # Import ObjectId
import os

client = MongoClient(os.getenv("MONGODB_URI"))
db = client['ai_saas']

class User:
    @staticmethod
    def register(email, password):
        if db.users.find_one({"email": email}):
            return None
        hashed_password = generate_password_hash(password)
        user_id = db.users.insert_one({
            "email": email,
            "password": hashed_password,
            "credits": 10  # Initial credits
        }).inserted_id
        return db.users.find_one({"_id": user_id})

    @staticmethod
    def authenticate(email, password):
        user = db.users.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            return user
        return None

    @staticmethod
    def get_by_id(user_id):
        try:
            return db.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            return None  # Handle any errors (e.g., invalid ObjectId format)

    @staticmethod
    def update_credits(user_id, credits):
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'credits': credits}}
        )
        
        if result.modified_count > 0:
            updated_user = db.users.find_one({'_id': ObjectId(user_id)})
            return updated_user['credits'] if updated_user else None
        return None

    @staticmethod
    def update_stripe_customer_id(user_id, stripe_customer_id):
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"stripe_customer_id": stripe_customer_id}}
        )