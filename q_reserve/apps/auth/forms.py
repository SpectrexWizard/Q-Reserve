"""
Authentication forms for Q-Reserve application.

This module defines WTForms for user authentication, registration,
and password management.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Optional, Regexp
)
from apps.users.models import User, UserRole


class LoginForm(FlaskForm):
    """User login form."""
    
    username_or_email = StringField(
        'Username or Email',
        validators=[
            DataRequired(message='Username or email is required'),
            Length(min=3, max=120, message='Must be between 3 and 120 characters')
        ]
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required')
        ]
    )
    
    remember_me = BooleanField('Remember Me')
    
    def validate_username_or_email(self, field):
        """Validate that user exists and is active."""
        # Check if it's an email or username
        if '@' in field.data:
            user = User.query.filter_by(email=field.data.lower()).first()
        else:
            user = User.query.filter_by(username=field.data).first()
        
        if not user:
            raise ValidationError('Invalid username/email or password')
        
        if not user.is_active_user:
            raise ValidationError('Account is not active. Please contact administrator.')


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(message='First name is required'),
            Length(min=2, max=50, message='Must be between 2 and 50 characters'),
            Regexp(r'^[a-zA-Z\s]+$', message='Only letters and spaces allowed')
        ]
    )
    
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(message='Last name is required'),
            Length(min=2, max=50, message='Must be between 2 and 50 characters'),
            Regexp(r'^[a-zA-Z\s]+$', message='Only letters and spaces allowed')
        ]
    )
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=80, message='Must be between 3 and 80 characters'),
            Regexp(r'^[a-zA-Z0-9_]+$', message='Only letters, numbers, and underscores allowed')
        ]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address'),
            Length(max=120, message='Email must be less than 120 characters')
        ]
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=8, max=128, message='Password must be between 8 and 128 characters'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='Password must contain at least one lowercase letter, uppercase letter, and number'
            )
        ]
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )
    
    department = StringField(
        'Department',
        validators=[
            Optional(),
            Length(max=100, message='Department must be less than 100 characters')
        ]
    )
    
    job_title = StringField(
        'Job Title',
        validators=[
            Optional(),
            Length(max=100, message='Job title must be less than 100 characters')
        ]
    )
    
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(max=20, message='Phone number must be less than 20 characters'),
            Regexp(r'^[\d\s\-\+\(\)]+$', message='Invalid phone number format')
        ]
    )
    
    def validate_username(self, field):
        """Check if username is already taken."""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, field):
        """Check if email is already registered."""
        user = User.query.filter_by(email=field.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or try logging in.')


class AdminRegistrationForm(RegistrationForm):
    """Admin registration form with role selection."""
    
    role = SelectField(
        'Role',
        choices=[
            (UserRole.END_USER.value, 'End User'),
            (UserRole.AGENT.value, 'Support Agent'),
            (UserRole.ADMIN.value, 'Administrator')
        ],
        default=UserRole.END_USER.value,
        validators=[DataRequired(message='Role is required')]
    )


class ForgotPasswordForm(FlaskForm):
    """Forgot password form."""
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address')
        ]
    )
    
    def validate_email(self, field):
        """Check if email exists in system."""
        user = User.query.filter_by(email=field.data.lower()).first()
        if not user:
            raise ValidationError('No account found with this email address.')


class ResetPasswordForm(FlaskForm):
    """Reset password form."""
    
    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=8, max=128, message='Password must be between 8 and 128 characters'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='Password must contain at least one lowercase letter, uppercase letter, and number'
            )
        ]
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )


class ChangePasswordForm(FlaskForm):
    """Change password form for logged-in users."""
    
    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Current password is required')
        ]
    )
    
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='New password is required'),
            Length(min=8, max=128, message='Password must be between 8 and 128 characters'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='Password must contain at least one lowercase letter, uppercase letter, and number'
            )
        ]
    )
    
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your new password'),
            EqualTo('new_password', message='Passwords must match')
        ]
    )


class ProfileForm(FlaskForm):
    """User profile editing form."""
    
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(message='First name is required'),
            Length(min=2, max=50, message='Must be between 2 and 50 characters'),
            Regexp(r'^[a-zA-Z\s]+$', message='Only letters and spaces allowed')
        ]
    )
    
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(message='Last name is required'),
            Length(min=2, max=50, message='Must be between 2 and 50 characters'),
            Regexp(r'^[a-zA-Z\s]+$', message='Only letters and spaces allowed')
        ]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address'),
            Length(max=120, message='Email must be less than 120 characters')
        ]
    )
    
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(max=20, message='Phone number must be less than 20 characters'),
            Regexp(r'^[\d\s\-\+\(\)]+$', message='Invalid phone number format')
        ]
    )
    
    department = StringField(
        'Department',
        validators=[
            Optional(),
            Length(max=100, message='Department must be less than 100 characters')
        ]
    )
    
    job_title = StringField(
        'Job Title',
        validators=[
            Optional(),
            Length(max=100, message='Job title must be less than 100 characters')
        ]
    )
    
    bio = TextAreaField(
        'Bio',
        validators=[
            Optional(),
            Length(max=500, message='Bio must be less than 500 characters')
        ]
    )
    
    theme = SelectField(
        'Theme',
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark')
        ],
        default='light'
    )
    
    language = SelectField(
        'Language',
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German')
        ],
        default='en'
    )
    
    email_notifications = BooleanField(
        'Email Notifications',
        default=True
    )
    
    def __init__(self, user=None, *args, **kwargs):
        """Initialize form with user data."""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_email(self, field):
        """Check if email is already taken by another user."""
        if self.user and field.data.lower() != self.user.email.lower():
            user = User.query.filter_by(email=field.data.lower()).first()
            if user:
                raise ValidationError('Email already in use by another account.')


# TODO: Add two-factor authentication form
# TODO: Add account verification form
# TODO: Add social login integration forms