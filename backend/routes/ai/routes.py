import os
from flask import Blueprint, request, jsonify, current_app
from openai import OpenAI
from auth import token_required
from models.user import User
import stripe
from dotenv import load_dotenv

load_dotenv()

ai_bp = Blueprint('ai', __name__)

# Setup OpenAI and Stripe
client = OpenAI() # make sure to set dotenv to access the api key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# route: /api/ai/generate
@ai_bp.route('/generate', methods=['POST'])
@token_required
def generate(user_id):
    data = request.json
    prompt = data.get('prompt')

    if not prompt.strip():
        return jsonify({'error': 'Prompt is required'}), 400

    user = User.get_by_id(user_id)

    if user['credits'] <= 0:
        return jsonify({'error': 'Not enough credits'}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        User.update_credits(user_id, -1)

        return jsonify({'text': response.choices[0].message.content})
    except Exception as e:
        current_app.logger.error(f"Error generating AI response: {str(e)}")
        return jsonify({'error': 'Failed to generate AI response'}), 500

# route: /api/ai/generate_image
@ai_bp.route('/generate-image', methods=['POST'])
@token_required
def generate_image(user_id):
    data = request.json
    prompt = data.get('prompt')

    if not prompt.strip():
        return jsonify({'error': 'Prompt is required'}), 400
    
    user = User.get_by_id(user_id)

    if user['credits'] <= 0:
        return jsonify({'error': 'Not enough credits'}), 400

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard"
        )

        User.update_credits(user_id, -3)

        return jsonify({'image_url': response.data[0].url})
    except Exception as e:
        current_app.logger.error(f"Error generating AI image: {str(e)}")
        return jsonify({'error': 'Failed to generate AI image'}), 500