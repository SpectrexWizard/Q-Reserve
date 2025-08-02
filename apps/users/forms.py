"""User forms for Q-Reserve."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from apps.users.models import User


class ProfileForm(FlaskForm):
    """User profile form."""
    
    first_name = StringField('First Name', validators=[
        Length(max=50, message='First name must be less than 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    
    display_name = StringField('Display Name', validators=[
        Length(max=100, message='Display name must be less than 100 characters')
    ])
    
    bio = TextAreaField('Bio', validators=[
        Length(max=500, message='Bio must be less than 500 characters')
    ])
    
    phone = StringField('Phone', validators=[
        Length(max=20, message='Phone must be less than 20 characters')
    ])
    
    company = StringField('Company', validators=[
        Length(max=100, message='Company must be less than 100 characters')
    ])
    
    department = StringField('Department', validators=[
        Length(max=100, message='Department must be less than 100 characters')
    ])
    
    location = StringField('Location', validators=[
        Length(max=100, message='Location must be less than 100 characters')
    ])
    
    website = StringField('Website', validators=[
        Length(max=255, message='Website must be less than 255 characters')
    ])
    
    linkedin = StringField('LinkedIn', validators=[
        Length(max=255, message='LinkedIn must be less than 255 characters')
    ])
    
    twitter = StringField('Twitter', validators=[
        Length(max=255, message='Twitter must be less than 255 characters')
    ])
    
    submit = SubmitField('Update Profile')


class PreferencesForm(FlaskForm):
    """User preferences form."""
    
    theme_preference = SelectField('Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto')
    ], validators=[DataRequired()])
    
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean')
    ], validators=[DataRequired()])
    
    timezone = SelectField('Timezone', choices=[
        ('UTC', 'UTC'),
        ('America/New_York', 'Eastern Time'),
        ('America/Chicago', 'Central Time'),
        ('America/Denver', 'Mountain Time'),
        ('America/Los_Angeles', 'Pacific Time'),
        ('Europe/London', 'London'),
        ('Europe/Paris', 'Paris'),
        ('Europe/Berlin', 'Berlin'),
        ('Asia/Tokyo', 'Tokyo'),
        ('Asia/Shanghai', 'Shanghai'),
        ('Australia/Sydney', 'Sydney')
    ], validators=[DataRequired()])
    
    email_notifications = BooleanField('Email Notifications')
    in_app_notifications = BooleanField('In-App Notifications')
    weekly_digest = BooleanField('Weekly Digest')
    
    submit = SubmitField('Update Preferences')


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    
    current_password = StringField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = StringField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = StringField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    submit = SubmitField('Change Password')


class AdminUserForm(FlaskForm):
    """Admin user management form."""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
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
    
    role = SelectField('Role', choices=[
        ('end_user', 'End User'),
        ('agent', 'Support Agent'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    
    is_active = BooleanField('Active')
    is_verified = BooleanField('Verified')
    
    submit = SubmitField('Update User')