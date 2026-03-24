from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Transaction, Depot, Purchase, DepotAllocation, User
from extensions import db
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

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

@reports_bp.route('/balance_sheet')
@login_required
@manager_required
def balance_sheet():
    """Generate comprehensive balance sheet with running balance"""
    
    # Get month and year from query params, default to current month
    from datetime import datetime
    month = request.args.get('month', type=int, default=datetime.now().month)
    year = request.args.get('year', type=int, default=datetime.now().year)
    
    # Calculate start and end dates for the month
    from calendar import monthrange
    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    # Calculate Balance Brought Forward (from all transactions before this month)
    purchases_before = db.session.query(func.sum(Purchase.amount)).filter(
        Purchase.purchase_date < start_date
    ).scalar() or 0
    
    dispensed_before = db.session.query(func.sum(Transaction.amount_dispensed)).filter(
        Transaction.transaction_date < start_date
    ).scalar() or 0
    
    balance_bf = purchases_before - dispensed_before
    
    # Collect all transactions with their types
    all_entries = []
    
    # Add Balance B/F as first entry if there's a balance
    if balance_bf != 0:
        all_entries.append({
            'date': start_date,
            'type': 'BALANCE_BF',
            'description': 'Balance Brought Forward',
            'reference': 'BAL-BF',
            'in': balance_bf if balance_bf > 0 else 0,
            'out': abs(balance_bf) if balance_bf < 0 else 0,
            'cost': 0,
            'revenue': 0,
            'depot': 'Opening Balance',
            'notes': 'Carried forward from previous period'
        })
    
    # 1. Purchases (increases inventory) - filter by month
    purchases = Purchase.query.filter(
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date
    ).order_by(Purchase.purchase_date).all()
    
    for p in purchases:
        all_entries.append({
            'date': p.purchase_date,
            'type': 'PURCHASE',
            'description': f'Purchase from {p.supplier or "Supplier"}',
            'reference': f'PUR-{p.id}',
            'in': p.amount,
            'out': 0,
            'cost': p.cost or 0,
            'revenue': 0,
            'depot': 'Central Storage',
            'notes': p.notes
        })
    
    # 2. Dispensing transactions (decreases inventory) - filter by month
    transactions = Transaction.query.filter(
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).order_by(Transaction.transaction_date).all()
    
    for t in transactions:
        all_entries.append({
            'date': t.transaction_date,
            'type': 'DISPENSED',
            'description': f'Dispensed by {t.filler.full_name}',
            'reference': f'TRANS-{t.id}',
            'in': 0,
            'out': t.amount_dispensed,
            'cost': 0,
            'revenue': t.total_amount,
            'depot': t.depot.name,
            'notes': t.notes or ''
        })
    
    # Sort all entries by date
    all_entries.sort(key=lambda x: x['date'])
    
    # Calculate running balance and monetary totals
    running_balance = 0
    total_cost = 0
    total_revenue = 0
    
    for entry in all_entries:
        running_balance += entry['in']
        running_balance -= entry['out']
        entry['balance'] = running_balance
        
        total_cost += entry['cost']
        total_revenue += entry['revenue']
    
    # Calculate profit
    profit = total_revenue - total_cost
    
    # Get month name
    month_name = start_date.strftime('%B %Y')
    
    return render_template('reports/balance_sheet.html',
                         all_entries=all_entries,
                         month_name=month_name,
                         current_month=month,
                         current_year=year,
                         total_cost=total_cost,
                         total_revenue=total_revenue,
                         profit=profit,
                         balance_bf=balance_bf,
                         datetime=datetime)
