"""Authentication forms for Q-Reserve."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from apps.users.models import User


class LoginForm(FlaskForm):
    """Login form."""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember me')
    
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    first_name = StringField('First Name', validators=[
        Length(max=50, message='First name must be less than 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    
    display_name = StringField('Display Name', validators=[
        Length(max=100, message='Display name must be less than 100 characters')
    ])
    
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Validate that email is not already registered."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('An account with this email already exists.')


class ForgotPasswordForm(FlaskForm):
    """Forgot password form."""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    """Reset password form."""
    
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Reset Password')