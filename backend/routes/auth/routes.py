import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from models.user import User
from auth import generate_token
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth


load_dotenv()

auth_bp = Blueprint('auth', __name__)

limiter = Limiter(key_func=get_remote_address)

def init_oauth(oauth):
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'email'},
    )
    return google

# route: /api/auth/register
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    data = request.json
    user = User.register(data['email'], data['password'])
    if user:
        token = generate_token(str(user['_id']))
        User.update_profile(user['_id'], {'last_login': datetime.now(timezone.utc)})
        return jsonify({'token': token})
    return jsonify({'message': 'User already exists'}), 400

# route: /api/auth/login
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.json
    user = User.authenticate(data['email'], data['password'])
    if user:
        token = generate_token(str(user['_id']))
        User.update_profile(user['_id'], {'last_login': datetime.now(timezone.utc)})
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 400



# route: /api/auth/google
@auth_bp.route('/google', methods=['GET'])
@limiter.limit("10 per minute")
def google_auth():
    google = init_oauth(current_app.extensions['authlib.integrations.flask_client'])
    redirect_uri = url_for('api.auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

# route: /api/auth/google/callback
@auth_bp.route('/google/callback', methods=['GET'])
@limiter.limit("10 per minute")
def google_callback():
    google = init_oauth(current_app.extensions['authlib.integrations.flask_client'])
    resp = google.authorize_access_token()
    if resp is None or resp.get('access_token') is None:
        return jsonify({'message': 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )}), 400

    google_user = google.get('userinfo')
    email = google_user.json()['email']

    user = User.get_by_email(email)
    if not user:
        user = User.register_google(email, google_id=google_user.json()['id'])

    token = generate_token(str(user['_id']))
    return jsonify({'token': token})

# route: /api/auth/google/callback
@auth_bp.route('/check', methods=['GET'])
@limiter.limit("10 per minute")
def auth_check():
    return jsonify({'token': "hi"})