from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(_name_)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# Define routes
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    new_user = User(username=data['username'], password=data['password'], role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({'message': 'Login successful', 'role': user.role}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Example API routes for data management
# Implement CRUD operations as per requirements

if _name_ == '_main_':
    db.create_all()
    app.run(debug=True)