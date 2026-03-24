from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import ProfileEditForm
from extensions import db
from models import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_manager():
        return redirect(url_for('manager.dashboard'))
    else:
        return redirect(url_for('filler.dashboard'))

@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm()
    
    if request.method == 'GET':
        # Pre-populate form with current user data
        form.first_name.data = current_user.first_name
        form.surname.data = current_user.surname
        form.username.data = current_user.username
        form.phone_number.data = current_user.phone_number
    
    if form.validate_on_submit():
        try:
            # Verify current password
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect.', 'danger')
                return render_template('profile_edit.html', form=form, user=current_user)
            
            # Check if username is taken by another user
            if form.username.data != current_user.username:
                existing_user = User.query.filter_by(username=form.username.data).first()
                if existing_user:
                    flash('Username already taken.', 'danger')
                    return render_template('profile_edit.html', form=form, user=current_user)
            
            # Check if phone number is taken by another user
            if form.phone_number.data != current_user.phone_number:
                existing_phone = User.query.filter_by(phone_number=form.phone_number.data).first()
                if existing_phone:
                    flash('Phone number already registered.', 'danger')
                    return render_template('profile_edit.html', form=form, user=current_user)
            
            # Update user details
            current_user.first_name = form.first_name.data
            current_user.surname = form.surname.data
            current_user.username = form.username.data
            current_user.phone_number = form.phone_number.data
            
            # Update password if provided
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Profile edit error: {str(e)}')
    
    return render_template('profile_edit.html', form=form, user=current_user)