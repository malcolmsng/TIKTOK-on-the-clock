from app import app, db
from flask import jsonify, request, url_for, render_template, Blueprint, g
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from passageidentity import Passage
import os
from passageidentity import Passage, PassageError

class User(db.Model):
    __tablename__ = 'user'

    User_ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String)
    EmailAddress = db.Column(db.String)
    Password = db.Column(db.String)
    Wallet_Balance = db.Column(db.Float)
    Phone_Number = db.Column(db.Integer)
    

    def json(self):
        return {
            "User_ID": self.User_ID,
            "Username": self.Username,
            "EmailAddress": self.EmailAddress,
            "Password": self.Password,
            "Phone_Number": self.Phone_Number,
            "Wallet_Balance": self.Wallet_Balance,
            "Phone_Number": self.Phone_Number
            
        }

auth = Blueprint('auth', __name__)

PASSAGE_API_KEY = os.environ.get('PASSAGE_API_KEY')
PASSAGE_APP_ID = os.environ.get('PASSAGE_APP_ID')

try:
    psg = Passage(PASSAGE_APP_ID, PASSAGE_API_KEY)
except PassageError as e:
    print(e)
    exit()


@auth.before_request
def before_request():
    try:
        g.user = psg.authenticateRequest(request)
    except PassageError as e:
        return "Not Authenticated", 404

# Function and Route for user login
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("EmailAddress")
    password = data.get("Password")

    if not email or not password:
        return "Invalid user credentials", 400

    user = User.query.filter_by(EmailAddress=email).first()

    if user and check_password_hash(user.Password, password):
        return jsonify(user.json())
    else:
        return "Invalid user credentials", 401

# Function and Route for getting All Users in the DB
@auth.route("/user")
def getAllUser():
    userList = User.query.all()
    
    return jsonify([user.json() for user in userList]), 200
    

# Function and Route for getting a User by ID
@auth.route("/user/<int:id>")
def getUserByID(id: int):
    userList = User.query.filter_by(User_ID=id).all()
    if len(userList):
        return jsonify(
            [user.json() for user in userList]
        ), 200
    return "There are no such user with ID: " + str(id), 406

# Function and Route to update a User's Balance
@auth.route("/updateBalance", methods=['PUT'])
def updateBalance():
    """
    Sample Request
    {
        "User_ID": "1",
        "TransactionAmount": 1000
    }
    """
    data = request.get_json()

    try:
        user = User.query.filter_by(User_ID=data["User_ID"]).first()
        if user:
            if (user.Wallet_Balance + data["TransactionAmount"] < 0):
                return "User has insufficient Balance", 200
            else:
                setattr(user, "Wallet_Balance", user.Wallet_Balance + data["TransactionAmount"])
                db.session.commit()
                return "User Balance Updated", 200
        return "User not found", 404
    except Exception as e:
        db.session.rollback()
        return "An error occurred while updating the User's balance. " + str(e), 406