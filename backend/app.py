import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.api import api
from dotenv import load_dotenv
from pymongo import MongoClient
from authlib.integrations.flask_client import OAuth
from flask_caching import Cache
import logging  

load_dotenv()

app = Flask(__name__)
CORS(app)
oauth = OAuth(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Implement caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# MongoDB setup with connection pooling
client = MongoClient(os.getenv("MONGODB_URI"), maxPoolSize=50)
db = client['ai_saas']

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

app.register_blueprint(api, url_prefix="/api")

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000) # nosec