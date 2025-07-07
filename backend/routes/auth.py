from flask import Blueprint, request, jsonify, make_response
from models.user_model import User
from utils.jwt_utils import create_access_token, create_refresh_token, verify_refresh_token
from utils.email_utils import generate_reset_token, verify_reset_token, send_reset_email
from utils.google_oauth import verify_google_token
from bson import ObjectId
from config.db_config import ADMIN_EMAIL
from config.db_config import ADMIN_PASSWORD

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    user = User.create_user(data["name"], data["email"], data["password"])
    if not user:
        return jsonify({"error": "User already exists"}), 409
    return jsonify({"message": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    # Hardcoded admin credentials
   

    # Check if login matches admin credentials
    if data["email"] == ADMIN_EMAIL and data["password"] == ADMIN_PASSWORD:
        # Return admin token and info
        access_token = create_access_token("admin_user_id")  # Use a fixed admin id or special id
        refresh_token = create_refresh_token("admin_user_id")

        resp = make_response(jsonify({
            "access_token": access_token,
            "isAdmin": True,
            "email": ADMIN_EMAIL,
            "user_id": "admin_user_id"
        }))
        resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Strict")
        return resp

    # Normal user login flow
    user = User.find_by_email(data["email"])
    if not user or not User.verify_password(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(user["_id"])
    refresh_token = create_refresh_token(user["_id"])

    resp = make_response(jsonify({
        "access_token": access_token,
        "isAdmin": False,
        "email": user["email"],
        
    }))
    resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Strict")
    return resp


@auth_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    token = request.cookies.get("refresh_token")
    user_id = verify_refresh_token(token)
    if not user_id:
        return jsonify({"error": "Invalid refresh token"}), 401

    new_access = create_access_token(user_id)
    return jsonify({"access_token": new_access})

@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"message": "Logged out"}))
    resp.set_cookie("refresh_token", "", max_age=0)
    return resp

@auth_bp.route("/google-login", methods=["POST"])
def google_login():
    token = request.json.get("token")
    user_data = verify_google_token(token)
    if not user_data:
        return jsonify({"error": "Invalid Google token"}), 401

    user = User.find_by_email(user_data["email"])
    if not user:
        # auto-create user
        user = User.create_user(user_data["name"], user_data["email"], password="")

    access_token = create_access_token(user["_id"])
    refresh_token = create_refresh_token(user["_id"])
    resp = make_response(jsonify({"access_token": access_token}))
    resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Strict")
    return resp

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.json.get("email")
    user = User.find_by_email(email)
    if not user:
        return jsonify({"message": "If email exists, a reset link will be sent."})

    token = generate_reset_token(email)
    send_reset_email(email, token)
    return jsonify({"message": "Reset email sent."})

@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    new_password = request.json.get("password")
    email = verify_reset_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token"}), 400

    success = User.set_new_password(email, new_password)
    return jsonify({"message": "Password reset successful" if success else "Error resetting password"})
