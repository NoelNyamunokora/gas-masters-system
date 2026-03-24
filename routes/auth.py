from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from forms import LoginForm, RegistrationForm
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                if user.status == 'pending':
                    flash('Your account is pending approval. Please contact an administrator.', 'warning')
                    return redirect(url_for('auth.login'))
                elif user.status == 'inactive':
                    flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                    return redirect(url_for('auth.login'))
                elif user.status == 'active':
                    login_user(user)
                    next_page = request.args.get('next')
                    if not next_page:
                        if user.is_manager():
                            next_page = url_for('manager.dashboard')
                        else:
                            next_page = url_for('filler.dashboard')
                    return redirect(next_page)
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Login error: {str(e)}')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if username or phone number already exists
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.phone_number == form.phone_number.data)
            ).first()
            
            if existing_user:
                if existing_user.username == form.username.data:
                    flash('Username already exists. Please choose a different one.', 'danger')
                else:
                    flash('Phone number already registered. Please use a different number.', 'danger')
                return redirect(url_for('auth.register'))
            
            user = User(
                username=form.username.data,
                first_name=form.first_name.data,
                surname=form.surname.data,
                phone_number=form.phone_number.data,
                role=form.role.data,  # Use the selected role from the form
                status='pending'  # All new accounts start as pending
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Your account is pending approval by an administrator.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Registration error: {str(e)}')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    response = redirect(url_for('auth.login'))
    # Prevent caching to stop back button access
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    flash('You have been logged out successfully.', 'success')
    return response