import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from auth import token_required
from models.user import User
import stripe
from dotenv import load_dotenv
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter

load_dotenv()

ai_bp = Blueprint('ai', __name__)

# Setup OpenAI and Stripe
client = OpenAI() # make sure to set dotenv to access the api key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# rate limit each user to 5 requests per minute
limiter = Limiter(key_func=get_remote_address)

# route: /api/ai/generate
@ai_bp.route('/generate', methods=['POST'])
@limiter.limit("5 per minute")
@token_required
def generate(user_id):
    data = request.json
    prompt = data.get('prompt')

    if not prompt.strip():
        return jsonify({'error': 'Prompt is required'}), 400

    user = User.get_by_id(user_id)

    if user['credits'] <= 0:
        return jsonify({'error': 'Not enough credits'}), 400

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    User.update_credits(user_id, -1)

    return jsonify({'text': response.choices[0].message.content})

# route: /api/ai/generate_image
@ai_bp.route('/generate_image', methods=['POST'])
@limiter.limit("5 per minute")
@token_required
def generate_image(user_id):
    data = request.json
    prompt = data.get('prompt')

    if not prompt.strip():
        return jsonify({'error': 'Prompt is required'}), 400
    
    user = User.get_by_id(user_id)

    if user['credits'] <= 0:
        return jsonify({'error': 'Not enough credits'}), 400

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard"
    )

    User.update_credits(user_id, -3)

    return jsonify({'image_url': response.data[0].url})