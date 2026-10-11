
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import Blueprint, request, jsonify
from pymongo.errors import PyMongoError

from database import db

auth_bp = Blueprint("auth", __name__)

JWT_SECRET = os.getenv("JWT_SECRET")


@auth_bp.route("/register", methods=["POST"])
def register():
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not JWT_SECRET:
        return jsonify({"error": "JWT secret is not configured"}), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Email is required"}), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    email = email.strip().lower()

    try:
        if db.users.find_one({"email": email}):
            return jsonify({"error": "Email is already registered"}), 409

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        user = {
            "email": email,
            "password_hash": password_hash.decode("utf-8"),
            # "role": "viewer"
        }

        result = db.users.insert_one(user)

        return jsonify({
            "message": "User registered successfully",
            "user_id": str(result.inserted_id),
            # "role": user["role"]
        }), 201

    except PyMongoError:
        return jsonify({"error": "Could not register user"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not JWT_SECRET:
        return jsonify({"error": "JWT secret is not configured"}), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = db.users.find_one({
            "email": email.strip().lower()
        })

        if user is None or not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid email or password"}), 401

        now = datetime.now(timezone.utc)

        token = jwt.encode(
            {
                "sub": str(user["_id"]),
                "role": user["role"],
                "iat": now,
                "exp": now + timedelta(hours=1)
            },
            JWT_SECRET,
            algorithm="HS256"
        )

        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not log in"}), 500
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid stored user credentials"}), 500