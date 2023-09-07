from app import app, db
from flask import jsonify, request, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.user import User

# Function and Route to Register a new User
@app.route("/register", methods=['POST'])
def register():
    """
    Sample Request
    {
        "Username": "John117",
        "EmailAddress": "johnny@gmail.com",
        "Password": "12345678",
        "Phone_Number": "99999999"
    }
    """
    data = request.get_json()
    try:
        userExists = User.query.filter_by(
            EmailAddress=data["EmailAddress"]).first()
        if userExists:
            return jsonify(
                {
                    "error": True,
                    "message": "An error occured while creating a new User. User with ID " + str(userExists.User_ID) + " already exists. Check that email address is unique."
                }
            ), 409
        
        # Hash password
        hashed_password = generate_password_hash(data.get("Password"), method='pbkdf2:sha256', salt_length=8)
        data["Password"] = hashed_password

        # Create new User
        newUser = User()
        newUser.Username = data.get("Username")
        newUser.EmailAddress = data.get("EmailAddress")
        newUser.ContactNo = data.get("ContactNo")
        newUser.Password = data.get("Password")
        newUser.Wallet_Balance = 0

        # Add newUser into the database, return error if failed
        db.session.add(newUser)
        db.session.commit()

        return jsonify(
            newUser.json()       
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "error": True,
                "message": "An error occurred while creating the new User. " + str(e)
            }
        ), 406
