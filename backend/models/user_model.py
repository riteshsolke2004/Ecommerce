from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
from config.db_config import user_collection

class User:
    @staticmethod
    def create_user(name, email, password, is_admin=False):
        if user_collection.find_one({"email": email}):
            return None  # User already exists

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "cart": [],
            "wishlist": [],
            "is_admin": is_admin,
            "last_active": datetime.utcnow()
        }
        user_collection.insert_one(user_data)
        return user_data

    @staticmethod
    def find_by_email(email):
        return user_collection.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id):
        return user_collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def verify_password(stored_password, entered_password):
        return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password)

    @staticmethod
    def update_last_active(user_id):
        user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_active": datetime.utcnow()}}
        )

    @staticmethod
    def set_new_password(email, new_password):
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        result = user_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed}}
        )
        return result.modified_count > 0

    @staticmethod
    def get_all_users():
        return list(user_collection.find({}, {"password": 0}))

    @staticmethod
    def delete_user(user_id):
        result = user_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
