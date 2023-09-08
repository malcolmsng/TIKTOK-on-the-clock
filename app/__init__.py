from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from dotenv import load_dotenv
import stripe


load_dotenv()

user = environ.get('user') or "placeholderuser"
password = environ.get('password') or "placeholderpassword"

DB_HOSTNAME = environ.get('DB_HOSTNAME')
DB_USERNAME = environ.get('DB_USERNAME')
DB_PASSWORD = environ.get('DB_PASSWORD')
DB_PORT = environ.get("DB_PORT")
DB_NAME = environ.get('DB_NAME')

CUSTOMPRICEKEY = environ.get("CUSTOM_PRICE_KEY") 
stripe.api_key = environ.get("STRIPE_PRIVATE_KEY") 
webhookKey = environ.get("WEB_HOOK_KEY")


app = Flask(__name__)

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_HOSTNAME + ":" + DB_PORT + "/" + DB_NAME
# print
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)

app.config['SECURITY_PASSWORD_SALT'] = environ.get("SECURITY_PASSWORD_SALT", default="very-important")

from .user import User, auth as auth_blueprint
from . import registration, transactions

app.register_blueprint(auth_blueprint)
