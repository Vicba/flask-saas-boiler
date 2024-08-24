from flask import Flask
from flask_cors import CORS
from routes.api import api
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client['ai_saas']

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

app.register_blueprint(api, url_prefix="/api")


if __name__ == "__main__":
    app.run(debug=True)
