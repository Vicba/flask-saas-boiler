from flask import Blueprint, request, jsonify
from auth import token_required
from models.user import User

user_bp = Blueprint('user', __name__)

# route: /api/user/profile
@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(user_id):
    user = User.get_by_id(user_id)
    if user:
        return jsonify({'user': user}), 200
    return jsonify({'error': 'User not found'}), 404

@user_bp.route('/update-profile', methods=['PATCH'])
@token_required
def update_profile(user_id):
    data = request.json

    allowed_fields = {"first_name", "last_name", "email", "preferences", "last_login"}

    # check if all fields are allowed
    for field in data.keys():
        if field not in allowed_fields:
            return jsonify({'error': f'Field {field} is not allowed'}), 400

    updated_user = User.update_profile(user_id, data)
    
    if updated_user:
        return jsonify({'message': 'Profile updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update profile'}), 400