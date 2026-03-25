from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Transaction, Depot, Purchase, DepotAllocation, User
from forms import DepotForm, PurchaseForm, AllocationForm
from extensions import db
from functools import wraps
from sqlalchemy import func
from config import Config
from datetime import datetime

manager_bp = Blueprint('manager', __name__)

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_active_user():
            flash('Your account is not active. Please contact an administrator.', 'danger')
            return redirect(url_for('auth.logout'))
        if not current_user.is_manager():
            flash('Access denied. Manager role required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@manager_bp.route('/dashboard')
@login_required
@manager_required
def dashboard():
    # Get inventory summary
    depots = Depot.query.all()
    low_inventory_depots = [d for d in depots if d.current_inventory < Config.LOW_INVENTORY_THRESHOLD]
    
    # Get pending users count
    pending_users_count = User.query.filter_by(status='pending').count()
    
    # Get total purchases and allocations
    total_purchased = db.session.query(func.sum(Purchase.amount)).scalar() or 0
    total_allocated = db.session.query(func.sum(DepotAllocation.amount)).scalar() or 0
    total_dispensed = db.session.query(func.sum(Transaction.amount_dispensed)).scalar() or 0
    
    # Calculate current total inventory across all depots
    total_current_inventory = db.session.query(func.sum(Depot.current_inventory)).scalar() or 0
    
    # Calculate unallocated inventory (purchased but not yet allocated to depots)
    unallocated_inventory = total_purchased - total_allocated
    
    # Recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(10).all()
    
    return render_template('manager/dashboard.html', 
                         depots=depots,
                         low_inventory_depots=low_inventory_depots,
                         pending_users_count=pending_users_count,
                         total_purchased=total_purchased,
                         total_allocated=total_allocated,
                         total_dispensed=total_dispensed,
                         total_current_inventory=total_current_inventory,
                         unallocated_inventory=unallocated_inventory,
                         recent_transactions=recent_transactions)

@manager_bp.route('/daily_sales')
@login_required
@manager_required
def daily_sales():
    from datetime import datetime, timedelta
    
    # Get date filter parameter
    filter_date = request.args.get('date')
    
    # Get all sales transactions with depot information
    query = db.session.query(
        Transaction.id,
        Depot.name.label('depot_name'),
        Transaction.transaction_date,
        Transaction.amount_dispensed,
        Transaction.price_per_kg,
        Transaction.total_amount,
        User.first_name,
        User.surname
    ).join(Depot, Transaction.depot_id == Depot.id
    ).join(User, Transaction.filler_id == User.id)
    
    # Apply date filter if provided
    if filter_date:
        try:
            filter_dt = datetime.strptime(filter_date, '%Y-%m-%d')
            next_day = filter_dt + timedelta(days=1)
            query = query.filter(
                Transaction.transaction_date >= filter_dt,
                Transaction.transaction_date < next_day
            )
        except ValueError:
            pass
    
    # Order by most recent first
    sales_data = query.order_by(Transaction.transaction_date.desc()).all()
    
    # Format the data with full name
    all_sales = []
    for sale in sales_data:
        all_sales.append({
            'id': sale.id,
            'depot_name': sale.depot_name,
            'transaction_date': sale.transaction_date,
            'amount_dispensed': sale.amount_dispensed,
            'price_per_kg': sale.price_per_kg,
            'total_amount': sale.total_amount,
            'operator_name': f"{sale.first_name} {sale.surname}"
        })
    
    return render_template('manager/daily_sales.html',
                         all_sales=all_sales,
                         filter_date=filter_date)

@manager_bp.route('/depots')
@login_required
@manager_required
def depots():
    depots = Depot.query.all()
    return render_template('manager/depots.html', depots=depots)

@manager_bp.route('/add_depot', methods=['GET', 'POST'])
@login_required
@manager_required
def add_depot():
    form = DepotForm()
    if form.validate_on_submit():
        try:
            depot = Depot(name=form.name.data, location=form.location.data)
            db.session.add(depot)
            db.session.commit()
            flash('Depot added successfully! You can add another or go back.', 'success')
            # Clear form for next entry
            form.name.data = ''
            form.location.data = ''
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the depot. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Add depot error: {str(e)}')
    return render_template('manager/add_depot.html', form=form)

@manager_bp.route('/purchases')
@login_required
@manager_required
def purchases():
    all_purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return render_template('manager/purchases_test.html', purchases=all_purchases)

@manager_bp.route('/add_purchase', methods=['GET', 'POST'])
@login_required
@manager_required
def add_purchase():
    form = PurchaseForm()
    if form.validate_on_submit():
        try:
            # Get cost from request (calculated by JavaScript)
            cost = request.form.get('cost')
            
            # Use provided date or default to current datetime
            purchase_date = form.purchase_date.data if form.purchase_date.data else datetime.now()
            
            purchase = Purchase(
                amount=form.amount.data,
                supplier=form.supplier.data,
                price_per_kg=form.price_per_kg.data,
                cost=float(cost) if cost else None,
                purchase_date=purchase_date,
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(purchase)
            db.session.commit()
            flash('Purchase recorded successfully! You can add another or go back.', 'success')
            # Clear form for next entry
            form.amount.data = None
            form.supplier.data = ''
            form.price_per_kg.data = None
            form.purchase_date.data = None
            form.notes.data = ''
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while recording the purchase. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Add purchase error: {str(e)}')
    return render_template('manager/add_purchase.html', form=form)

@manager_bp.route('/allocations')
@login_required
@manager_required
def allocations():
    allocations = DepotAllocation.query.order_by(DepotAllocation.allocation_date.desc()).all()
    return render_template('manager/allocations.html', allocations=allocations)

@manager_bp.route('/add_allocation', methods=['GET', 'POST'])
@login_required
@manager_required
def add_allocation():
    form = AllocationForm()
    # Exclude "Main Depot" or "Main Location" from allocation choices
    form.depot_id.choices = [(d.id, f"{d.name} - {d.location}") 
                             for d in Depot.query.all() 
                             if d.name.lower() not in ['main depot', 'main location']]
    
    # Calculate unallocated inventory for display
    total_purchased = db.session.query(func.sum(Purchase.amount)).scalar() or 0
    total_allocated = db.session.query(func.sum(DepotAllocation.amount)).scalar() or 0
    unallocated = total_purchased - total_allocated
    
    if form.validate_on_submit():
        try:
            # Check if there's enough unallocated inventory
            if form.amount.data > unallocated:
                flash(f'Insufficient unallocated inventory! Available: {unallocated:.2f} kg, Requested: {form.amount.data:.2f} kg', 'danger')
                return render_template('manager/add_allocation.html', form=form, unallocated=unallocated)
            
            depot = Depot.query.get(form.depot_id.data)
            allocation = DepotAllocation(
                depot_id=form.depot_id.data,
                amount=form.amount.data,
                allocated_by=current_user.id,
                notes=form.notes.data
            )
            
            # Update depot inventory
            depot.current_inventory += form.amount.data
            
            db.session.add(allocation)
            db.session.commit()
            
            # Recalculate unallocated after successful allocation
            total_allocated = db.session.query(func.sum(DepotAllocation.amount)).scalar() or 0
            unallocated = total_purchased - total_allocated
            
            flash(f'Allocation completed successfully! {form.amount.data:.2f} kg allocated to {depot.name}.', 'success')
            # Clear form for next entry
            form.amount.data = None
            form.notes.data = ''
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing the allocation. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Add allocation error: {str(e)}')
    
    return render_template('manager/add_allocation.html', form=form, unallocated=unallocated)

@manager_bp.route('/reports')
@login_required
@manager_required
def reports():
    # Get month and year from query params, default to current month
    month = request.args.get('month', type=int, default=datetime.now().month)
    year = request.args.get('year', type=int, default=datetime.now().year)
    
    # Calculate start and end dates for the month
    from calendar import monthrange
    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    # Generate comprehensive reports
    depot_summary = []
    total_revenue_all = 0
    
    for depot in Depot.query.all():
        # Get allocations BEFORE the selected month (for Balance B/F calculation)
        total_allocated_before = db.session.query(func.sum(DepotAllocation.amount))\
                                   .filter(DepotAllocation.depot_id == depot.id)\
                                   .filter(DepotAllocation.allocation_date < start_date)\
                                   .scalar() or 0
        
        # Get transactions BEFORE the selected month (for Balance B/F calculation)
        total_dispensed_before = db.session.query(func.sum(Transaction.amount_dispensed))\
                                   .filter(Transaction.depot_id == depot.id)\
                                   .filter(Transaction.transaction_date < start_date)\
                                   .scalar() or 0
        
        # Calculate Balance Brought Forward (what was in depot at start of month)
        balance_bf = total_allocated_before - total_dispensed_before
        
        # Filter allocations by month (for current month activities)
        total_allocated = db.session.query(func.sum(DepotAllocation.amount))\
                                   .filter(DepotAllocation.depot_id == depot.id)\
                                   .filter(DepotAllocation.allocation_date >= start_date)\
                                   .filter(DepotAllocation.allocation_date <= end_date)\
                                   .scalar() or 0
        
        # Filter transactions by month and get monetary values (for current month activities)
        transactions_query = db.session.query(
            func.sum(Transaction.amount_dispensed),
            func.sum(Transaction.total_amount),
            func.count(Transaction.id)
        ).filter(Transaction.depot_id == depot.id)\
         .filter(Transaction.transaction_date >= start_date)\
         .filter(Transaction.transaction_date <= end_date)\
         .first()
        
        total_dispensed = transactions_query[0] or 0
        total_revenue = transactions_query[1] or 0
        transaction_count = transactions_query[2] or 0
        
        total_revenue_all += total_revenue
        
        depot_summary.append({
            'depot': depot,
            'balance_bf': balance_bf,
            'total_allocated': total_allocated,
            'total_dispensed': total_dispensed,
            'total_revenue': total_revenue,
            'transaction_count': transaction_count,
            'current_inventory': depot.current_inventory
        })
    
    # Get month name
    month_name = start_date.strftime('%B %Y')
    
    return render_template('manager/reports.html', 
                         depot_summary=depot_summary,
                         month_name=month_name,
                         current_month=month,
                         current_year=year,
                         total_revenue_all=total_revenue_all)
@manager_bp.route('/users')
@login_required
@manager_required
def users():
    pending_users = User.query.filter_by(status='pending').all()
    active_users = User.query.filter_by(status='active').all()
    inactive_users = User.query.filter_by(status='inactive').all()
    
    pending_users_count = len(pending_users)
    
    return render_template('manager/users.html', 
                         pending_users=pending_users,
                         active_users=active_users,
                         inactive_users=inactive_users,
                         pending_users_count=pending_users_count)

@manager_bp.route('/approve_user/<int:user_id>')
@login_required
@manager_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.status == 'pending':
        user.approve_user(current_user.id)
        db.session.commit()
        flash(f'User {user.username} has been approved and activated. You can now assign them to a depot.', 'success')
    else:
        flash('User is not in pending status.', 'warning')
    
    return redirect(url_for('manager.users'))

@manager_bp.route('/search_fillers')
@login_required
@manager_required
def search_fillers():
    """API endpoint for live search of fillers"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return {'results': []}
    
    # Search for fillers matching the query
    fillers = User.query.filter(
        User.role == 'filler',
        db.or_(
            User.username.ilike(f'%{query}%'),
            User.full_name.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = [{
        'id': filler.id,
        'username': filler.username,
        'full_name': filler.full_name,
        'phone_number': filler.phone_number,
        'status': filler.status,
        'assigned_depot': filler.assigned_depot.name if filler.assigned_depot else None
    } for filler in fillers]
    
    return {'results': results}

@manager_bp.route('/assign_depot', methods=['GET', 'POST'])
@manager_bp.route('/assign_depot/<int:user_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def assign_depot(user_id=None):
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Handle assignment submission
    if request.method == 'POST' and user_id:
        user = User.query.get_or_404(user_id)
        
        if user.role != 'filler':
            flash('Only fillers can be assigned to depots.', 'warning')
            return redirect(url_for('manager.assign_depot'))
        
        depot_id = request.form.get('depot_id')
        if depot_id:
            depot = Depot.query.get(int(depot_id))
            user.assigned_depot_id = int(depot_id)
            db.session.commit()
            flash(f'Filler {user.username} has been assigned to {depot.name}.', 'success')
        else:
            user.assigned_depot_id = None
            db.session.commit()
            flash(f'Depot assignment removed for {user.username}.', 'info')
        return redirect(url_for('manager.assign_depot'))
    
    # Get depots
    depots = Depot.query.all()
    
    if not depots:
        flash('No depots available. Please create a depot first.', 'warning')
        return redirect(url_for('manager.users'))
    
    # If user_id is provided, show that user
    if user_id:
        user = User.query.get_or_404(user_id)
        if user.role != 'filler':
            flash('Only fillers can be assigned to depots.', 'warning')
            return redirect(url_for('manager.assign_depot'))
        
        if user.status != 'active':
            flash(f'Note: User {user.username} is not yet active. You can assign a depot now, but they won\'t be able to access it until approved.', 'info')
        
        return render_template('manager/assign_depot.html', user=user, depots=depots, search_query='')
    
    # Search functionality
    user = None
    if search_query:
        # Search by username or full name (case insensitive)
        user = User.query.filter(
            User.role == 'filler',
            db.or_(
                User.username.ilike(f'%{search_query}%'),
                User.full_name.ilike(f'%{search_query}%')
            )
        ).first()
        
        if not user:
            flash(f'No filler found matching "{search_query}". Please try another search.', 'warning')
    
    return render_template('manager/assign_depot.html', user=user, depots=depots, search_query=search_query)

@manager_bp.route('/deactivate_user/<int:user_id>')
@login_required
@manager_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
    elif user.status == 'active':
        user.status = 'inactive'
        db.session.commit()
        flash(f'User {user.username} has been deactivated.', 'success')
    else:
        flash('User is not in active status.', 'warning')
    
    return redirect(url_for('manager.users'))

@manager_bp.route('/activate_user/<int:user_id>')
@login_required
@manager_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.status == 'inactive':
        user.status = 'active'
        user.approved_at = datetime.utcnow()
        user.approved_by = current_user.id
        db.session.commit()
        flash(f'User {user.username} has been reactivated.', 'success')
    else:
        flash('User is not in inactive status.', 'warning')
    
    return redirect(url_for('manager.users'))

@manager_bp.route('/delete_user/<int:user_id>')
@login_required
@manager_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
    else:
        # Check if user has any transactions
        transaction_count = Transaction.query.filter_by(filler_id=user.id).count()
        if transaction_count > 0:
            flash(f'Cannot delete user {user.username}. User has {transaction_count} transactions in the system.', 'danger')
        else:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            flash(f'User {username} has been deleted.', 'success')
    
    return redirect(url_for('manager.users'))


@manager_bp.route('/create_manager', methods=['GET', 'POST'])
@login_required
@manager_required
def create_manager():
    """Allow managers to create new manager accounts"""
    from forms import CreateManagerForm
    
    form = CreateManagerForm()
    
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
                return render_template('manager/create_manager.html', form=form)
            
            # Create new manager account
            user = User(
                username=form.username.data,
                first_name=form.first_name.data,
                surname=form.surname.data,
                phone_number=form.phone_number.data,
                role='manager',
                status='active'  # Manager accounts are automatically activated
            )
            user.set_password(form.password.data)
            user.approved_by = current_user.id
            user.approved_at = datetime.utcnow()
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Manager account created successfully for {user.username}!', 'success')
            return redirect(url_for('manager.users'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the manager account. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Create manager error: {str(e)}')
    
    return render_template('manager/create_manager.html', form=form)
