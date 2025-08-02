"""Authentication routes for Q-Reserve."""

from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from core.extensions import login_manager
from core.utils import get_client_ip
from apps.users.models import User
from apps.users.services import create_user, get_user_by_email
from .forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime, timezone
from core.extensions import db


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('tickets.list'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            # Log login attempt
            current_app.logger.info(f'User {user.email} logged in from {get_client_ip()}')
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('tickets.list')
            
            flash('Welcome back!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('tickets.list'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = create_user(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                display_name=form.display_name.data,
                role='end_user'
            )
            
            # Log registration
            current_app.logger.info(f'New user registered: {user.email}')
            
            # Send welcome email
            from apps.notifications.sender import send_welcome_email
            send_welcome_email.delay(user.id)
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash(str(e), 'error')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password route."""
    if current_user.is_authenticated:
        return redirect(url_for('tickets.list'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        
        if user:
            # Generate password reset token
            from apps.users.services import generate_password_reset_token
            token = generate_password_reset_token(user)
            
            # Send password reset email
            from apps.notifications.sender import send_password_reset_email
            send_password_reset_email.delay(user.id, token)
            
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            # Don't reveal if user exists or not
            flash('If an account with that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password route."""
    if current_user.is_authenticated:
        return redirect(url_for('tickets.list'))
    
    # Verify token
    from apps.users.services import verify_password_reset_token
    user = verify_password_reset_token(token)
    
    if not user:
        flash('Invalid or expired password reset token.', 'error')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.set_password(form.password.data)
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash(str(e), 'error')
    
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Email verification route."""
    from apps.users.services import verify_email_token
    user = verify_email_token(token)
    
    if user:
        user.is_verified = True
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        flash('Your email has been verified successfully.', 'success')
    else:
        flash('Invalid or expired verification token.', 'error')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile route."""
    return redirect(url_for('users.profile'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route."""
    from apps.users.forms import ChangePasswordForm
    
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            from apps.users.services import change_password
            change_password(
                current_user,
                form.current_password.data,
                form.new_password.data
            )
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('users.profile'))
            
        except Exception as e:
            flash(str(e), 'error')
    
    return render_template('users/change_password.html', form=form)