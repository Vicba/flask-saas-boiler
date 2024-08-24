from flask import Blueprint
from auth import token_required

user_bp = Blueprint('user', __name__)

# Add user-related routes here