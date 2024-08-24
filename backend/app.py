import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.api import api
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth


load_dotenv()

app = Flask(__name__)
CORS(app)
oauth = OAuth(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client['ai_saas']

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Add rate limits
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    # default_limits=["200 per day", "50 per hour"]
)

app.register_blueprint(api, url_prefix="/api")

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded, try again later", message=str(e.description)), 429


if __name__ == "__main__":
    app.run(debug=True) # nosec