import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId  # Import ObjectId

client = MongoClient(os.getenv("MONGODB_URI"))
db = client['ai_saas']

class User:
    @staticmethod
    def register(email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None, google_id: Optional[str] = None):
        if db.users.find_one({"email": email}):
            return None
        hashed_password = generate_password_hash(password)
        user_id = db.users.insert_one({
            "email": email,
            "password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "credits": 10,  # Initial credits
            "created_at": datetime.now(timezone.utc),
            "last_login": None,
            "is_active": True,
            "role": "user",
            "google_id": google_id,
            "preferences": {}
        }).inserted_id
        return db.users.find_one({"_id": user_id})
    
    @staticmethod
    def register_google(email: str, google_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
        if db.users.find_one({"email": email}):
            return None
        user_id = db.users.insert_one({
            "email": email,
            "password": None,
            "first_name": first_name,
            "last_name": last_name,
            "credits": 10,  # Initial credits
            "created_at": datetime.now(timezone.utc),
            "last_login": None,
            "is_active": True,
            "role": "user",
            "google_id": google_id,
            "preferences": {}
        }).inserted_id
        return db.users.find_one({"_id": user_id})

    @staticmethod
    def authenticate(email: str, password: str):
        user = db.users.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            return user
        return None

    @staticmethod
    def get_by_id(user_id: str):
        try:
            return db.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            return None  # Handle any errors (e.g., invalid ObjectId format)

    @staticmethod
    def get_by_email(email: str):
        try:
            return db.users.find_one({"email": email})
        except Exception as e:
            return None 

    @staticmethod
    def update_credits(user_id: str, credits: int):
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$inc': {'credits': credits}}
        )
        
        if result.modified_count > 0:
            updated_user = db.users.find_one({'_id': ObjectId(user_id)})
            return updated_user['credits'] if updated_user else None
        return None

    @staticmethod
    def update_stripe_customer_id(user_id: str, stripe_customer_id: str):
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"stripe_customer_id": stripe_customer_id}}
        )
        
    @staticmethod
    def update_profile(user_id: str, update_data: Dict[str, Any]):
        allowed_fields = ["first_name", "last_name", "email", "preferences", "last_login"]
        update_dict = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            return db.users.find_one({"_id": ObjectId(user_id)})
        return None

    @staticmethod
    def change_role(user_id: str, new_role: str):
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": new_role}}
        )
        
        if result.modified_count > 0:
            return db.users.find_one({"_id": ObjectId(user_id)})
        return None

    @staticmethod
    def deactivate_account(user_id: str):
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )
        
        if result.modified_count > 0:
            return True
        return False
    