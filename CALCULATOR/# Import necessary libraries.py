# Import necessary libraries
import bcrypt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import jwt
from functools import wraps

# Initialize Flask app
app = Flask(_name_)

# Set up SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def _repr_(self):
        return '<User %r>' % self.username

# Decorator for token-based authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=data['username'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully!'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Username already exists!'}), 400

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401
    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 401
    if bcrypt.checkpw(auth.password.encode('utf-8'), user.password):
        token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Password incorrect!'}), 401

@app.route('/data', methods=['GET'])
@token_required
def get_data(current_user):
    # Implement data retrieval logic here
    return jsonify({'message': 'Data accessed successfully!'})

# Run the app
if _name_ == '_main_':
    app.run(debug=True)