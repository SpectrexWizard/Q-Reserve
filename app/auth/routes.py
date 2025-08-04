from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User
from app.auth.utils import hash_password, check_password, is_valid_role
from app.utils import jwt_required_with_user
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'end_user')
        
        # Validation
        if not email or not username or not password:
            error = 'Email, username, and password are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('auth/register.html')
        
        if not is_valid_email(email):
            error = 'Invalid email format'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            error = 'Password must be at least 6 characters long'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('auth/register.html')
        
        if not is_valid_role(role):
            role = 'end_user'  # Default to end_user for invalid roles
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            error = 'Email already registered'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            error = 'Username already taken'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        if request.is_json:
            return jsonify({
                'message': 'User registered successfully',
                'access_token': access_token,
                'user': user.to_dict()
            }), 201
        
        # Store token in session for web interface
        session['access_token'] = access_token
        session['user_id'] = user.id
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('tickets.list_tickets'))
        
    except Exception as e:
        db.session.rollback()
        error = 'Registration failed. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            error = 'Email and password are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password(password, user.password_hash):
            error = 'Invalid email or password'
            if request.is_json:
                return jsonify({'error': error}), 401
            flash(error, 'error')
            return render_template('auth/login.html')
        
        if not user.is_active:
            error = 'Account is deactivated'
            if request.is_json:
                return jsonify({'error': error}), 401
            flash(error, 'error')
            return render_template('auth/login.html')
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        if request.is_json:
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        
        # Store token in session for web interface
        session['access_token'] = access_token
        session['user_id'] = user.id
        flash('Login successful!', 'success')
        return redirect(url_for('tickets.list_tickets'))
        
    except Exception as e:
        error = 'Login failed. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Clear session
        session.clear()
        
        if request.is_json:
            return jsonify({'message': 'Logout successful'}), 200
        
        flash('You have been logged out.', 'info')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'error': 'Logout failed'}), 500
        flash('Logout failed.', 'error')
        return redirect(url_for('tickets.list_tickets'))

@auth_bp.route('/profile')
@jwt_required_with_user
def profile(user):
    if request.is_json:
        return jsonify({'user': user.to_dict()}), 200
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/verify-token')
@jwt_required_with_user
def verify_token(user):
    """Endpoint to verify if token is still valid"""
    return jsonify({
        'valid': True,
        'user': user.to_dict()
    }), 200