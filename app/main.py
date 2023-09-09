from app import app, db, CUSTOMPRICEKEY, webhookKey
from flask import jsonify, request, Blueprint, g, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from passageidentity import Passage
import os
from sqlalchemy import or_
import stripe
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

class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_ID = db.Column(db.Integer, primary_key=True)
    Sender_ID = db.Column(db.Integer, db.ForeignKey('user.User_ID'))
    Recepient_ID = db.Column(db.Integer, db.ForeignKey('user.User_ID'))
    Transaction_Type = db.Column(db.String)
    Amount = db.Column(db.Float)
    def json(self):
        return {
            "transaction_ID": self.transaction_ID,
            "Sender_ID": self.Sender_ID,
            "Recepient_ID": self.Recepient_ID,
            "Transaction_Type": self.Transaction_Type,
            "Amount": self.Amount

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
        ##########check this back after testing ###############
        g.user = psg.authenticateRequest(request)
        # pass
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
    
@app.route("/usernames")
def getAllUsenames():
    userList = User.query.all()
    
    return jsonify([user.json()["Username"] for user in userList]), 200

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
                return "User Balance Updated: " + str(user.Wallet_Balance + data["TransactionAmount"]), 200
        return "User not found", 404
    except Exception as e:
        db.session.rollback()
        return "An error occurred while updating the User's balance. " + str(e), 406
    
# Route to create a new transaction
@app.route("/transaction", methods=['POST'])
def createTransaction():
    """
    Sample Request
    {
        "Sender_ID": "1",
        "Recepient_ID": "2",
        "Transaction_Type": "Transfer",
        "TransactionAmount": 1000
    }
    """
    data = request.get_json()
    try:
        sender = User.query.filter_by(User_ID=data["Sender_ID"]).first()
        recepient = User.query.filter_by(User_ID=data["Recepient_ID"]).first()
        if ((sender and recepient) and (sender != recepient)):
            # Check if sender has enough balance for transaction
            if (sender.Wallet_Balance - data["TransactionAmount"] < 0):
                return "Sender has insufficient Balance", 406

            # Update Balances of sender and recepient
            setattr(sender, "Wallet_Balance",
                    sender.Wallet_Balance - data["TransactionAmount"])
            setattr(recepient, "Wallet_Balance",
                    recepient.Wallet_Balance + data["TransactionAmount"])

            # Create a new transaction
            new_Transaction = Transaction()
            new_Transaction.Sender_ID = data["Sender_ID"]
            new_Transaction.Recepient_ID = data["Recepient_ID"]
            new_Transaction.Transaction_Type = data["Transaction_Type"]
            new_Transaction.Amount = data["TransactionAmount"]
            db.session.add(new_Transaction)

            db.session.commit()

            return "Transaction Complete", 201

        return "One of the transaction parties does not exist", 404
    except Exception as e:
        db.session.rollback()
        return "An error occurred while creating the transaction. " + str(e), 406

# Get the transactions of a user using their User_ID
@auth.route("/viewTransaction/<int:id>", methods=['GET'])
def viewTransaction(id: int):

    user_ID = id
    try:
        transactions = Transaction.query.filter(
            or_(Transaction.Sender_ID == user_ID, Transaction.Recepient_ID == user_ID)).all()
        print(transactions)
        if len(transactions):
            return jsonify(
                [transaction.json() for transaction in transactions]
            ), 200

        return "No transactions found.", 404
    except Exception as e:
        db.session.rollback()
        return "An error occurred while creating the transaction. " + str(e), 406

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': CUSTOMPRICEKEY,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost/TIKTOK-on-the-clock/frontend/pages/homepage.html',
            cancel_url='http://localhost/TIKTOK-on-the-clock/frontend/pages/topuppage.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/create-checkout-session/cart', methods=['POST'])
def create_cart_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': CUSTOMPRICEKEY,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1/TIKTOK-on-the-clock/frontend/pages/cartShopping.html',
            cancel_url='http://127.0.0.1/TIKTOK-on-the-clock/frontend/pages/carttopuppage.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route('/create-checkout-session/buy-now-pay-later', methods=['POST'])
def create_checkout_session_buy_now():
    try:
        stripe.checkout.Session.create(
            payment_method_types=['card', 'afterpay_clearpay'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'T-shirt',
                    },
                    # Make sure the total amount fits within Afterpay transaction amount limits:
                    # https://stripe.com/docs/payments/afterpay-clearpay#collection-schedule
                    'unit_amount': 2000,
                },
                'quantity': 1,
            }],
            mode='payment',
            shipping_address_collection={
                # Specify which shipping countries Checkout should provide as options for shipping locations
                'allowed_countries': ['AU', 'GB', 'NZ', 'US'],
            },
            # If you already have the shipping address, provide it in payment_intent_data:
            # payment_intent_data: {
            #   shipping: {
            #     name: 'Jenny Rosen',
            #     address: {
            #       line1: '1234 Main Street',
            #       city: 'San Francisco',
            #       state: 'CA',
            #       country: 'US',
            #       postal_code: '94111',
            #     },
            #   },
            # },
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(create_checkout_session_buy_now.url, code=303)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.data

        sig_header = request.headers.get('Stripe-Signature')

        # creating this event will ensure that post request is sent by stripe
        event = stripe.Webhook.construct_event(payload, sig_header, webhookKey)

    except ValueError as e:
        # Invalid payload
        return '', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return '', 500

    # Passed signature verification, transaction has occured and user has transferred that amount

    # event object contains all important info including transacted amount
    # amount transected comes in cents(have to divide by 100 for dollar value)
    print('event is printed')
    print(event)

    # to do for aloysius
    # fetch the price from the event json object (which comes in cents so divide by 100)
    # update the user DB on the amount of value topped up
    if("amount_total" not in event["data"]["object"]):
        amount = event["data"]["object"]["amount"]/100
    else:
        amount = event["data"]["object"]["amount_total"]/100
    
    email = event["data"]["object"]["customer_details"]["email"]

    try:
        user = User.query.filter_by(EmailAddress=email).first()
        if user:
            if (user.Wallet_Balance + amount < 0):
                return "User has insufficient Balance", 200
            else:
                setattr(user, "Wallet_Balance", user.Wallet_Balance + amount)
                db.session.commit()
                return "User Balance Updated", 200
        return "User not found", 404
    except Exception as e:
        db.session.rollback()
        return "An error occurred while updating the User's balance. " + str(e), 406