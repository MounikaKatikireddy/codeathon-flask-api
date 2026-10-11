
from functools import wraps
from flask import request, jsonify


def roles_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            user = getattr(request, "current_user", None)

            if user is None:
                return jsonify({
                    "error": "Authentication required"
                }), 401

            if user.get("role") not in allowed_roles:
                return jsonify({
                    "error": "You do not have permission to perform this action"
                }), 403

            return function(*args, **kwargs)

        return wrapper
    return decorator