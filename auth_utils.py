
import os
from functools import wraps

import jwt
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")


def token_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not JWT_SECRET:
            return jsonify({
                "error": "JWT secret is not configured"
            }), 503

        auth_header = request.headers.get("Authorization", "")

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "A Bearer token is required"
            }), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"]
            )

            if not payload.get("sub") or not payload.get("role"):
                return jsonify({
                    "error": "Token is missing required claims"
                }), 401

            request.current_user = payload

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid or expired token"
            }), 401

        return function(*args, **kwargs)

    return wrapper