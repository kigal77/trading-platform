from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Trade(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # "UP" or "DOWN"
    result = db.Column(db.String(10), nullable=True)  # "WIN" or "LOSS"
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/trade', methods=['POST'])
def trade():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})

    user = User.query.get(session['user_id'])
    amount = float(request.form['amount'])
    direction = request.form['direction']

    if amount > user.balance:
        return jsonify({'error': 'Insufficient balance'})

    result = "WIN" if random.random() > 0.5 else "LOSS"

    if result == "WIN":
        user.balance += amount * 1.95  
    else:
        user.balance -= amount

    trade = Trade(user_id=user.id, amount=amount, direction=direction, result=result)
    db.session.add(trade)
    db.session.commit()

    return jsonify({'result': result, 'new_balance': user.balance})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
