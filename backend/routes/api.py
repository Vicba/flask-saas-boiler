from flask import Blueprint, jsonify
from routes.auth.routes import auth_bp
from routes.user.routes import user_bp
from routes.payment.routes import payment_bp
from routes.ai.routes import ai_bp

api = Blueprint('api', __name__)

# Register sub-blueprints
api.register_blueprint(auth_bp, url_prefix='/auth')
api.register_blueprint(user_bp, url_prefix='/user')
api.register_blueprint(payment_bp, url_prefix='/payment')
api.register_blueprint(ai_bp, url_prefix='/ai')

# Health check route
@api.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})