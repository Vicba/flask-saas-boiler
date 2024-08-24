import jwt
from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY")

def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization').split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        user_id = decode_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid!'}), 403
        
        return f(user_id, *args, **kwargs)
    
    return decorated_function
