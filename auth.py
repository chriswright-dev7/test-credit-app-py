from flask import request, jsonify

def require_api_key(expected_key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = request.headers.get("X-API-Key")

            if key != expected_key:
                return jsonify({"error": "Unauthorized"}), 401

            return func(*args, **kwargs)
        return wrapper
    return decorator