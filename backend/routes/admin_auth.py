from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.jwt_utils import verify_access_token
from bson import ObjectId

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/api/admin")

def is_admin(user_id):
    user = User.find_by_id(user_id)
    return user and user.get("is_admin", False)

@admin_auth_bp.route("/users", methods=["GET"])
def get_users():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    user_id = verify_access_token(token)

    if not user_id or not is_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    users = User.get_all_users()
    return jsonify(users)

@admin_auth_bp.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    admin_id = verify_access_token(token)

    if not admin_id or not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    User.delete_user(ObjectId(user_id))
    return jsonify({"message": "User deleted"})
