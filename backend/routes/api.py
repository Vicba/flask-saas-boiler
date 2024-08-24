from flask import Blueprint, request, jsonify
from openai import OpenAI
import stripe
from models.user import User
from auth import generate_token, token_required
import os
from dotenv import load_dotenv
import logging

load_dotenv()

api = Blueprint('api', __name__)

# Setup OpenAI and Stripe
client = OpenAI() # make sure to set dotenv to access the api key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# health check
@api.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User.register(data['email'], data['password'])
    if user:
        token = generate_token(str(user['_id']))
        return jsonify({'token': token})
    return jsonify({'message': 'User already exists'}), 400

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.authenticate(data['email'], data['password'])
    if user:
        token = generate_token(str(user['_id']))
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 400

@api.route('/generate', methods=['POST'])
@token_required
def generate(user_id):
    data = request.json
    prompt = data.get('prompt')

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

@api.route('/create-checkout-session', methods=['POST'])
@token_required
def create_checkout_session(user_id):
    data = request.json
    amount = data.get('amount')

    if not amount:
        return jsonify({'error': 'Amount is required'}), 400

    user = User.get_by_id(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        # Check if user has a Stripe customer ID, if not, create one
        if 'stripe_customer_id' not in user or not user['stripe_customer_id']:
            stripe_customer = stripe.Customer.create(email=user['email'])
            User.update_stripe_customer_id(user_id, stripe_customer.id)
            stripe_customer_id = stripe_customer.id
        else:
            stripe_customer_id = user['stripe_customer_id']

        # Create Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': amount,
                    'product_data': {
                        'name': 'Credits',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/cancel',
            metadata={
                "user_id": user_id
            }
        )

        return jsonify({
            'success': True,
            'checkout_session_id': checkout_session.id,
            'checkout_session_url': checkout_session.url
        })

    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

# Add a new webhook route to handle successful payments
@api.route('/webhook', methods=['POST'])
def webhook():
    try:
        event = stripe.Webhook.construct_event(
            request.data, request.headers.get('Stripe-Signature'), os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        credits = session['amount_total'] // 100  # Convert cents to credits
    
        if User.update_credits(user_id, credits):
            logging.info(f"Successfully added {credits} credits to user {user_id}")
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Failed to update user credits'}), 400
    else:
        logging.info(f"Unhandled event type: {event['type']}")

    return jsonify({'success': True}), 200