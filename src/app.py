"""Flask Application"""

from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_restx import Api
from flask_jwt_extended import JWTManager

from src.services import api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

load_dotenv()
app = Flask(__name__)
api.init_app(app)

app.config["JWT_SECRET_KEY"] = "budget-app"

jwt = JWTManager(app)