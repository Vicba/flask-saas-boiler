from flask import Blueprint, request, jsonify
from models.user import User
from auth import generate_token

auth_bp = Blueprint('auth', __name__)

# route: /api/auth/register
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User.register(data['email'], data['password'])
    if user:
        token = generate_token(str(user['_id']))
        return jsonify({'token': token})
    return jsonify({'message': 'User already exists'}), 400

# route: /api/auth/login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.authenticate(data['email'], data['password'])
    if user:
        token = generate_token(str(user['_id']))
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 400