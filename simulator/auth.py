"""
Authentication module for Proofpoint TAP API Simulator
Implements Basic Authentication
"""
from functools import wraps
from flask import request, jsonify
from config import Config
import base64


def check_auth(username, password):
    """Check if username and password are valid"""
    return username == Config.AUTH_USERNAME and password == Config.AUTH_PASSWORD


def authenticate():
    """Send a 401 response that enables basic auth"""
    return jsonify({'error': 'Authentication required'}), 401, {
        'WWW-Authenticate': 'Basic realm="Proofpoint TAP API"'
    }


def require_basic_auth(f):
    """
    Decorator to require HTTP Basic Authentication for a route
    Usage:
        @app.route('/protected')
        @require_basic_auth
        def protected_route():
            return "Success"
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
