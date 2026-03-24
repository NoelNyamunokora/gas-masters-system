from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Transaction, Depot
from forms import TransactionForm
from extensions import db
from functools import wraps

filler_bp = Blueprint('filler', __name__)

def filler_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_active_user():
            flash('Your account is not active. Please contact an administrator.', 'danger')
            return redirect(url_for('auth.logout'))
        if not current_user.is_filler():
            flash('Access denied. Filler role required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@filler_bp.route('/dashboard')
@login_required
@filler_required
def dashboard():
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Check if filler has been assigned to a depot
    if not current_user.assigned_depot_id:
        return render_template('filler/no_depot_assigned.html')
    
    # Get only the assigned depot
    depot = Depot.query.get(current_user.assigned_depot_id)
    
    # Calculate today's stats
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_transactions = Transaction.query.filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id,
        Transaction.transaction_date >= today_start
    ).all()
    
    today_transactions_count = len(today_transactions)
    today_dispensed = sum(t.amount_dispensed for t in today_transactions)
    
    # Get total transactions count
    total_transactions = Transaction.query.filter_by(
        filler_id=current_user.id,
        depot_id=current_user.assigned_depot_id
    ).count()
    
    # Calculate week start (Monday)
    week_start = today_start - timedelta(days=today_start.weekday())
    
    # This week's sales
    week_transactions = Transaction.query.filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id,
        Transaction.transaction_date >= week_start
    ).all()
    week_sales = sum(t.total_amount for t in week_transactions)
    week_quantity = sum(t.amount_dispensed for t in week_transactions)
    
    # This month's sales
    month_start = today_start.replace(day=1)
    month_transactions = Transaction.query.filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id,
        Transaction.transaction_date >= month_start
    ).all()
    month_sales = sum(t.total_amount for t in month_transactions)
    month_quantity = sum(t.amount_dispensed for t in month_transactions)
    
    # Average transactions per day (last 30 days)
    thirty_days_ago = today_start - timedelta(days=30)
    last_30_days_count = Transaction.query.filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id,
        Transaction.transaction_date >= thirty_days_ago
    ).count()
    avg_transactions_per_day = last_30_days_count / 30 if last_30_days_count > 0 else 0
    
    # Best selling day this week
    week_daily_sales = db.session.query(
        func.date(Transaction.transaction_date).label('date'),
        func.sum(Transaction.total_amount).label('total_amount')
    ).filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id,
        Transaction.transaction_date >= week_start
    ).group_by(
        func.date(Transaction.transaction_date)
    ).order_by(
        func.sum(Transaction.total_amount).desc()
    ).first()
    
    best_day_week = None
    best_day_week_amount = 0
    if week_daily_sales:
        best_day_week = week_daily_sales.date.strftime('%A, %b %d')
        best_day_week_amount = week_daily_sales.total_amount
    
    # Best selling day this month
    month_daily_sales = db.session.query(
        func.date(Transaction.transaction_date).label('date'),
        func.sum(Transaction.total_amount).label('total_amount')
    ).filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id,
        Transaction.transaction_date >= month_start
    ).group_by(
        func.date(Transaction.transaction_date)
    ).order_by(
        func.sum(Transaction.total_amount).desc()
    ).first()
    
    best_day_month = None
    best_day_month_amount = 0
    if month_daily_sales:
        best_day_month = month_daily_sales.date.strftime('%A, %b %d')
        best_day_month_amount = month_daily_sales.total_amount
    
    return render_template('filler/dashboard.html', 
                         depot=depot,
                         today_transactions_count=today_transactions_count,
                         today_dispensed=today_dispensed,
                         total_transactions=total_transactions,
                         week_sales=week_sales,
                         week_quantity=week_quantity,
                         month_sales=month_sales,
                         month_quantity=month_quantity,
                         avg_transactions_per_day=avg_transactions_per_day,
                         best_day_week=best_day_week,
                         best_day_week_amount=best_day_week_amount,
                         best_day_month=best_day_month,
                         best_day_month_amount=best_day_month_amount)

@filler_bp.route('/add_transaction', methods=['GET', 'POST'])
@login_required
@filler_required
def add_transaction():
    # Check if filler has been assigned to a depot
    if not current_user.assigned_depot_id:
        flash('You have not been assigned to a depot yet. Please contact your manager.', 'warning')
        return redirect(url_for('filler.dashboard'))
    
    form = TransactionForm()
    # Only show the assigned depot
    depot = Depot.query.get(current_user.assigned_depot_id)
    form.depot_id.choices = [(depot.id, f"{depot.name} - {depot.location}")]
    
    if form.validate_on_submit():
        try:
            # Verify the depot matches assigned depot
            if form.depot_id.data != current_user.assigned_depot_id:
                flash('You can only record transactions for your assigned depot.', 'danger')
                return render_template('filler/add_transaction.html', form=form, depot=depot)
            
            if depot.current_inventory < form.amount_dispensed.data:
                flash(f'Insufficient inventory at depot! Available: {depot.current_inventory:.2f} kg', 'danger')
                return render_template('filler/add_transaction.html', form=form, depot=depot)
            
            total_amount = form.amount_dispensed.data * form.price_per_kg.data
            
            transaction = Transaction(
                depot_id=form.depot_id.data,
                filler_id=current_user.id,
                amount_dispensed=form.amount_dispensed.data,
                price_per_kg=form.price_per_kg.data,
                total_amount=total_amount
            )
            
            # Update depot inventory
            depot.current_inventory -= form.amount_dispensed.data
            
            db.session.add(transaction)
            db.session.commit()
            flash(f'Transaction recorded successfully! {form.amount_dispensed.data:.2f} kg dispensed. Total: ${total_amount:.2f}', 'success')
            # Clear form for next entry
            form.amount_dispensed.data = None
            form.price_per_kg.data = None
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while recording the transaction. Please try again.', 'danger')
            from flask import current_app
            current_app.logger.error(f'Add transaction error: {str(e)}')
    
    return render_template('filler/add_transaction.html', form=form, depot=depot)


@filler_bp.route('/transaction_history')
@login_required
@filler_required
def transaction_history():
    # Check if filler has been assigned to a depot
    if not current_user.assigned_depot_id:
        return render_template('filler/no_depot_assigned.html')
    
    # Get all transactions from the assigned depot by this filler
    transactions = Transaction.query.filter_by(
        filler_id=current_user.id,
        depot_id=current_user.assigned_depot_id
    ).order_by(Transaction.transaction_date.desc()).all()
    
    # Get the assigned depot
    depot = Depot.query.get(current_user.assigned_depot_id)
    
    # Calculate total dispensed
    total_dispensed = sum(t.amount_dispensed for t in transactions)
    
    return render_template('filler/transaction_history.html', 
                         transactions=transactions,
                         depot=depot,
                         total_dispensed=total_dispensed)


@filler_bp.route('/total_sales')
@login_required
@filler_required
def total_sales():
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from flask import request
    
    # Check if filler has been assigned to a depot
    if not current_user.assigned_depot_id:
        return render_template('filler/no_depot_assigned.html')
    
    # Get the assigned depot
    depot = Depot.query.get(current_user.assigned_depot_id)
    
    # Get filter parameter
    filter_date = request.args.get('date')
    
    # Build query
    query = db.session.query(
        func.date(Transaction.transaction_date).label('date'),
        func.count(Transaction.id).label('transaction_count'),
        func.sum(Transaction.amount_dispensed).label('total_quantity'),
        func.avg(Transaction.price_per_kg).label('avg_price_per_kg'),
        func.sum(Transaction.total_amount).label('total_amount')
    ).filter(
        Transaction.filler_id == current_user.id,
        Transaction.depot_id == current_user.assigned_depot_id
    )
    
    # Apply date filter if provided
    if filter_date:
        try:
            filter_dt = datetime.strptime(filter_date, '%Y-%m-%d')
            # Filter for the specific date only
            next_day = filter_dt + timedelta(days=1)
            query = query.filter(
                Transaction.transaction_date >= filter_dt,
                Transaction.transaction_date < next_day
            )
        except ValueError:
            pass
    
    # Get daily sales summary grouped by date
    daily_sales = query.group_by(
        func.date(Transaction.transaction_date)
    ).order_by(
        func.date(Transaction.transaction_date).desc()
    ).all()
    
    return render_template('filler/total_sales.html',
                         depot=depot,
                         daily_sales=daily_sales,
                         filter_date=filter_date)

