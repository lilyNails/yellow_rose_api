from flask import Blueprint, request, jsonify, session
from src.models.database import UserManager
import hashlib

auth_bp = Blueprint('auth', __name__)
user_manager = UserManager()

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        # Simple password hashing (in production, use proper hashing like bcrypt)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        user = user_manager.authenticate_user(username, password_hash)
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        role = data.get('role', 'كاشير')
        
        # Simple password hashing
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        user_id = user_manager.add_user(username, password_hash, role)
        
        return jsonify({'success': True, 'user_id': user_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    try:
        if 'user_id' in session:
            return jsonify({
                'success': True,
                'logged_in': True,
                'user': {
                    'user_id': session['user_id'],
                    'username': session['username'],
                    'role': session['role']
                }
            })
        else:
            return jsonify({'success': True, 'logged_in': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

