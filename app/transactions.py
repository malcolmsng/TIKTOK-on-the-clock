from app import app, db
from flask import jsonify, request, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import User
from sqlalchemy import or_

class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_ID = db.Column(db.Integer, primary_key=True)
    Sender_ID = db.Column(db.Integer)
    Recepient_ID = db.Column(db.Integer)
    Transaction_Type = db.Column(db.String)
    Amount = db.Column(db.Integer)
    
    def json(self):
        return {
            "transaction_ID": self.transaction_ID,
            "Sender_ID": self.Sender_ID,
            "Recepient_ID": self.Recepient_ID,
            "Transaction_Type": self.Transaction_Type,
            "Amount": self.Amount
            
        }

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
        if (sender and recepient):
            # Check if sender has enough balance for transaction
            if (sender.Wallet_Balance - data["TransactionAmount"] < 0):
                return "Sender has insufficient Balance", 406

            # Update Balances of sender and recepient
            setattr(sender, "Wallet_Balance", sender.Wallet_Balance - data["TransactionAmount"])
            setattr(recepient, "Wallet_Balance", sender.Wallet_Balance + data["TransactionAmount"])
            
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
@app.route("/viewTransaction", methods=['POST'])
def viewTransaction():
    """
    Sample Request
    {
        "User_ID": 1
    }
    """
    data = request.get_json()
    user_ID = data["User_ID"]
    try:
        transactions = Transaction.query.filter(or_(Transaction.Sender_ID == user_ID, Transaction.Recepient_ID == user_ID)).all()
        print(transactions)
        if len(transactions):
            return jsonify(
                [transaction.json() for transaction in transactions]
            ), 200

        return "No transactions found.", 404
    except Exception as e:
        db.session.rollback()
        return "An error occurred while creating the transaction. " + str(e), 406