from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FloatField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Regexp, ValidationError
from datetime import datetime
import re

def validate_no_sql_injection(form, field):
    """Prevent SQL injection attempts"""
    dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC']
    for pattern in dangerous_patterns:
        if pattern.lower() in str(field.data).lower():
            raise ValidationError('Invalid characters detected')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80),
        validate_no_sql_injection
    ])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=2, max=50),
        Regexp(r'^[a-zA-Z\s\-\']+$', message='Only letters, spaces, hyphens and apostrophes allowed')
    ])
    surname = StringField('Surname', validators=[
        DataRequired(), 
        Length(min=2, max=50),
        Regexp(r'^[a-zA-Z\s\-\']+$', message='Only letters, spaces, hyphens and apostrophes allowed')
    ])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Only letters, numbers and underscores allowed'),
        validate_no_sql_injection
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), 
        Length(min=10, max=20),
        Regexp(r'^[\d\s\+\-\(\)]+$', message='Invalid phone number format')
    ])
    role = SelectField('Register As', choices=[
        ('filler', 'Operator'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=5, message='Password must be at least 5 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])

class TransactionForm(FlaskForm):
    depot_id = SelectField('Depot', coerce=int, validators=[DataRequired()])
    amount_dispensed = FloatField('Amount Dispensed (kg)', 
                                validators=[DataRequired(), NumberRange(min=0.1, max=10000)])
    price_per_kg = FloatField('Price per KG', 
                            validators=[DataRequired(), NumberRange(min=0.01, max=1000)])

class DepotForm(FlaskForm):
    name = StringField('Depot Name', validators=[
        DataRequired(), 
        Length(max=100),
        validate_no_sql_injection
    ])
    location = StringField('Location', validators=[
        DataRequired(), 
        Length(max=200),
        validate_no_sql_injection
    ])

class PurchaseForm(FlaskForm):
    amount = FloatField('Amount Purchased (kg)', 
                       validators=[DataRequired(), NumberRange(min=0.1, max=100000)])
    supplier = StringField('Supplier', validators=[
        Length(max=100),
        validate_no_sql_injection
    ])
    price_per_kg = FloatField('Price per kg ($)', validators=[NumberRange(min=0, max=10000)])
    purchase_date = DateTimeField('Purchase Date (Optional)', format='%Y-%m-%d', validators=[])
    notes = TextAreaField('Notes', validators=[Length(max=500)])

class AllocationForm(FlaskForm):
    depot_id = SelectField('Depot', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount to Allocate (kg)', 
                       validators=[DataRequired(), NumberRange(min=0.1, max=100000)])
    notes = TextAreaField('Notes', validators=[Length(max=500)])

class ProfileEditForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=2, max=50),
        Regexp(r'^[a-zA-Z\s\-\']+$', message='Only letters, spaces, hyphens and apostrophes allowed')
    ])
    surname = StringField('Surname', validators=[
        DataRequired(), 
        Length(min=2, max=50),
        Regexp(r'^[a-zA-Z\s\-\']+$', message='Only letters, spaces, hyphens and apostrophes allowed')
    ])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Only letters, numbers and underscores allowed'),
        validate_no_sql_injection
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), 
        Length(min=10, max=20),
        Regexp(r'^[\d\s\+\-\(\)]+$', message='Invalid phone number format')
    ])
    current_password = PasswordField('Current Password (required to save changes)', validators=[DataRequired()])
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[
        Length(min=8, message='Password must be at least 8 characters'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', message='Password must contain uppercase, lowercase and number')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])

class CreateManagerForm(FlaskForm):
    """Form for managers to create new manager accounts"""
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=2, max=50),
        Regexp(r'^[a-zA-Z\s\-\']+$', message='Only letters, spaces, hyphens and apostrophes allowed')
    ])
    surname = StringField('Surname', validators=[
        DataRequired(), 
        Length(min=2, max=50),
        Regexp(r'^[a-zA-Z\s\-\']+$', message='Only letters, spaces, hyphens and apostrophes allowed')
    ])
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=4, max=20),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Only letters, numbers and underscores allowed'),
        validate_no_sql_injection
    ])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), 
        Length(min=10, max=20),
        Regexp(r'^[\d\s\+\-\(\)]+$', message='Invalid phone number format')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', message='Password must contain uppercase, lowercase and number')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
