from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='filler')  # 'filler' or 'manager'
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'active', 'inactive'
    assigned_depot_id = db.Column(db.Integer, db.ForeignKey('depots.id'), nullable=True)  # Depot assignment for fillers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    assigned_depot = db.relationship('Depot', foreign_keys=[assigned_depot_id], backref='assigned_fillers')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.surname}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_filler(self):
        return self.role == 'filler'
    
    def is_active_user(self):
        return self.status == 'active'
    
    def is_pending(self):
        return self.status == 'pending'
    
    def approve_user(self, approved_by_user_id):
        self.status = 'active'
        self.approved_at = datetime.utcnow()
        self.approved_by = approved_by_user_id

class Depot(db.Model):
    __tablename__ = 'depots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    current_inventory = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='depot', lazy=True)
    allocations = db.relationship('DepotAllocation', backref='depot', lazy=True)
class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    supplier = db.Column(db.String(100))
    price_per_kg = db.Column(db.Float)
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class DepotAllocation(db.Model):
    __tablename__ = 'depot_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    depot_id = db.Column(db.Integer, db.ForeignKey('depots.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    allocation_date = db.Column(db.DateTime, default=datetime.utcnow)
    allocated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    depot_id = db.Column(db.Integer, db.ForeignKey('depots.id'), nullable=False)
    filler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount_dispensed = db.Column(db.Float, nullable=False)  # in kilograms
    price_per_kg = db.Column(db.Float, nullable=False, default=0.0)  # price per kilogram
    total_amount = db.Column(db.Float, nullable=False, default=0.0)  # total amount (price_per_kg * amount_dispensed)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    filler = db.relationship('User', backref='transactions')