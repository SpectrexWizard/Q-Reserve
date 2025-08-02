"""
Authentication routes for Q-Reserve application.

This module handles user authentication, registration, and password management routes.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from core.extensions import db, limiter
from core.utils import generate_secure_token
from apps.auth.forms import (
    LoginForm, RegistrationForm, ForgotPasswordForm, 
    ResetPasswordForm, ChangePasswordForm
)
from apps.users.models import User, UserRole
from apps.auth.utils import send_password_reset_email
from apps.notifications.sender import send_welcome_email

# Create blueprint
bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Determine if login is with email or username
        if '@' in form.username_or_email.data:
            user = User.query.filter_by(email=form.username_or_email.data.lower()).first()
        else:
            user = User.query.filter_by(username=form.username_or_email.data).first()
        
        if user and user.verify_password(form.password.data):
            if not user.is_active_user:
                flash('Your account is not active. Please contact administrator.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Log the user in
            login_user(user, remember=form.remember_me.data)
            
            # Update last login time
            user.update_last_login()
            
            # Get next page from query parameter
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                # Redirect based on user role
                if user.is_admin:
                    next_page = url_for('dashboard.admin')
                elif user.is_agent:
                    next_page = url_for('dashboard.agent')
                else:
                    next_page = url_for('tickets.list')
            
            flash(f'Welcome back, {user.display_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data.lower(),
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                department=form.department.data,
                job_title=form.job_title.data,
                role=UserRole.END_USER  # Default role for self-registration
            )
            user.password = form.password.data
            
            # Generate email verification token
            user.email_verification_token = generate_secure_token()
            
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email
            try:
                send_welcome_email(user)
            except Exception as e:
                current_app.logger.error(f"Failed to send welcome email: {e}")
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Forgot password route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # Generate password reset token
            user.password_reset_token = generate_secure_token()
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            db.session.commit()
            
            # Send password reset email
            try:
                send_password_reset_email(user)
                flash('Password reset instructions have been sent to your email.', 'info')
            except Exception as e:
                current_app.logger.error(f"Failed to send password reset email: {e}")
                flash('Failed to send password reset email. Please try again.', 'error')
        else:
            # Don't reveal that email doesn't exist for security
            flash('If an account with that email exists, you will receive password reset instructions.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_password(token):
    """Reset password with token route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Find user with valid reset token
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
        flash('Invalid or expired password reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        try:
            # Update password
            user.password = form.password.data
            user.password_reset_token = None
            user.password_reset_expires = None
            
            db.session.commit()
            
            flash('Your password has been reset successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password reset error: {e}")
            flash('Failed to reset password. Please try again.', 'error')
    
    return render_template('auth/reset_password.html', form=form, token=token)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in users."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        try:
            current_user.password = form.new_password.data
            db.session.commit()
            
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('users.profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password change error: {e}")
            flash('Failed to change password. Please try again.', 'error')
    
    return render_template('auth/change_password.html', form=form)


@bp.route('/verify-email/<token>')
def verify_email(token):
    """Email verification route."""
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash('Invalid email verification token.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.email_verified_at:
        flash('Email already verified.', 'info')
        return redirect(url_for('auth.login'))
    
    try:
        user.email_verified_at = datetime.utcnow()
        user.email_verification_token = None
        
        db.session.commit()
        
        flash('Email verified successfully! You can now log in.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email verification error: {e}")
        flash('Failed to verify email. Please try again.', 'error')
    
    return redirect(url_for('auth.login'))


@bp.route('/resend-verification')
@login_required
@limiter.limit("1 per minute")
def resend_verification():
    """Resend email verification."""
    if current_user.email_verified_at:
        flash('Email already verified.', 'info')
        return redirect(url_for('users.profile'))
    
    try:
        current_user.email_verification_token = generate_secure_token()
        db.session.commit()
        
        send_welcome_email(current_user)
        flash('Verification email sent. Please check your inbox.', 'info')
        
    except Exception as e:
        current_app.logger.error(f"Failed to resend verification email: {e}")
        flash('Failed to send verification email. Please try again.', 'error')
    
    return redirect(url_for('users.profile'))


# Error handlers for authentication blueprint
@bp.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors."""
    flash('Too many attempts. Please try again later.', 'error')
    return redirect(url_for('auth.login')), 429


# TODO: Add social login routes (OAuth)
# TODO: Add two-factor authentication routes
# TODO: Add account lockout functionality
# TODO: Add login attempt logging and monitoring