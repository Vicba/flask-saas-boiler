import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union, Tuple
from pymongo import MongoClient, IndexModel, ASCENDING
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

client = MongoClient(os.getenv("MONGODB_URI"))
db = client['ai_saas']

class User:
    @staticmethod
    def register(email: str, google_id: Optional[str] = None, password: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None):
        if db.users.find_one({"email": email}):
            return None
        
        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "credits": 10,
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc),
            "is_active": True,
            "role": "user",
            "preferences": {},
            "google_id": google_id,
            "password": generate_password_hash(password) if password else None
        }

        if not (google_id or password):
            return None  # Either google_id or password must be provided

        user_id = db.users.insert_one(user_data).inserted_id
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
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return user
        except Exception as e:
            current_app.logger.error(f"Error getting user by ID: {str(e)}")
            return None

    @staticmethod
    def get_by_email(email: str):
        try:
            return db.users.find_one({"email": email}, projection={"password": 0})
        except Exception as e:
            current_app.logger.error(f"Error getting user by email: {str(e)}")
            return None 

    @staticmethod
    def update_credits(user_id: str, credits: int):
        try:
            result = db.users.find_one_and_update(
                {'_id': ObjectId(user_id)},
                {'$inc': {'credits': credits}},
                return_document=True
            )
            return result['credits'] if result else None
        except Exception as e:
            current_app.logger.error(f"Error updating user credits: {str(e)}")
            return None

    @staticmethod
    def update_stripe_customer_id(user_id: str, stripe_customer_id: str):
        try:
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"stripe_customer_id": stripe_customer_id}}
            )
        except Exception as e:
            current_app.logger.error(f"Error updating Stripe customer ID: {str(e)}")
        
    @staticmethod
    def update_profile(user_id: str, update_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        allowed_fields = {"first_name", "last_name", "email", "preferences", "last_login"}
        update_dict = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not update_dict:
            return False, None  # No valid fields to update
        
        try:
            result = db.users.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_dict},
                return_document=True
            )
            return bool(result), result
        except Exception as e:
            current_app.logger.error(f"Error updating user profile: {str(e)}")
            return False, None

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