from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)

# Mock user database (in production, use a real database)
users_db = {
    "admin@govtosha.in": {
        "password": "admin123",
        "name": "Admin User",
        "role": "Administrator"
    }
}

# Mock sessions (in production, use Redis or database)
active_sessions = {}

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Check if user exists and password is correct
        if email in users_db and users_db[email]['password'] == password:
            # Create mock access token
            access_token = f"token_{email}_{hash(password)}"
            active_sessions[access_token] = {
                "email": email,
                "name": users_db[email]['name'],
                "role": users_db[email]['role']
            }
            
            return jsonify({
                "accessToken": access_token,
                "message": "Login successful"
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', 'User')
        
        # Check if user already exists
        if email in users_db:
            return jsonify({"error": "User already exists"}), 400
            
        # Add new user
        users_db[email] = {
            "password": password,
            "name": name,
            "role": "User"
        }
        
        return jsonify({"message": "Registration successful"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/getUserDetails', methods=['GET'])
def get_user_details():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No valid token provided"}), 401
            
        token = auth_header.split(' ')[1]
        
        if token in active_sessions:
            user_data = active_sessions[token]
            return jsonify(user_data), 200
        else:
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/refresh', methods=['GET'])
def refresh_token():
    try:
        # In a real implementation, this would validate refresh tokens
        # For demo purposes, return a new token
        return jsonify({
            "accessToken": "new_refresh_token_demo",
            "message": "Token refreshed"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if token in active_sessions:
                del active_sessions[token]
                
        return jsonify({"message": "Logout successful"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)