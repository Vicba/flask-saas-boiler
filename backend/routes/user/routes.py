from flask import Blueprint, request, jsonify
from auth import token_required
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(user_id):
    data = request.json
    updated_user = User.update_profile(user_id, data)
    
    if updated_user:
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'email': updated_user['email'],
                'first_name': updated_user['first_name'],
                'last_name': updated_user['last_name'],
                'preferences': updated_user['preferences']
            }
        }), 200
    else:
        return jsonify({'error': 'Failed to update profile'}), 400